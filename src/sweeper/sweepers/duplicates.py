#!/usr/bin/env python
# * coding: utf8 *
'''
duplicates.py
A module that removes duplicate geometry or attributes or both
'''

import arcpy
import re
from xxhash import xxh64

def removeNone(word):
    if word == None:
        word = ''
    return word

def deleteDuplicateFeatures(inFc):

    digestDict = {}
    duplicateLst = []
    dupePrintLst = []
    digTrim = re.compile(r'(\d+\.\d{2})(\d+)')

    shps = ['Shape', 'SHAPE']

    fields = [f.name for f in arcpy.ListFields(inFc) if f.name not in shps]
    fields.append('SHAPE@WKT')
    print(fields)
    # if 'Shape' in fields:
    #     shpIndex = fields.index('Shape')
    # else:
    #     shpIndex = fields.index('SHAPE')

    with arcpy.da.SearchCursor(inFc, fields) as sCursor:
        for row in sCursor:
            shp = row[-1]
            if shp != None:
                coordTrim = digTrim.sub(r'\1', shp)
                hash = xxh64('{} {}'.format(row[1:], coordTrim))
                digest = hash.hexdigest()
                if digest not in digestDict:
                    digestDict.setdefault(digest)
                else:
                    duplicateLst.append(row[0])
                    dupePrintLst.append(row)
            if shp == None:
                duplicateLst.append(row[0])
                dupePrintLst.append(row)

    #     print (dupePrintLst)
    #     print (duplicateLst)

    if len(duplicateLst) >= 1:
        sql = '"OBJECTID" IN ({})'.format(', '.join(str(d) for d in duplicateLst))
        duplicatePts_FL = arcpy.MakeFeatureLayer_management(inFc, 'duplicatePts_FL', sql)
        print ('Deleted {} records'.format(len(duplicateLst)))
        arcpy.DeleteFeatures_management(duplicatePts_FL)
    else:
        print ('No Duplicates found')
    
fc = r'C:\ZBECK\Addressing\Beaver\BeaverCounty.gdb\Address_ptsOLD'
deleteDuplicateFeatures(fc)