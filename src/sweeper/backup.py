#!/usr/bin/env python
# * coding: utf8 *
'''
backup.py
A module that creates a gdb if it doesn't exist and inserts a feature class
'''
import arcpy 

def backup_data(source_data, out_path):
    # if the gdb does not exist, then create it
    if not arcpy.Exists(out_path):
        out_dir = out_path.rsplit('\\', 1)[0]
        gdb_name = out_path.rsplit('\\', 1)[1]
        arcpy.CreateFileGDB_management(out_dir, gdb_name)
    
    # get source_data feature class name
    fc_name = source_data.rsplit('\\',1)[1]

    # backup the source feature class
    arcpy.Copy_management(source_data, out_path + '\\' + fc_name)


