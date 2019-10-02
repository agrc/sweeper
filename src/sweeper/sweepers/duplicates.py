#!/usr/bin/env python
# * coding: utf8 *
import re

from xxhash import xxh64

import arcpy


class DuplicateTest():
    '''A class that finds and removes duplicate geometries or attributes or both
    '''
    def __init__(self, workspace, table_name):
        self.report = {}
        self.workspace = workspace
        self.table_name = table_name


    def sweep(self):
        '''A method that finds duplicate records and returns a report dictionary
        '''
        digests = set([])

        truncate_shape_precision = re.compile(r'(\d+\.\d{2})(\d+)')

        with arcpy.EnvManager(workspace=self.workspace):
            description = arcpy.da.Describe(self.table_name)

            skip_fields = ['guid', description.shapeFieldName]

            if description.hasGlobalID:
                skip_fields.append(description.globalIDFieldName)

            if description.hasOID:
                skip_fields.append(description.OIDFieldName)

            fields = [field.name for field in description.fields if field.name not in skip_fields]

            fields.append('SHAPE@WKT')
            fields.append('OID@')

            shapefield_index = fields.index('SHAPE@WKT')
            oid_index = fields.indexOf('OID@')

            with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                for row in search_cursor:
                    shape_wkt = row[shapefield_index]
                    object_id = row[oid_index]

                    if shape_wkt is None:
                        self.report[object_id] = 'empty geometry'

                        continue

                    #: trim some digits to help with hash matching
                    generalized_wkt = truncate_shape_precision.sub(r'\1', shape_wkt)

                    hasher = xxh64(f'{row[:-2]} {generalized_wkt}')
                    digest = hasher.hexdigest()

                    if digest in digests:
                        self.report[object_id] = 'duplicate feature'

                        continue

                    digests.add(digest)

        return self.report


    def try_fix(self):
        '''a method that tries to remove the duplicate records
        '''
        if len(self.report) == 0:
            return

        sql = f'"OBJECTID" IN ({",".join(str(object_id) for object_id in self.report)})'
        temp_feature_layer = 'temp_layer'

        with arcpy.EnvManager(workspace=self.workspace):
            try:
                duplicate_features = arcpy.management.MakeFeatureLayer(self.table_name, temp_feature_layer, sql)

                print(f'attempting to delete {len(self.report)} duplicate records')

                arcpy.management.DeleteFeatures(duplicate_features)
            except Exception as error:
                print(f'unable to delete features {error}')
            finally:
                if arcpy.Exists(temp_feature_layer):
                    arcpy.management.Delete(temp_feature_layer)
