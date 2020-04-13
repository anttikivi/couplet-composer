# Copyright (c) 2019 Antti Kivi
# Licensed under the MIT License

"""
This support module contains the functions related to the
building and finding stb_image.
"""

import os

from ..github import repository

from ..support.environment import get_temporary_directory

from ..support.github_data import GitHubData

from ..util.cache import cached

from ..util import shell


################################################################
# DEPENDENCY DATA FUNCTIONS
################################################################


@cached
def should_install(
    dependencies_root,
    version,
    target,
    host_system,
    installed_version
):
    """
    Tells whether the build of the dependency should be skipped.

    dependencies_root -- The root directory of the dependencies
    for the current build target.

    version -- The full version number of the dependency.

    target -- The target system of the build represented by a
    Target.

    host_system -- The system this script is run on.

    installed_version -- The version of the dependecy that is
    written to the JSON file containing the currently installed
    versions of the dependencies.
    """
    if not installed_version or version != installed_version:
        return True

    return not os.path.exists(
        os.path.join(dependencies_root, "include", "stb_image.h")
    )


def install_dependency(
    toolchain,
    cmake_generator,
    build_root,
    dependencies_root,
    version,
    target,
    host_system,
    build_variant,
    github_user_agent,
    github_api_token,
    opengl_version,
    dry_run=None,
    print_debug=None
):
    """
    Installs the dependency by downloading and possibly building
    it. Returns the path to the built dependency.

    toolchain -- The toolchain object of the run.

    cmake_generator -- The name of the generator that CMake
    should use as the build system for which the build scripts
    are generated.

    build_root -- The path to the root directory that is used for
    all created files and directories.

    dependencies_root -- The root directory of the dependencies
    for the current build target.

    version -- The full version number of the dependency.

    target -- The target system of the build represented by a
    Target.

    host_system -- The system this script is run on.

    build_variant -- The build variant used to build the project.

    github_user_agent -- The user agent used when accessing the
    GitHub API.

    github_api_token -- The GitHub API token that is used to
    access the API.

    opengl_version -- The version of OpenGL that is used.

    dry_run -- Whether the commands are only printed instead of
    running them.

    print_debug -- Whether debug output should be printed.
    """
    temp_dir = get_temporary_directory(build_root=build_root)

    shell.makedirs(temp_dir, dry_run=dry_run, echo=print_debug)

    asset_path = repository.clone(
        path=temp_dir,
        git=toolchain.scm,
        github_data=GitHubData(
            owner="nothings",
            name="stb",
            tag_name=None,
            asset_name=None
        ),
        user_agent=github_user_agent,
        api_token=github_api_token,
        host_system=host_system,
        commit="0224a44a10564a214595797b4c88323f79a5f934",
        dry_run=dry_run,
        print_debug=print_debug
    )

    if not os.path.isdir(os.path.join(dependencies_root, "include")):
        shell.makedirs(os.path.join(dependencies_root, "include"))
    if os.path.exists(os.path.join(
        dependencies_root,
        "include",
        "stb_image.h"
    )):
        shell.rmtree(
            os.path.join(dependencies_root, "include", "stb_image.h"),
            dry_run=dry_run,
            echo=print_debug
        )
    shell.copy(
        os.path.join(asset_path, "stb_image.h"),
        os.path.join(dependencies_root, "include", "stb_image.h"),
        dry_run=dry_run,
        echo=print_debug
    )

    shell.rmtree(temp_dir, dry_run=dry_run, echo=print_debug)
