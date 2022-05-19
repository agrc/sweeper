#!/usr/bin/env python
# * coding: utf8 *
'''
workspace_info.py
A module that gets information about the workspace, including a list of feature classes.
'''
import arcpy
import os
import datetime
from pathlib import Path
from . import credentials
import logging

log = logging.getLogger('sweeper')

#: A function to determine when change detection was last run
def read_last_check_date():
    last_checked = Path('./.last_checked')

    last_date_string = ''

    if last_checked.exists():
        with open(last_checked, 'r') as log_file:
            last_date_string = log_file.readline().strip()

    if last_date_string is None or len(last_date_string) < 1:
        return None

    return last_date_string


#: A function to update the last_checked file
def update_last_check_date():
    last_checked = Path('./.last_checked')

    if not last_checked.exists():
        last_checked.touch()

    with open(last_checked, 'w') as log_file:
        log_file.write(datetime.datetime.today().strftime('%Y-%m-%d'))


#: A function to generate and return a list of workspace feature classes.
def get_featureclasses(workspace_path):
    '''
    workspace_path: full path to the feature workspace.
    '''

    with arcpy.EnvManager(workspace=workspace_path):
        fc_list = []

        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []

        #: generate a list of feature classes showing their full path (Example: Directory/Workspace/Dataset/TableName)
        for ds in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                fc_list.append(fc)

        return fc_list


#: A function to return a list of feature classes based on the change detection table.
def get_change_detection():

    checked_date = read_last_check_date()

    if checked_date:
        checked_string = datetime.datetime.strptime(checked_date, '%Y-%m-%d')
    else:
        checked_string = datetime.date.today()

    last_checked = checked_string.strftime('%m/%d/%Y')
    log.info(f'Last date change detection was checked: {last_checked}')

    egdb = Path(credentials.DB)
    cd_table = credentials.CHANGE_DETECTION

    egdb_conn = arcpy.ArcSDESQLExecute(str(egdb))
    sql = f"SELECT table_name FROM {cd_table} WHERE last_modified >= '{last_checked}'"

    #: result will typically be a nested list
    result = egdb_conn.execute(sql)
    log.info(f'SQL execution result: {result}')

    #: handle cases where result is a string (single feature class) or not a list (None type)
    if isinstance(result, str):
        #: reset list to None if single table doesn't exist in Internal database
        if not arcpy.Exists(str(egdb / result)):
            fc_list = None
            return fc_list
        
        fc_list = []
        fc_list.append(result)
        fc_list = [item.split('.', 1)[1] for item in fc_list]
        log.info(f'fc_list is: {fc_list}')
        return fc_list
    
    elif not isinstance(result, list):
        fc_list = None
        return fc_list

    #: Flatten resulting list
    fc_list = [item for sublist in result for item in sublist]

    #: Remove tables that aren't in the Internal database (but were in the change detection table)
    for fc in fc_list:
        if not arcpy.Exists(str(egdb / fc)):
            fc_list.remove(fc)

    #: Strip off the leading 'sgid.' of each table name
    fc_list = [item.split('.', 1)[1] for item in fc_list]
    log.info(f'fc_list is: {fc_list}')

    return fc_list
