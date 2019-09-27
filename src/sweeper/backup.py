#!/usr/bin/env python
# * coding: utf8 *
'''
backup.py
A module that creates a gdb if it doesn't exist and inserts a feature class
'''
import os
from datetime import datetime

import arcpy


def backup_data(source_data, out_path):
    '''
    source_data: full path to the feature class to be backed up.
    out_path: a geodatabase path where the feature class will be stored.
    '''
    now = datetime.now().strftime('%Y%m%d_%H%M')

    #: check if the db exists
    if not arcpy.Exists(out_path):
        #: if db does not exist, then create it
        out_dir = out_path.rsplit('\\', 1)[0]
        gdb_name=out_path.rsplit('\\', 1)[1]

        arcpy.management.CreateFileGDB(out_dir, gdb_name)

    #: get source_data feature class name
    fc_name = source_data.rsplit('\\', 1)[1] + '_' + now

    #: backup the source feature class
    arcpy.management.Copy(source_data, os.path.join(out_path, fc_name))
