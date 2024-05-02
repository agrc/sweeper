#!/usr/bin/env python
# * coding: utf8 *
"""
backup.py
A module that creates a gdb if it doesn't exist and inserts a feature class
"""

import logging
import os
from datetime import datetime

import arcpy

from . import workspace_info

log = logging.getLogger("sweeper")


def backup_data(workspace_path, table_name, out_path):
    """
    workspace_path: the full path to the workspace or geodatabase containing the tables to be backed up.
    table_name: the table name to be backed up - if it was provided to the CLI.
    out_path: a geodatabase path where the feature class will be stored.
    """
    now = datetime.now().strftime("%Y%m%d_%H%M")

    #: check if the db exists
    if not arcpy.Exists(out_path):
        #: if db does not exist, then create it
        out_dir = out_path.rsplit("\\", 1)[0]
        gdb_name = out_path.rsplit("\\", 1)[1]

        arcpy.management.CreateFileGDB(out_dir, gdb_name)

    tables_to_backup = []

    #: populate the list with feature class name(s) to backup
    if table_name:  #: table name was provided.
        tables_to_backup.append(table_name)
    else:  #: table name was not provided, use all tables in workspace.
        #: get a list of feature class names that are contained in the provided workspace
        feature_class_names = workspace_info.get_featureclasses(workspace_path)
        for feature_class in feature_class_names:
            tables_to_backup.append(feature_class)

    #: loop through the list and backup each feature class
    for table in tables_to_backup:
        full_table_path = os.path.join(workspace_path, table)
        fc_name = full_table_path.rsplit("\\", 1)[1] + "_" + now

        #: backup the source feature class
        arcpy.management.Copy(full_table_path, os.path.join(out_path, fc_name))

    log.info("The following feature classes were backed up here", out_path, ":", str(tables_to_backup))
