#!/usr/bin/env python
# * coding: utf8 *


import arcpy
from .. import credentials
import logging

log = logging.getLogger('sweeper')

class EmptyTest():
    '''A class to find empty geometries
    '''
    def __init__(self, workspace, table_name):
        self.workspace = workspace
        self.table_name = table_name
        self.oids_with_issues = []


    def sweep(self):
        '''A method to find empty geometries and return a report dictionarty
        '''
        report = {'title': 'Empty Test', 'feature_class': self.table_name, 'issues': []}
        fields = ['OID@', 'SHAPE@']

        with arcpy.EnvManager(workspace=self.workspace):
            description = arcpy.da.Describe(self.table_name)

            if description['dataType'].casefold() == 'table':
                log.info(f'{self.table_name} is a table, skipping EmptyTest ...')
            else:
                with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                    for oid, geometry in search_cursor:
                        if geometry is not None:
                            continue

                        report['issues'].append(str(oid))
                        self.oids_with_issues.append(oid)

        return report


    def try_fix(self):
        '''A method to that attempts to remove records with empty geometries
        '''
        report = {'title': 'Empty Try Fix', 'feature_class': self.table_name, 'issues': [], 'fixes': []}
        if len(self.oids_with_issues) == 0:
            return report

        #: for point, polylines, or polygons
        fields = ['OID@']
        query = f'OBJECTID IN ({",".join([str(oid) for oid in self.oids_with_issues])})'

        log.info(f'Workspace is:   {self.workspace}')
        with arcpy.EnvManager(workspace=self.workspace):
            with arcpy.da.UpdateCursor(self.table_name, fields, query) as update_cursor:
                for oid, in update_cursor:
                    if oid not in self.oids_with_issues:
                        continue

                    update_cursor.deleteRow()

        report['fixes'].append(f'{len(self.oids_with_issues)} records deleted successfully')

        return report

    def clone(self, table_name):
        log.info(f'cloning to {table_name}')
        user = table_name.split('.')[0].upper()
        user_workspace = credentials.CONNECTIONS[user]
        return EmptyTest(user_workspace, table_name)
