#!/usr/bin/env python
# * coding: utf8 *
'''
test_metadata.py
a module that tests the metadata sweeper
'''
from os import path
from unittest import TestCase

from ..sweepers.metadata import MetadataTest, title_case_tag, update_tags

current_folder = path.dirname(__file__)
workspace = path.join(current_folder, 'data', 'Sweeper as CADASTRE.sde')


class TestMetadataSweeper(TestCase):

    def test_no_tags(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.MissingTags')
        report = tool.sweep()

        assert len(report['issues']) == 1
        self.assertRegex(report['issues'][0], r'missing tags')

    def test_title_cased_tags(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.IncorrectCasing')
        report = tool.sweep()

        assert len(report['issues']) == 3
        self.assertRegex(report['issues'][0], r'incorrectly cased tag')


class TestTitleCaseTag(TestCase):

    def test_title_case_tag(self):
        #: input, expected
        tests = [['agrc', 'AGRC'], ['Plss Fabric', 'PLSS Fabric'], ['water-related', 'Water-Related'], ['test', 'Test'],
                 ['article is a good test', 'Article is a Good Test']]

        for input_tag, expected in tests:
            assert title_case_tag(input_tag) == expected


class TestUpdateTags(TestCase):

    def test_update_tags(self):
        results = update_tags(['a', 'b', 'c', 'd'], ['b', 'c'], ['B', 'E'])
        expected = ['a', 'd', 'B', 'E']

        assert results == expected
