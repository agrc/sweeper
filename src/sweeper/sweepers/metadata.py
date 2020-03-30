#!/usr/bin/env python
# * coding: utf8 *
'''
metadata.py
A sweeper that checks geodatabase metadata
'''

import arcpy


class MetadataTest():
    '''A class that implements a sweeper for metadata
    '''
    def __init__(self, workspace, table_name):
        self.workspace = workspace
        self.table_name = table_name
        self.oids_with_issues = []

    def sweep(self):
        pass

    def try_fix(self):
        pass

    def clone(self, table_name):
        print(f'cloning to {table_name}')
        return MetadataTest(self.workspace, table_name)
