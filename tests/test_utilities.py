#!/usr/bin/env python
# * coding: utf8 *
"""
test_utilities.py
tests for the utilities module
"""

from sweeper import utilities


class TestApplyExclusions:
    def test_simple_exclusions(self):
        exclusions = [
            "test1",
            "test2",
            "test3",
        ]
        test_list = [
            "test1",
            "test2",
            "test4",
            "test5",
        ]
        result = utilities.apply_exclusions(test_list, exclusions)
        assert result == ["test4", "test5"]

    def test_glob_exclusions(self):
        exclusions = [
            "test*",
        ]
        test_list = ["test1", "test2", "test4", "test5", "hello"]
        result = utilities.apply_exclusions(test_list, exclusions)
        assert result == ["hello"]

    def test_no_exclusions(self):
        exclusions = []
        test_list = ["test1", "test2", "test4", "test5", "hello"]
        result = utilities.apply_exclusions(test_list, exclusions)
        assert result == test_list

    def test_case_insensitive(self):
        exclusions = [
            "TEST*",
        ]
        test_list = ["test1", "test2", "test4", "test5", "hello"]
        result = utilities.apply_exclusions(test_list, exclusions)
        assert result == ["hello"]
