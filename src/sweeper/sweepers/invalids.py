#!/usr/bin/env python
# * coding: utf8 *


class InvalidSweeper:
    """A class that identifies invalid geometry objects and returns a report dictionary"""

    key = "invalids"

    def __init__(self, workspace, table_name):
        self.report = {}
        self.workspace = workspace
        self.table_name = table_name

    def sweep(self):
        """A method to find invalid geometries and return a report dictionary"""

    def try_fix(self):
        """A method to that attempts to repair records with invalid geometries"""
