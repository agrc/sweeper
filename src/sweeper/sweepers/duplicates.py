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


        dig_trim = re.compile(r'(\d+\.\d{2})(\d+)')

        arcpy.env.workspace = self.workspace

        fields = [f.name for f in arcpy.ListFields(self.table_name) if f.type not in ['OID', 'Guid', 'GlobalID', 'Geometry']]
        fields.append('SHAPE@WKT')
        fields.append('OID@')

        with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
            for row in search_cursor:
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
        '''a method that tries to remove the duplicate records
        '''

        arcpy.env.workspace = self.workspace
        if len(self.report) > 0:
            try:
                sql = '"OBJECTID" IN ({})'.format(', '.join(str(d) for d in self.report))
                duplicate_FL = arcpy.management.MakeFeatureLayer(self.table_name, 'duplicate_FL', sql)
                print('Deleted {} duplicate records'.format(len(self.report)))
                arcpy.DeleteFeatures_management(duplicate_FL)
            except:
                print('unable to delete features')

        arcpy.ClearEnvironment('workspace')

    