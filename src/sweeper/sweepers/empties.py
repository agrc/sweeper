#!/usr/bin/env python
# * coding: utf8 *
'''
backup.py
A module that to identify empty geometries in a feature class with ArcPy
'''

#import os
import arcpy

class EmptyTest(object):
    def __init__(self, workspace, table_name):
        #: Create dictionaries for reporting that are instance attributes
        self.report = {}
        self.workspace = workspace
        self.table_name = table_name


    def sweep(self):
        empty_count = 0
        #: for point, polylines, or polygons
        fields = ['OID@', 'SHAPE@']

        arcpy.env.workspace = self.workspace

        with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:

            for oid, geometry in search_cursor:
                #: Check if geometry object is null
                if geometry is None:
                    self.report[oid] = 'empty geometry'
                    empty_count += 1

        return self.report


    def try_fix(self):
        if len(self.report) == 0:
            return

        del_count = 0
        #: for point, polylines, or polygons
        fields = ['OID@']
        query = 'OBJECTID IN ({})'.format(','.join(str(d) for d in self.report))
        with arcpy.da.UpdateCursor(self.table_name, fields, query) as update_cursor:
            for oid, in update_cursor:
                #: this is a redundant check that OID is in the dictionary
                if oid in self.report:
                    update_cursor.deleteRow()
                    del_count += 1
