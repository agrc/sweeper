#!/usr/bin/env python
# * coding: utf8 *
'''
test_addresses.py
tests for the addresses sweeper
'''
from os import path

from ..sweepers.addresses import AddressTest


current_folder = path.dirname(__file__)


def test_issues():
    workspace = path.join(current_folder, 'data', 'addresses.gdb')
    tool = AddressTest(workspace, 'Normalize', 'StreetAddress')
    report = tool.sweep()

    assert len(report['issues']) == 5
