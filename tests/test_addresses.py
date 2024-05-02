#!/usr/bin/env python
# * coding: utf8 *
"""
test_addresses.py
tests for the addresses sweeper
"""

from os import path

# ruff: isort: off
from . import mock_arcpy  # noqa: F401
from sweeper.sweepers.addresses import AddressTest

# ruff: isort: on

current_folder = path.dirname(__file__)


def test_issues(skip_if_no_arcpy):
    workspace = path.join(current_folder, "data", "addresses.gdb")
    tool = AddressTest(workspace, "Normalize", "StreetAddress")
    report = tool.sweep()

    assert len(report["issues"]) == 5
