#!/usr/bin/env python
# * coding: utf8 *


import arcpy

class EmptyTest():
    '''A class to find empty geometries
    '''
    def __init__(self, workspace, table_name):
        self.report = {'title': 'Empty Test', 'feature_class': table_name, 'issues': []}
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

                    self.report['issues'].append(str(oid))

        return self.report


    def try_fix(self):
        '''A method to that attempts to remove records with empty geometries
        '''
        if len(self.report['issues']) == 0:
            return

        #: for point, polylines, or polygons
        fields = ['OID@']
        query = f'OBJECTID IN ({",".join(self.report["issues"])})'

        with arcpy.EnvManager(workspace=self.workspace):
            with arcpy.da.UpdateCursor(self.table_name, fields, query) as update_cursor:
                for oid, in update_cursor:
                    if str(oid) not in self.report['issues']:
                        continue

                    update_cursor.deleteRow()


    def clone(self, table_name):
        print(f'cloning to {table_name}')
        return EmptyTest(self.workspace, table_name)
