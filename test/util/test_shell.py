# ------------------------------------------------------------- #
#                       Couplet Composer
# ------------------------------------------------------------- #
#
# This source file is part of the Couplet Composer project which
# is part of the Obliging Ode and Unsung Anthem project.
#
# Copyright 2019 Antti Kivi
# Licensed under the EUPL, version 1.2
#
# ------------------------------------------------------------- #

"""This module defines the tests for the shell utilities."""

from couplet_composer.util import shell


def test_quote_command():
    cmd = ["app", "--option", "value", "--another-option=and-value"]
    expected = "app --option value --another-option=and-value"
    assert shell.quote_command(cmd) == expected
