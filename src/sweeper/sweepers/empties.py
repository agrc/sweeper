#!/usr/bin/env python
# * coding: utf8 *


import arcpy

class EmptyTest():
    '''A class to find empty geometries
    '''
    def __init__(self, workspace, table_name):
        self.report = {}
        self.workspace = workspace
        self.table_name = table_name


    def sweep(self):
        '''A method to find empty geometries and return a report dictionarty
        '''
        fields = ['OID@', 'SHAPE@']

        with arcpy.EnvManager(workspace=self.workspace):
            with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                for oid, geometry in search_cursor:
                    if geometry is not None:
                        continue

                    self.report[oid] = 'empty geometry'

        return self.report


    def try_fix(self):
        '''A method to that attempts to remove records with empty geometries
        '''
        if len(self.report) == 0:
            return

        #: for point, polylines, or polygons
        fields = ['OID@']
        query = f'OBJECTID IN ({",".join(str(object_id) for object_id in self.report)})'

        with arcpy.EnvManager(workspace=self.workspace):
            with arcpy.da.UpdateCursor(self.table_name, fields, query) as update_cursor:
                for oid, in update_cursor:
                    if oid not in self.report:
                        continue

                    update_cursor.deleteRow()
