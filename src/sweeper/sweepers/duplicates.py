#!/usr/bin/env python
# * coding: utf8 *
import re

from xxhash import xxh64
from .. import credentials

import arcpy
import logging

log = logging.getLogger('sweeper')

class DuplicateTest():
    '''A class that finds and removes duplicate geometries or attributes or both
    '''
    def __init__(self, workspace, table_name):
        self.workspace = workspace
        self.table_name = table_name
        self.oids_with_issues = []
        self.is_table = False


    def sweep(self):
        '''A method that finds duplicate records and returns a report dictionary
        '''
        report = {'title': 'Duplicate Test', 'feature_class': self.table_name, 'issues': []}
        digests = set([])

        truncate_shape_precision = re.compile(r'(\d+\.\d{2})(\d+)')

        with arcpy.EnvManager(workspace=self.workspace):
            description = arcpy.da.Describe(self.table_name)
            log.info(f'Working on Duplicates for: {self.table_name}')
            if description['dataType'].casefold() == 'table':
                self.is_table = True
                skip_fields = ['guid']
            else:
                skip_fields = ['guid', description['shapeFieldName']]


            if description['hasGlobalID']:
                skip_fields.append(description['globalIDFieldName'])

            if description['hasOID']:
                skip_fields.append(description['OIDFieldName'])

            fields = [field.name for field in description['fields'] if field.name not in skip_fields]
            fields.append('OID@')

            #: include or exclude shape field depending on if working on table or feature class
            if self.is_table:
                oid_index = fields.index('OID@')

                with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                    for row in search_cursor:
                        object_id = row[oid_index]

                        hasher = xxh64(f'{row[:-1]}')
                        digest = hasher.hexdigest()

                        if digest in digests:
                            report['issues'].append(str(object_id))
                            self.oids_with_issues.append(object_id)

                        digests.add(digest)
            else:
                oid_index = fields.index('OID@')            
                fields.append('SHAPE@WKT')           

                shapefield_index = fields.index('SHAPE@WKT')
                oid_index = fields.index('OID@')

                with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                    for row in search_cursor:
                        shape_wkt = row[shapefield_index]
                        object_id = row[oid_index]

                        if shape_wkt is None:
                            continue

                        #: trim some digits to help with hash matching
                        generalized_wkt = truncate_shape_precision.sub(r'\1', shape_wkt)

                        hasher = xxh64(f'{row[:-2]} {generalized_wkt}')
                        digest = hasher.hexdigest()

                        if digest in digests:
                            report['issues'].append(str(object_id))
                            self.oids_with_issues.append(object_id)

                        digests.add(digest)

        return report


    def try_fix(self):
        '''a method that tries to remove the duplicate records
        '''
        report = {'title': 'Duplicate Try Fix', 'feature_class': self.table_name, 'issues': [], 'fixes': []}

        if len(self.oids_with_issues) == 0:
            return report

        sql = f'"OBJECTID" IN ({",".join([str(oid) for oid in self.oids_with_issues])})'
        temp_feature_layer = 'temp_layer'

        log.info(f'Workspace is:   {self.workspace}')
        #: Delete duplicate rows using different arcpy tools for tables and feature classes
        with arcpy.EnvManager(workspace=self.workspace):
            if self.is_table:
                duplicate_features = arcpy.management.MakeTableView(self.table_name, temp_feature_layer, sql)
            else:
                duplicate_features = arcpy.management.MakeFeatureLayer(self.table_name, temp_feature_layer, sql)
            
            try:
                log.info(f'attempting to delete {len(self.oids_with_issues)} duplicate records')
                if self.is_table:
                    arcpy.management.DeleteRows(duplicate_features)
                else:
                    arcpy.management.DeleteFeatures(duplicate_features)
                
                except Exception as error:
                    error_message = f'unable to delete features {error}'
                    report['issues'].append(error_message)
                finally:
                    if arcpy.Exists(temp_feature_layer):
                        arcpy.management.Delete(temp_feature_layer)

            report['fixes'].append(f'{len(self.oids_with_issues)} records deleted successfully')

        return report

    def clone(self, table_name):
        log.info(f'cloning to {table_name}')
        user = table_name.split('.')[0].upper()
        user_workspace = credentials.CONNECTIONS[user]
        return DuplicateTest(user_workspace, table_name)
