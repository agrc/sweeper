#!/usr/bin/env python
# * coding: utf8 *
'''
test_metadata.py
a module that tests the metadata sweeper
'''
from os import path
from unittest import TestCase

from ..sweepers.metadata import MetadataTest


current_folder = path.dirname(__file__)
workspace = path.join(current_folder, 'data', 'Sweeper as CADASTRE.sde')


class TestMetadataSweeper(TestCase):
    def test_no_tags(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.MissingTags')
        report = tool.sweep()

        assert len(report['issues']) == 1
        self.assertRegex(report['issues'][0], r'missing tags')
