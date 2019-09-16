#!/usr/bin/env python
# * coding: utf8 *
'''
duplicates.py
A module that removes duplicate geometry or attributes or both
'''

import arcpy
import re
from xxhash import xxh64

class DuplicateTest(object):
    def __init__(self):
        self.report = {}
        self.workspace = workspace
        self.table_name = table_name


    def sweep(self):

        digestDict = {}

        digTrim = re.compile(r'(\d+\.\d{2})(\d+)')

        shps = ['Shape', 'SHAPE']
        fields = [f.name for f in arcpy.ListFields(self.table_name) if f.name not in shps]
        fields.append('SHAPE@WKT')

        with arcpy.da.SearchCursor(self.table_name, fields) as sCursor:
            for row in sCursor:
                shp = row[-1]
                if shp != None:
                    coordTrim = digTrim.sub(r'\1', shp)
                    hash = xxh64('{} {}'.format(row[1:-1], coordTrim))
                    digest = hash.hexdigest()
                    if digest not in digestDict:
                        digestDict.setdefault(digest)
                    else:
                        self.report[row[0]] = 'duplicate feature'

                else:
                    self.report[row[0]] = 'empty geometry'

        return self.report


    def try_fix(self):
        if len(self.report) > 0:
            try:
                sql = '"OBJECTID" IN ({})'.format(', '.join(str(d) for d in self.report))
                duplicate_FL = arcpy.MakeFeatureLayer_management(fc, 'duplicate_FL', sql)
                print('Deleted {} duplicate records'.format(len(self.report)))
                arcpy.DeleteFeatures_management(duplicate_FL)
            except:
                print('unable to delete features')

    