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


    def sweep(self, fc):

        digestDict = {}
        duplicateDict = {}
        dupePrintLst = []
        digTrim = re.compile(r'(\d+\.\d{2})(\d+)')

        shps = ['Shape', 'SHAPE']

        fields = [f.name for f in arcpy.ListFields(fc) if f.name not in shps]
        fields.append('SHAPE@WKT')

        with arcpy.da.SearchCursor(fc, fields) as sCursor:
            for row in sCursor:
                shp = row[-1]
                if shp != None:
                    coordTrim = digTrim.sub(r'\1', shp)
                    hash = xxh64('{} {}'.format(row[1:], coordTrim))
                    digest = hash.hexdigest()
                    if digest not in digestDict:
                        digestDict.setdefault(digest)
                    else:
                        duplicates = duplicateDict.setdefault('Duplicate Features', [])
                        duplicates.extend(row[0])
                else:
                    duplicateDict.extend(row[0])



    def get_report(duplicateDict):
        return duplicateDict


    def try_fix(self, duplicateDict):
        try:
            sql = '"OBJECTID" IN ({})'.format(', '.join(str(d) for d in duplicateDict['Duplicate Features']))
            duplicate_FL = arcpy.MakeFeatureLayer_management(fc, 'duplicate_FL', sql)
            print ('Deleted {} records'.format(len(duplicateLst)))
            arcpy.DeleteFeatures_management(duplicatePts_FL)

    

