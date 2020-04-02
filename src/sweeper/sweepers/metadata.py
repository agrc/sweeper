#!/usr/bin/env python
# * coding: utf8 *
'''
metadata.py
A sweeper that checks geodatabase metadata
'''
from os.path import join

from arcpy import metadata as md
from arcpy import EnvManager, ListFeatureClasses, ListTables


class MetadataTest():
    '''A class that validates geodatabase metadata
    '''
    def __init__(self, workspace, table_name):
        self.workspace = workspace
        self.table_name = table_name

    def sweep(self):
        report = {'title': 'Metadata Test', 'workspace': self.workspace, 'feature_class': self.table_name, 'issues': []}

        metadata = md.Metadata(join(self.workspace, self.table_name))

        name_parts = self.table_name.split('.')

        #: check for required tags
        required_tags = []
        if len(name_parts) == 3:
            [database, schema, feature_class_name] = name_parts
            required_tags.append(database)
            required_tags.append(schema.title())
        if metadata.tags is None:
            missing_tags = required_tags
        else:
            tags = [tag.strip() for tag in metadata.tags.split(',')]
            missing_tags = set(required_tags) - set(tags)

        if len(missing_tags):
            report['issues'].append(f'missing tags: {required_tags}')

        return report

    def try_fix(self):
        pass

    def clone(self, table_name):
        print(f'cloning to {table_name}')
        return MetadataTest(self.workspace, table_name)
