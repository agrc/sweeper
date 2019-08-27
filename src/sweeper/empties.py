# -*- coding: utf-8 -*-
'''
Created on Thu Aug 8 13:54:56 2019
@author: eneemann
Script to identify empty geometries in a feature class with ArcPy
'''

#import os
import time
import arcpy
from arcpy import env
import pprint
import os

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script start time is {}'.format(readable_start))

# Get list of feature classes in a geodatabase
database = r'C:\E911\StGeorgeDispatch_TEST\Bad_Geometries_TEST.gdb'
env.workspace = database
fclist = arcpy.ListFeatureClasses()
            
###############
#  Functions  #
###############

class EmptyTest(object):
    def __init__(self):
        # Create dictionaries for reporting that are instance attributes
        self.report = {}
        self.final_report = {}
        pass
    
    
    def sweep(self, lyr):
        empty_count = 0
        fields = ['OID@', 'Shape', 'SHAPE@']  # for point, polylines, or polygons
        with arcpy.da.SearchCursor(lyr, fields) as Scursor:
            print("Looping through rows in '{}' ...".format(lyr))
            for row in Scursor:
                bad_geom = False
                
                # Check if geometry object is null
                if row[2] is None:
                    print("     OID {} has null (None) geometry".format(row[0]))
                    bad_geom = True
                    self.report[row[0]] = {'problem':'null geometry', 'action':'delete'}
                    
                # Check shape centroid has a null coordinate
                elif row[1][0] == None or row[1][1] == None:
                    print("     OID {} has empty geometry".format(row[0]))
                    bad_geom = True
                    self.report[row[0]] = {'problem':'empty geometry', 'action':'delete or repair'}
                    
                if bad_geom == True:
                    empty_count += 1
        print("Total number of empty geometries: {}".format(empty_count))
        self.final_report = {'empties': self.report}
        
    
    def get_report(self):
#        pprint.pprint(self.final_report)
        return self.final_report
    
    
    def try_fix(self, lyr):
        if len(self.report) > 0:
            del_count = 0
            fields = ['OID@', 'Shape', 'SHAPE@']  # for point, polylines, or polygons
            query = 'OBJECTID IN ({})'.format(', '.join(str(d) for d in self.report))
            print(query)
            with arcpy.da.UpdateCursor(lyr, fields, query) as Ucursor:
                print("Looping through rows in '{}' ...".format(lyr))
                for row in Ucursor:
                    if row[0] in self.report:       # this is a redundant check that OID is in the dictionary
                        Ucursor.deleteRow()
                        del_count += 1
            print("Total number of rows deleted: {}".format(del_count))
        else:
            pass


##########################
#  Call Functions Below  #
##########################

if __name__ == '__main__':
    for fc in sorted(fclist):
        fc_path = os.path.join(database, fc)
        empty = EmptyTest()
        empty.sweep(fc_path)
        empty.get_report()
        empty.try_fix(fc_path)


print('Script shutting down ...')
# Stop timer and print end time in UTC
readable_end = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script end time is {}'.format(readable_end))
print('Time elapsed: {:.2f}s'.format(time.time() - start_time))