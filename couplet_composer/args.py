# ------------------------------------------------------------- #
#                       Couplet Composer
# ------------------------------------------------------------- #
#
# This source file is part of the Couplet Composer project which
# is part of the Obliging Ode and Unsung Anthem project.
#
# Copyright (c) 2019 Antti Kivi
# Licensed under the MIT License
#
# ------------------------------------------------------------- #

"""This module defines the argument parser for the project."""

import argparse
import multiprocessing

from .support.build_variant import \
    get_build_variant_names, get_debug_variant_name, \
    get_minimum_size_release_variant_name, get_release_variant_name, \
    get_release_with_debuginfo_variant_name

from .support.cmake_generators import \
    get_cmake_generator_names, get_make_cmake_generator_name, \
    get_ninja_cmake_generator_name

from .support.compiler_toolchains import \
    get_gcc_toolchain_name, get_clang_toolchain_name, \
    get_compiler_toolchain_names

from .support.project_libraries import \
    get_all_project_library_names, get_anthem_shared_name, \
    get_anthem_static_name, get_ode_shared_name, get_ode_static_name

from .support.project_values import \
    get_anthem_binaries_base_name, get_anthem_name, get_anthem_version, \
    get_default_anthem_logger_name, get_default_ode_logger_name, \
    get_default_anthem_window_name, get_default_ode_window_name, \
    get_ode_binaries_base_name, get_ode_name, get_ode_version, \
    get_opengl_version

from .util.cache import cached

from .util.target import resolve_host_target


def _add_common_arguments(parser):
    """
    Adds the options common to all parsers to the given parser.
    This function isn't pure as it modifies the given parser.
    Returns the parser that contains the added arguments.

    parser -- The parser to which the arguments are added.
    """
    # --------------------------------------------------------- #
    # Top-level options

    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="don't actually run any commands; just print them"
    )
    parser.add_argument(
        "-j",
        "--jobs",
        default=multiprocessing.cpu_count(),
        type=int,
        help="specify the number of parallel build jobs to use"
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="clean up the build environment before build"
    )
    parser.add_argument(
        "--print-debug",
        action="store_true",
        help="print the debug-level logging output"
    )

    # --------------------------------------------------------- #
    # GitHub options

    github_group = parser.add_argument_group("GitHub options")

    github_group.add_argument(
        "--github-user-agent",
        default=None,
        help="set the user agent used when accessing the GitHub API "
             "(default: {})".format(None)
    )
    github_group.add_argument(
        "--github-api-token",
        default=None,
        help="set the API token used when accessing the GitHub API "
             "(default: {})".format(None)
    )

    return parser


def _add_common_build_arguments(parser, source_root):
    """
    Adds the options common to configure and compose parsers to
    the given parser. This function isn't pure as it modifies the
    given parser. Returns the parser that contains the added
    arguments.

    parser -- The parser to which the arguments are added.

    source_root -- Path to the directory that is the root of the
    script run.
    """
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="build the tests",
        dest="build_test"
    )

    # --------------------------------------------------------- #
    # Build variant options

    variant_group = parser.add_argument_group("Build variant options")

    variant_selection_group = variant_group.add_mutually_exclusive_group(
        required=False
    )

    default_build_variant = get_debug_variant_name()

    parser.set_defaults(build_variant=default_build_variant)

    variant_selection_group.add_argument(
        "--build-variant",
        default=default_build_variant,
        choices=get_compiler_toolchain_names(),
        help="use the selected build variant (default: {})".format(
            default_build_variant
        ),
        dest="build_variant"
    )
    variant_selection_group.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=get_debug_variant_name(),
        help="build the project using the Debug variant",
        dest="build_variant"
    )
    variant_selection_group.add_argument(
        "-r",
        "--release-debuginfo",
        action="store_const",
        const=get_release_with_debuginfo_variant_name(),
        help="build the project using the RelWithDebInfo variant",
        dest="build_variant"
    )
    variant_selection_group.add_argument(
        "-R",
        "--release",
        action="store_const",
        const=get_release_variant_name(),
        help="build the project using the Release variant",
        dest="build_variant"
    )
    variant_selection_group.add_argument(
        "-M",
        "--minsize-release",
        action="store_const",
        const=get_minimum_size_release_variant_name(),
        help="build the project using the MinSizeRel variant",
        dest="build_variant"
    )

    # --------------------------------------------------------- #
    # TODO Build target options

    target_group = parser.add_argument_group(
        "Build target options",
        "Please note that these option don't have any actual effect on the "
        "built binaries yet"
    )

    target_group.add_argument(
        "--host-target",
        default=resolve_host_target(),
        help="set the main target for the build (default: {})".format(
            resolve_host_target()
        )
    )
    # target_group.add_argument(
    #     "--cross-compile-hosts",
    #     default=[],
    #     help="cross-compile the project for the given targets"
    # )

    # --------------------------------------------------------- #
    # Toolchain options

    toolchain_group = parser.add_argument_group("Toolchain options")

    toolchain_selection_group = toolchain_group.add_mutually_exclusive_group(
        required=False
    )

    default_compiler_toolchain = get_clang_toolchain_name()

    toolchain_selection_group.add_argument(
        "-C",
        "--compiler-toolchain",
        default=default_compiler_toolchain,
        choices=get_compiler_toolchain_names(),
        help="resolve paths to the selected compiler toolchain for building "
             "the project if no path is given with '--host-cc' and "
             "'--host-cxx' (default: {})".format(default_compiler_toolchain),
        dest="compiler_toolchain"
    )
    toolchain_selection_group.add_argument(
        "--clang",
        action="store_const",
        const=get_clang_toolchain_name(),
        help="resolve paths to the Clang compiler toolchain for building the "
             "project if no path is given with '--host-cc' and '--host-cxx'",
        dest="compiler_toolchain"
    )
    toolchain_selection_group.add_argument(
        "--gcc",
        action="store_const",
        const=get_gcc_toolchain_name(),
        help="resolve paths to the GCC compiler toolchain for building the "
             "project if no path is given with '--host-cc' and '--host-cxx'",
        dest="compiler_toolchain"
    )

    toolchain_group.add_argument(
        "--compiler-version",
        default=None,
        help="use the given version for the set compiler toolchain if the "
             "compiler toolchain is resolved by the script and not given "
             "manually"
    )

    toolchain_group.add_argument(
        "--host-cc",
        default=None,
        help="give the path to the C compiler for the host platform and use "
             "it instead of the automatically resolved C compiler"
    )
    toolchain_group.add_argument(
        "--host-cxx",
        default=None,
        help="give the path to the C++ compiler for the host platform and use "
             "it instead of the automatically resolved C++ compiler"
    )

    # --------------------------------------------------------- #
    # OpenGL options

    opengl_group = parser.add_argument_group("OpenGL options")

    opengl_group.add_argument(
        "--opengl-version",
        default=get_opengl_version(source_root=source_root),
        help="set the version of OpenGL"
    )

    # --------------------------------------------------------- #
    # TODO Build generator options

    generator_group = parser.add_mutually_exclusive_group(required=False)

    default_cmake_generator = get_ninja_cmake_generator_name()

    parser.set_defaults(cmake_generator=default_cmake_generator)

    generator_group.add_argument(
        "-G",
        "--cmake-generator",
        default=default_cmake_generator,
        choices=get_cmake_generator_names(),
        help="generate the build files using the selected CMake generator",
        dest="cmake_generator"
    )
    generator_group.add_argument(
        "-N",
        "--ninja",
        action="store_const",
        const=get_ninja_cmake_generator_name(),
        help="generate the build files using the CMake generator for Ninja",
        dest="cmake_generator"
    )
    generator_group.add_argument(
        "-m",
        "--make",
        action="store_const",
        const=get_make_cmake_generator_name(),
        help="generate the build files using the CMake generator for Unix "
             "Makefiles",
        dest="cmake_generator"
    )

    return parser


def create_argument_parser(source_root):
    """
    Creates the argument parser of the program.

    source_root -- Path to the directory that is the root of the
    script run.
    """
    parser = argparse.ArgumentParser(
        description=_get_description(source_root=source_root),
        epilog=_get_epilog(source_root=source_root),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # The common arguments are added to the base parser so the
    # normal help command shows them
    parser = _add_common_arguments(parser)

    # --------------------------------------------------------- #
    # Sub-commands

    subparsers = parser.add_subparsers(dest="composer_mode")

    preset = _add_common_arguments(subparsers.add_parser("preset"))
    configure = _add_common_build_arguments(
        _add_common_arguments(
            subparsers.add_parser("configure")
        ),
        source_root=source_root
    )
    compose = _add_common_build_arguments(
        _add_common_arguments(
            subparsers.add_parser("compose")
        ),
        source_root=source_root
    )

    # --------------------------------------------------------- #
    # Preset: Positional arguments

    preset.add_argument(
        "preset_run_mode",
        choices=["configure", "compose"],
        help="run preset invocation in the given mode"
    )

    # --------------------------------------------------------- #
    # Preset: Preset options

    preset_group = preset.add_argument_group("Preset options")

    preset_group.add_argument(
        "--file",
        action="append",
        default=[],
        help="load presets from the given file",
        metavar="PATH",
        dest="preset_file_names"
    )
    preset_group.add_argument(
        "--name",
        help="use the given option preset",
        metavar="NAME",
        dest="preset"
    )
    preset_group.add_argument(
        "--show",
        action="store_true",
        help="list all presets and exit",
        dest="show_presets"
    )
    preset_group.add_argument(
        "--expand-script-invocation",
        action="store_true",
        help="print the build-script invocation made by the preset, but don't "
             "run it"
    )

    # --------------------------------------------------------- #
    # Compose: Common build options

    compose.add_argument(
        "--ode-version",
        default=get_ode_version(source_root=source_root),
        help="set the version of {}".format(get_ode_name(
            source_root=source_root
        ))
    )
    compose.add_argument(
        "--anthem-version",
        default=get_anthem_version(source_root=source_root),
        help="set the version of {}".format(get_anthem_name(
            source_root=source_root
        ))
    )

    compose.set_defaults(libs_to_build=[])

    compose.add_argument(
        "--build-libs",
        action="store_const",
        const=get_all_project_library_names(),
        help="build both the static and shared libraries of {} and {}".format(
            get_ode_name(source_root=source_root),
            get_anthem_name(source_root=source_root)
        ),
        dest="libs_to_build"
    )

    # --------------------------------------------------------- #
    # Compose: Feature options

    compose.add_argument(
        "--ode-window-name",
        default=get_default_ode_window_name(source_root=source_root),
        help="set name of the default window of {}".format(get_ode_name(
            source_root=source_root
        ))
    )
    compose.add_argument(
        "--anthem-window-name",
        default=get_default_anthem_window_name(source_root=source_root),
        help="set name of the default window of {}".format(get_anthem_name(
            source_root=source_root
        ))
    )
    compose.add_argument(
        "--ode-logger-name",
        default=get_default_ode_logger_name(source_root=source_root),
        help="set name of the default logger of {}".format(get_ode_name(
            source_root=source_root
        ))
    )
    compose.add_argument(
        "--anthem-logger-name",
        default=get_default_anthem_logger_name(source_root=source_root),
        help="set name of the default logger of {}".format(get_anthem_name(
            source_root=source_root
        ))
    )
    compose.add_argument(
        "--ode-binaries-name",
        default=get_ode_binaries_base_name(source_root=source_root),
        help="set base name of the binaries of {}".format(get_ode_name(
            source_root=source_root
        ))
    )
    compose.add_argument(
        "--anthem-binaries-name",
        default=get_anthem_binaries_base_name(source_root=source_root),
        help="set base name of the binaries of {}".format(get_anthem_name(
            source_root=source_root
        ))
    )

    assertions_group = compose.add_mutually_exclusive_group()

    assertions_group.set_defaults(assertions=True)

    assertions_group.add_argument(
        "-a",
        "--assertions",
        action="store_true",
        help="enable assertions",
        dest="assertions"
    )
    assertions_group.add_argument(
        "-A",
        "--no-assertions",
        action="store_false",
        help="disable assertions",
        dest="assertions"
    )

    compose.add_argument(
        "-D",
        "--developer-build",
        action="store_true",
        help="enable developer features in the built executables"
    )

    return parser


@cached
def _get_description(source_root):
    """
    Gives the command line description of Couplet Composer.

    source_root -- Path to the directory that is the root of the
    script run.
    """
    return """
Use this tool to build, test, and prepare binary distribution archives of
{ode} and {anthem}.  This tool contains configuration mode that is used prepare
the build environment and composing mode that builds the project.
""".format(
        ode=get_ode_name(source_root=source_root),
        anthem=get_anthem_name(source_root=source_root)
    )


@cached
def _get_epilog(source_root):
    """
    Gives the command line epilogue of Couplet Composer.

    source_root -- Path to the directory that is the root of the
    script run.
    """
    return """
Using option presets:

  preset                use the option preset mode by specifying this argument

  --file=PATH           load presets from the specified file

  --name=NAME         use the specified option preset

  You cannot use the preset mode with other options.  It is not possible to add
  ad hoc customizations to a preset.  If you want to customize a preset, you
  need to create a new preset.


Environment variables
---------------------

This script respects the following environment variables if you set them:

ODE_SOURCE_ROOT: a directory containing the source for {ode}

Couplet Composer expects the sources to be laid out in the following way:

   $ODE_SOURCE_ROOT/unsung-anthem
                   /build           (created automatically)
                   /composer        (created automatically)

The directory '$ODE_SOURCE_ROOT/composer' is created only if the script is run
by using the scripts in the repository of {ode} and {anthem}, which
is the recommended way.

Preparing to run this script
----------------------------

Make sure that your system has C and C++ compilers and Git.

That's it; you're ready to go!

Configuring mode
----------------

Before you can build the project by using so called composing mode, you need to
set up the build environment by using configuring mode of the script.  The you
can invoke configuring mode with the following command:

  [~/src/s]$ ./unsung-anthem/util/configure

You must run the configuring mode only once per one set of command line
options.  After that you can build the project without building the
dependencies every time.

Examples
--------

Given the above layout of sources, the simplest invocation of Couplet Composer
is just:

  [~/src/s]$ ./unsung-anthem/util/configure
  [~/src/s]$ ./unsung-anthem/util/compose

This builds {ode} and {anthem} in debug mode.  All builds are
incremental.  To incrementally build changed files, repeat the same command.

Typical uses of Couplet Composer
--------------------------------

To build everything with optimization without debug information:

  [~/src/s]$ ./unsung-anthem/util/compose -R

To run tests, add '-t':

  [~/src/s]$ ./unsung-anthem/util/compose -R -t

To build the libraries of the project to write add-ons:

  [~/src/s]$ ./unsung-anthem/util/compose --build-libs

To use 'make' instead of 'ninja', use '-m':

  [~/src/s]$ ./unsung-anthem/util/compose -m

Preset mode in Couplet Composer
-------------------------------

All automated environments use Couplet Composer in preset mode.  In preset
mode, the command line only specifies the preset name.  The actual options come
from the selected preset in 'util/composer-presets.ini'.

If you have your own favourite set of options, you can create your own, local,
preset.  For example, let's create a preset called 'release':

  $ cat > ~/.ode-build-presets
  [release]
  release
  test

To use it, invoke the script with the 'preset' command and specify the preset
to expand with the '--name=' argument:

  [~/src/s]$ ./unsung-anthem/util/configure preset --name=release
  Using preset 'release', which expands to

  composer --release --test --
  ...

You can find the existing presets in 'utils/build-presets.ini'

Philosophy
----------

While one can invoke CMake directly to build {anthem}, this tool will save
one's time by taking away the mechanical parts of the process, providing one
the controls for the important options.

For all automated build environments, this tool is regarded as the only way to
build {anthem}.  This is not a technical limitation of the {anthem}
build system.  It is a policy decision aimed at making the builds uniform
across all environments and easily reproducible by engineers who are not
familiar with the details of the setups of other systems or automated
environments.
""".format(
        ode=get_ode_name(source_root=source_root),
        anthem=get_anthem_name(source_root=source_root)
    )
