#!/usr/bin/env python
# * coding: utf8 *
'''
test_metadata.py
a module that tests the metadata sweeper
'''
from os import path
from unittest import TestCase

from ..sweepers.metadata import MetadataTest, title_case_tag, update_tags, get_description_text_only

current_folder = path.dirname(__file__)
workspace = path.join(current_folder, 'data', 'Sweeper as CADASTRE.sde')


def contains_issue_with_text(issues, text):
    for issue in issues:
        if issue.find(text) > -1:
            return True

    return False

def does_not_contain_issue_with_text(issues, text):
    for issue in issues:
        if issue.find(text) > -1:
            return False

    return True

class TestMetadataSweeper(TestCase):

    def test_no_tags(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.MissingTags')
        report = tool.sweep()

        assert contains_issue_with_text(report['issues'], 'missing tags')

    def test_title_cased_tags(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.IncorrectCasing')
        report = tool.sweep()

        assert does_not_contain_issue_with_text(report['issues'], 'missing tags')
        assert contains_issue_with_text(report['issues'], 'incorrectly cased tag')


class TestTitleCaseTag(TestCase):

    def test_title_case_tag(self):
        #: input, expected
        tests = [['ugrc', 'UGRC'], ['Plss Fabric', 'PLSS Fabric'], ['water-related', 'Water-Related'], ['test', 'Test'],
                 ['article is a good test', 'Article is a Good Test']]

        for input_tag, expected in tests:
            assert title_case_tag(input_tag) == expected


class TestUpdateTags(TestCase):

    def test_update_tags(self):
        results = update_tags(['a', 'b', 'c', 'd'], ['b', 'c'], ['B', 'E'])
        expected = ['a', 'd', 'B', 'E']

        assert results == expected


class TestSummary(TestCase):

    def test_summary_longer_than_description(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.SummaryLongerThanDescription')
        report = tool.sweep()

        assert contains_issue_with_text(report['issues'], 'Summary is longer than Description')

    def test_summary_too_long(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.SummaryTooLong')
        report = tool.sweep()

        assert contains_issue_with_text(report['issues'], 'Summary is longer than')


class TestDescriptionParsing(TestCase):

    def test_get_description_text_only(self):
        input = '<DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is a short description.</SPAN></P></DIV></DIV>'

        assert get_description_text_only(input) == 'This is a short description.'

    def test_handles_none(self):
        assert get_description_text_only(None) == ''


class TestDescriptionChecks(TestCase):

    def test_find_data_page_link(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.WithoutDataPageLink')
        report = tool.sweep()

        assert contains_issue_with_text(report['issues'], 'Description is missing link')

    def test_existing_link(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.WithDataPageLink')
        report = tool.sweep()

        assert does_not_contain_issue_with_text(report['issues'], 'Description is missing link')


class TestUseLimitation(TestCase):

    def test_correct_use_limitation(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.CorrectUseLimitations')
        report = tool.sweep()

        assert does_not_contain_issue_with_text(report['issues'], 'Use limitations')

    def test_incorrect_use_limitation(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.WithBadUseLimitations')
        report = tool.sweep()

        assert contains_issue_with_text(report['issues'], 'Use limitations text is not standard')
        assert tool.use_limitations_needs_update

    def test_no_use_limitation(self):
        tool = MetadataTest(workspace, 'Sweeper.CADASTRE.WithoutUseLimitations')
        report = tool.sweep()

        assert contains_issue_with_text(report['issues'], 'Use limitations text is missing')
        assert tool.use_limitations_needs_update
