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
This support module contains type ToolData for creating the
toolchain and the functions for handling the creation of ToolData
objects for each tool for the toolchain.
"""

import importlib

from collections import namedtuple

from .project_names import get_project_package_name


# The type 'ToolData' represent the data to construct a tool.
# Thus, the tuple contains various functions that the toolchain
# utilizes when it constructs itself.
#
# get_tool_type -- Returns the type of the tool for the
# toolchain, e.g. 'cc' or 'cxx'
#
# get_searched_tool -- Returns a string that represents the name
# that is used if the tool is looked for from the system. TODO:
# Parameters
#
# get_required_local_version -- Returns a string that represents
# version of the tool that is donwloaded when the tool isn't
# found. Returns None if the tool can't be installed locally. The
# parameters for the function are: target, host_system
#
# get_local_executable -- Returns path to the local executable of
# the tool. Returns None if the tool can't be installed locally.
# The parameters for the function are: tools_root, version,
# target, host_system
ToolData = namedtuple("ToolData", [
    "get_tool_type",
    "get_searched_tool",
    "get_required_local_version",
    "get_local_executable"
])


def _create_tool_data(module_name):
    """
    Creates a common ToolData object of a tool for toolchain.
    This function isn't totally pure as it imports the module
    using importlib.

    module_name -- The name of the module from which the various
    functions are got.
    """
    package_name = "{}.tools.{}".format(
        get_project_package_name(),
        module_name
    )
    tool_module = importlib.import_module(package_name)
    return ToolData(
        get_tool_type=getattr(tool_module, "get_tool_type"),
        get_searched_tool=lambda: module_name,
        get_required_local_version=getattr(tool_module, "get_version"),
        get_local_executable=getattr(tool_module, "get_local_executable")
    )


def create_clang_tool_data():
    """Creates the ToolData object of Clang for toolchain."""
    return ToolData(
        get_tool_type=lambda: "cc",
        get_searched_tool=lambda: "clang",
        get_required_local_version=None,
        get_local_executable=None
    )


def create_clangxx_tool_data():
    """Creates the ToolData object of Clang++ for toolchain."""
    return ToolData(
        get_tool_type=lambda: "cxx",
        get_searched_tool=lambda: "clang++",
        get_required_local_version=None,
        get_local_executable=None
    )


def create_cmake_tool_data():
    """
    Creates the ToolData object of CMake for toolchain. This
    function isn't totally pure as it imports the module using
    importlib.
    """
    return _create_tool_data("cmake")


def create_ninja_tool_data():
    """
    Creates the ToolData object of Ninja for toolchain. This
    function isn't totally pure as it imports the module using
    importlib.
    """
    return _create_tool_data("ninja")