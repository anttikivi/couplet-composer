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


"""
This support module contains the functions for resolving and
building the toolchain required to build the project that this
script acts on.
"""

from collections import namedtuple

import os

from .support.platform_names import \
    get_darwin_system_name, get_linux_system_name, get_windows_system_name

from .util.where import where

from .util.which import which

from .util import xcrun


# The type 'Toolchain' represents the toolchain for the script.
# The tools in the toolchain are following:
#
# cc -- C compiler.
#
# cxx -- C++ compiler.
#
# cmake -- CMake.
#
# build_system -- The build system that CMake generates the
# scripts for, e.g. Ninja or Make.
Toolchain = namedtuple("Toolchain", ["cc", "cxx", "cmake", "build_system"])


def construct_tools_data(tools):
    """
    Constructs a list of objects of type 'ToolData' to be used in
    the creation of the toolchain. This function isn't pure as it
    gets data from the given modules.

    tools -- Dictionary of tool names and handler functions. The
    handler function for each tool should be responsible for
    returning the correct functions to the construction of the
    object of type ToolData.
    """
    return [tools[name]() for name in tools.keys()]


def _resolve_local_tools(
    tools_data,
    cmake_generator,
    target,
    host_system,
    tools_root
):
    """
    Checks whether or not the tools required by this run of the
    script exist locally and returns two lists: the first one
    contains the found tools and the second one the missing
    tools.

    tools_data -- List of objects of type ToolData that contain
    the functions for checking and building the tools.

    cmake_generator -- The name of the generator that CMake
    should use as the build system for which the build scripts
    are generated. It's used to determine which build system is
    checked for and built if necessary.

    target -- The target system of the build represented by a
    Target.

    host_system -- The system this script is run on.

    tools_root -- The root directory of the tools for the current
    build target.
    """
    accumulated_found_tools = [
        data for data in tools_data
        if data.get_local_executable is not None and os.path.exists(
            data.get_local_executable(
                tools_root=tools_root,
                version=data.get_required_local_version(
                    target=target,
                    host_system=host_system
                ),
                target=target,
                host_system=host_system
            )
        )
    ]
    accumulated_missing_tools = [
        data for data in tools_data
        if data.get_local_executable is None or not os.path.exists(
            data.get_local_executable(
                tools_root=tools_root,
                version=data.get_required_local_version(
                    target=target,
                    host_system=host_system
                ),
                target=target,
                host_system=host_system
            )
        )
    ]
    return accumulated_found_tools, accumulated_missing_tools


def _find_tool(tool, host_system):
    """
    Looks for a tool on the system and returns the path to the
    tool if it was found.

    tool -- The tool to look for.

    host_system -- The name of the system this script is run on.
    """
    if host_system == get_darwin_system_name():
        return xcrun.find(tool)
    elif host_system == get_linux_system_name():
        return which(tool)
    elif host_system == get_windows_system_name():
        return where(tool)
    else:
        return None


def create_toolchain(
    tools_data,
    cmake_generator,
    target,
    host_system,
    tools_root
):
    """
    Creates the toolchain for this run. This function isn't pure
    as it reads files, calls shell commands, and downloads and
    builds the required tools if they're missing.

    This currently supports only downloading and building CMake
    and Ninja if they're missing from the system. Ninja isn't
    even required for the builds. Other tools, like compilers,
    must be presents.

    Returns a named tuple of type 'Toolchain' that contains the
    tool executables that are used.

    tools_data -- List of objects of type ToolData that contain
    the functions for checking and building the tools.

    cmake_generator -- The name of the generator that CMake
    should use as the build system for which the build scripts
    are generated. It's used to determine which build system is
    checked for and built if necessary.

    target -- The target system of the build represented by a
    Target.

    host_system -- The system this script is run on.

    tools_root -- The root directory of the tools for the current
    build target.
    """
    # The function contains internal non-pure element as this
    # dictionary is modified when new tools are resolved.
    found_tools = {}

    # Start by checking if a correct local copy of the tool
    # exists.
    found_local_tools, missing_local_tools = _resolve_local_tools(
        tools_data=tools_data,
        cmake_generator=cmake_generator,
        target=target,
        host_system=host_system,
        tools_root=tools_root
    )

    # Add the found tools to the dictionary.
    for tool in found_local_tools:
        found_tools.update({tool.get_tool_type(): tool.get_local_executable(
            tools_root=tools_root,
            version=tool.get_required_local_version(target=target),
            target=target
        )})

    missing_tools = []

    # If a tool is missing, look for it from the host system.
    for tool in missing_local_tools:
        found_tool = _find_tool(
            tool=tool.get_searched_tool(),
            host_system=host_system
        )
        if found_tool:
            found_tools.update({tool.get_tool_type(): found_tool})
        else:
            missing_tools.append(tool)

    # Download the missing tools.

    return None  # Toolchain()