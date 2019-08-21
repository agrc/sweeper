# -*- coding: utf-8 -*-
'''
Created on Wed Jun 5 14:15:04 2019
@author: eneemann
Script to identify empty geometries in a feature class with open source tools
'''

import time
import fiona
# import os
# import geopandas as gpd

# Start timer and print start time in UTC
start_time = time.time()
readable_start = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script start time is {}'.format(readable_start))

# Get list of feature classes in a geodatabase
# database = r'C:\E911\Box Elder CO\BoxElder_Spillman_WGS84.gdb'
database = r'C:\E911\StGeorgeDispatch_TEST\Bad_Geometries_TEST.gdb'
fclist = fiona.listlayers(database)

###############
#  Functions  #
###############


def find_empty_geom(db, data):
    with fiona.open(db, layer=data) as lyr:
        print('working on {} feature class ...'.format(lyr.name,))

        if lyr.schema['geometry'] == ('Point' or 'MultiPoint'):
            del_count = 0
            print('{} geometry type is: {}, looping through features ...'.format(lyr.name, lyr.schema['geometry']))
            # Assign x and y min/max values from lyr bounds and use to verify each point
            xmin, ymin, xmax, ymax = lyr.bounds[0], lyr.bounds[1], lyr.bounds[2], lyr.bounds[3]

            for feature in lyr:
                geom = feature['geometry']
                if geom is None:
                    print('Geometry is invalid (null) for ID: {}'.format(feature['id']))
                    del_count += 1
                # Check for points with coordinates outside of lyr bounds, these are invalid
                elif geom['coordinates'][0] < xmin or geom['coordinates'][0] > xmax:
                    print('Geometry is invalid (outside of bounds) for ID: {}'.format(feature['id']))
                    del_count += 1
                elif geom['coordinates'][1] < ymin or geom['coordinates'][1] > ymax:
                    print('Geometry is invalid (outside of bounds) for ID: {}'.format(feature['id']))
                    del_count += 1

        elif lyr.schema['geometry'] in ['LineString', 'MultiLineString']:
            del_count = 0
            print('{} geometry type is: {}, looping through features ...'.format(lyr.name, lyr.schema['geometry']))
            # Loop through line features, find those with empty coordinate tuples
            for feature in lyr:
                geom = feature['geometry']
                if geom is None:
                    print('Geometry is invalid (null) for ID: {}'.format(feature['id']))
                    del_count += 1
                elif len(geom['coordinates'][0]) == 0:
                    print('Geometry is invalid (empty) for ID: {}'.format(feature['id']))
                    del_count += 1

        elif lyr.schema['geometry'] in ['Polygon', 'MultiPolygon']:
            del_count = 0
            print('{} geometry type is: {}, looping through features ...'.format(lyr.name, lyr.schema['geometry']))
            # Loop through polygon features, find those with empty coordinate tuples
            for feature in lyr:
                geom = feature['geometry']
                if geom is None:
                    print('Geometry is invalid (null) for ID: {}'.format(feature['id']))
                    del_count += 1
                elif len(geom['coordinates'][0]) == 0:
                    print('Geometry is invalid (empty) for ID: {}'.format(feature['id']))
                    del_count += 1

    print('number of feature deleted due to empty geometry: {}'.format(del_count))


##########################
#  Call Functions Below  #
##########################

if __name__ == '__main__':
    for fc in sorted(fclist):
        find_empty_geom(database, fc)

print('Script shutting down ...')
# Stop timer and print end time in UTC
readable_end = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
print('The script end time is {}'.format(readable_end))
print('Time elapsed: {:.2f}s'.format(time.time() - start_time))