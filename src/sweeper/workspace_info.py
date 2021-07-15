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
    '''
    workspace_path: full path to the change detection table.
    '''

    last_checked = read_last_check_date()
    print(f'Last date change detection was checked: {last_checked}')

    if last_checked is None:
        last_checked = datetime.date.today().strftime('%m/%d/%Y')
    else:
        last_checked = datetime.datetime.strptime(last_checked, '%m/%d/%Y')

    print(f'Last date change detection was checked: {last_checked}')

    # egdb = r'C:\Users\eneemann\AppData\Roaming\ESRI\ArcGISPro\Favorites\internal@SGID@internal.agrc.utah.gov.sde'
    # egdb = r'\\itwfpcap2\AGRC\sgid_to_agol\ConnectionFilesSGID\SGID_internal\SGID_agrc.sde'
    egdb = credentials.DB
    cd_table = credentials.CHANGE_DETECTION

    # egdb_conn = arcpy.ArcSDESQLExecute(server='sgid.agrc.utah.gov', database='SGID', user='USER', password='PASSWORD')
    egdb_conn = arcpy.ArcSDESQLExecute(egdb)
    # sql = f"SELECT table_name FROM {cd_table} WHERE last_modified >= '04/17/2021'"
    sql = f"SELECT table_name FROM {cd_table} WHERE last_modified = '07/14/2021'"
    # sql = f"SELECT table_name FROM {cd_table} WHERE last_modified >= '{last_checked}'"

    #: result will typically be a nested list
    result = egdb_conn.execute(sql)
    print(f'SQL execution result: {result}')
    print(f'Data type is: {type(result)}')

    #: handle cases where result is a string (single feature class) or not a list (None type)
    if isinstance(result, str):
        fc_list = []
        fc_list.append(result)
        fc_list = [item.split('.', 1)[1] for item in fc_list]
        print(f'fc_list is: {fc_list}')
        return fc_list
    elif not isinstance(result, list):
        fc_list = None
        return fc_list

    #: Flatten resulting list and strip off the leading 'sgid.' of each table name
    fc_list = [item for sublist in result for item in sublist]
    # print(fc_list)
    print(f'fc_list is: {fc_list}')
    fc_list = [item.split('.', 1)[1] for item in fc_list]
    # print(fc_list)
    print(f'fc_list is: {fc_list}')

    return fc_list