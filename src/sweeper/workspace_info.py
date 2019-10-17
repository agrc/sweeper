#!/usr/bin/env python
# * coding: utf8 *
'''
workspace_info.py
A module that gets information about the workspace, including a list of feature classes.
'''
import arcpy
import os


#: A function to generate and return a list of workspace feature classes.
def get_featureclasses(workspace_path):
    '''
    workspace_path: full path to the feature workspace.
    '''

    with arcpy.EnvManager(workspace=workspace_path):
        #arcpy.env.workspace = workspace_path
        fc_list = []

        datasets = arcpy.ListDatasets(feature_type='feature')
        datasets = [''] + datasets if datasets is not None else []

        #: generate a list of feature classes showing their full path (Example: Directory/Workspace/Dataset/TableName)
        for ds in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                fc_list.append(fc)

        return fc_list
