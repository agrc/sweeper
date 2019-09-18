#!/usr/bin/env python
# * coding: utf8 *
'''
duplicates.py
A module that removes duplicate geometry or attributes or both
'''

import arcpy
import re
import os
from xxhash import xxh64

class DuplicateTest(object):
    def __init__(self, workspace, table_name):
        self.report = {}
        self.workspace = workspace
        self.table_name = table_name


    def sweep(self):

        digest_dict = {}

        dig_trim = re.compile(r'(\d+\.\d{2})(\d+)')

        arcpy.env.workspace = self.workspace

        def is_skip_field(field):
            return 'SHAPE' in field.upper() or field.upper() in ['OBJECTID', 'FID', 'GLOBAL_ID', 'GLOBALID']

        fields = [f.name for f in arcpy.ListFields(self.table_name) if not is_skip_field(f.name)]
        fields.append('SHAPE@WKT')
        fields.append('OID@')

        with arcpy.da.SearchCursor(self.table_name, fields) as sCursor:
            for row in sCursor:
                shp = row[-2]
                if shp != None:
                    coord_trim = dig_trim.sub(r'\1', shp)
                    hash = xxh64('{} {}'.format(row[:-2], coord_trim))
                    digest = hash.hexdigest()
                    if digest not in digest_dict:
                        digest_dict.setdefault(digest)
                    else:
                        self.report[row[-1]] = 'duplicate feature'

                else:
                    self.report[row[-1]] = 'empty geometry'

        arcpy.ClearEnvironment('workspace')
        return self.report
        


    def try_fix(self):

        arcpy.env.workspace = self.workspace
        if len(self.report) > 0:
            try:
                sql = '"OBJECTID" IN ({})'.format(', '.join(str(d) for d in self.report))
                duplicate_FL = arcpy.MakeFeatureLayer_management(self.table_name, 'duplicate_FL', sql)
                print('Deleted {} duplicate records'.format(len(self.report)))
                arcpy.DeleteFeatures_management(duplicate_FL)
            except:
                print('unable to delete features')

        arcpy.ClearEnvironment('workspace')

    