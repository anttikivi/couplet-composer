# Copyright (c) 2020 Antti Kivi
# Licensed under the MIT License

"""A module that contains the class that represents an invocation
of the build script.
"""

import logging
import os
import platform

from collections import namedtuple

from .support.run_mode import RunMode

from .support.system import System

from .args_parser import create_args_parser

from .composing_runner import ComposingRunner

from .configuring_runner import ConfiguringRunner

from .preset_runner import PresetRunner

from .project import Project

from .target import Target


class Invocation:
    """A class for creating callable objects that represent
    invocations of the build script.

    Attributes:
        args (Namespace): A namespace that contains the parsed
            command line arguments.
        run_mode (RunMode): The run mode selected for the
            invocation instance.
        version (str): The version of the build script.
        name (str): The name of the build script.
        source_root (str): The root directory in which the
            project and the build files are.
        project (Project): The project object for the project
            this build script acts on.
        repository (str): The name of the repository directory of
            the project that is being built.
        platform (System): The platform that the build script is
            invoked on.
        targets (Targets): A named tuple of targets that contains
            the host target and other possible cross compile
            targets.
        runner (Runner): The runner for the run mode of the
            invocation.
    """

    Targets = namedtuple("Targets", ["host", "cross_compile"])

    def __init__(self, version: str, name: str) -> None:
        """Initializes the invocation object for the current run.

        Args:
            version (str): The version of the build script.
            name (str): The name of the build script.
        """
        self.args = create_args_parser().parse_args()
        self.run_mode = RunMode(self.args.run_mode)
        self.version = version
        self.name = name
        self.source_root = os.getcwd()

        # The logger must be initialized first.
        self._set_logging_level()

        logging.info("Running %s version %s", self.name, self.version)

        self.project = Project(
            source_root=self.source_root,
            repo=self.args.repository,
            script_package="couplet_composer"  # TODO Remove hard-coded value
        )
        self.repository = self.args.repository
        self.platform = System(platform.system().lower())
        self.targets = self._resolve_targets()

        def _resolve_runner_type():
            if self.run_mode is RunMode.preset:
                return PresetRunner(invocation=self)
            elif self.run_mode is RunMode.configure:
                return ConfiguringRunner(invocation=self)
            elif self.run_mode is RunMode.compose:
                return ComposingRunner(invocation=self)
            else:
                raise ValueError

        self.runner = _resolve_runner_type()

    def __call__(self) -> int:
        """Invokes the build script with the current
        configuration.

        Returns:
            An 'int' that is equal to the exit code of the
            invocation.
        """
        return self.runner()

    def _set_logging_level(self) -> None:
        """Sets the logging level according to the configuration
        of the current run.

        This function isn't pure and doesn't return anything.
        """
        log_format = "%(message)s"

        if self.args.verbose:
            logging.basicConfig(format=log_format, level=logging.DEBUG)
        else:
            logging.basicConfig(format=log_format, level=logging.INFO)

    def _resolve_targets(self) -> namedtuple:
        """Resolves the target platforms for the build.

        Returns:
            A dictionary that contains the host target and the
            cross compile targets.
        """
        host_target = Target.resolve_host_target() \
            if self.run_mode is RunMode.preset \
            else Target.to_target(self.args.host_target)

        return self.Targets(host=host_target, cross_compile=list())