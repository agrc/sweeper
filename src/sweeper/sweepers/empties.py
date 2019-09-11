#!/usr/bin/env python
# * coding: utf8 *
'''
backup.py
A module that to identify empty geometries in a feature class with ArcPy
'''

import arcpy

class EmptyTest(object):
    def __init__(self, workspace, table_name):
        #: Create dictionaries for reporting that are instance attributes
        self.report = {}
        self.final_report = {}
        self.workspace = workspace
        self.table_name = table_name


    def sweep(self):
        empty_count = 0
        #: for point, polylines, or polygons
        fields = ['OID@', 'SHAPE@']

        arcpy.env.workspace = self.workspace

        with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
            print('Looping through rows in '{} ' ...'.format(self.table_name))

            for oid, geometry in search_cursor:
                bad_geom = False

                #: Check if geometry object is null
                if geometry is None:
                    print('     OID {} has null (None) geometry'.format(oid))
                    bad_geom = True
                    self.report[oid] = {'problem':'null geometry', 'action':'delete'}

                if bad_geom == True:
                    empty_count += 1

        print('Total number of empty geometries: {}'.format(empty_count))
        self.final_report = {'empties': self.report}


    def get_report(self):
        return self.final_report


    def try_fix(self):
        if len(self.report) == 0:
            return

        del_count = 0
        #: for point, polylines, or polygons
        fields = ['OID@']
        query = 'OBJECTID IN ({})'.format(','.join(str(d) for d in self.report))
        print(query)

        with arcpy.da.UpdateCursor(self.feature_class_path, fields, query) as update_cursor:
            print('Looping through rows in '{}' ...'.format(self.feature_class_path))
            for row in update_cursor:
                #: this is a redundant check that OID is in the dictionary
                if row[0] in self.report:
                    update_cursor.deleteRow()
                    del_count += 1

        print('Total number of rows deleted: {}'.format(del_count))
