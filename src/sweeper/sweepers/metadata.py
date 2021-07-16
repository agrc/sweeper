#!/usr/bin/env python
# * coding: utf8 *
'''
metadata.py
A sweeper that checks geodatabase metadata
'''
import re
from os.path import dirname, join, realpath
from . import credentials

from arcpy import Exists
from arcpy import metadata as md
from bs4 import BeautifulSoup

#: these constants were copied from https://github.com/agrc/agol-validator/blob/master/validate.py
#: Tags or words that should be uppercased, saved as lower to check against
UPPERCASED_TAGS = ['2g', '3g', '4g', 'agol', 'agrc', 'aog', 'at&t', 'blm', 'brat', 'caf', 'cdl', 'daq', 'dfcm', 'dfirm', 'dnr', 'dsl', 'dwq', 'e911', 'ems', 'fae', 'fcc', 'fema', 'gcdb', 'gis', 'gnis', 'hava', 'huc', 'lir', 'lrs', 'lte', 'luca', 'mrrc', 'nca', 'ng911', 'nox', 'npsbn', 'ntia', 'nwi', 'nws', 'plss', 'pm10', 'psap', 'sao', 'sbdc', 'sbi', 'sgid', 'sitla', 'sligp', 'trax', 'uca', 'udot', 'ugrc', 'ugs', 'uhp', 'uic', 'us', 'usao', 'usdw', 'usfs', 'usfws', 'usps', 'ustc', 'ut', 'uta', 'vcp', 'vista', 'voc']
#: Articles that should be left lowercase.
ARTICLES = ['a', 'the', 'of', 'is', 'in']

DATA_PAGE_LINK_REGEX = re.compile(r'gis\.utah\.gov.*\/data', re.IGNORECASE)

with open(join(dirname(realpath(__file__)), 'UseLimitations.html')) as file:
    STANDARD_LIMITATIONS = re.sub(r'\s\s+', '', file.read()).replace('\n', '')

#: copied from https://github.com/agrc/agol-validator/blob/master/checks.py with minor modifications
def title_case_tag(tag):
    '''
    Changes a tag to the correct title case while also removing any periods:
    'U.S. bureau Of Geoinformation' -> 'US Bureau of Geoinformation'. Should
    properly upper-case any words or single tags that are acronyms:
    'agrc' -> 'AGRC', 'Plss Fabric' -> 'PLSS Fabric'. Any words separated by
    a hyphen will also be title-cased: 'water-related' -> 'Water-Related'.
    Note: No check is done for articles at the begining of a tag; all articles
    will be lowercased.
    tag:        The single or multi-word tag to check
    '''

    new_words = []
    for word in tag.split():
        cleaned_word = word.replace('.', '').lower()

        #: Upper case specified words:
        if cleaned_word.lower() in UPPERCASED_TAGS:
            new_words.append(cleaned_word.upper())
        #: Lower case articles/conjunctions
        elif cleaned_word.lower() in ARTICLES:
            new_words.append(cleaned_word.lower())
        #: Title case everything else
        else:
            new_words.append(cleaned_word.title())

    return ' '.join(new_words)


def get_tags_from_string(text):
    if text is None:
        return []

    return [tag.strip() for tag in text.split(',')]


def update_tags(existing, tags_to_remove, tags_to_add):
    new_tags = [existing_tag for existing_tag in existing if existing_tag not in tags_to_remove]

    return new_tags + tags_to_add


def get_description_text_only(html):
    soup = BeautifulSoup(html or '', 'html5lib')

    return soup.get_text()


class MetadataTest():
    '''A class that validates geodatabase metadata
    '''
    def __init__(self, workspace, table_name):
        self.workspace = workspace
        self.table_name = table_name
        self.tags_to_add = []
        self.tags_to_remove = []
        self.use_limitations_needs_update = False

    def sweep(self):
        print(f'Sweep Workspace is:   {self.workspace}')
        report = {'title': 'Metadata Test', 'workspace': self.workspace, 'feature_class': self.table_name, 'issues': []}

        table_path = join(self.workspace, self.table_name)

        if not Exists(table_path):
            raise Exception(f'dataset does not exist! {table_path}')
        metadata = md.Metadata(table_path)

        name_parts = self.table_name.split('.')

        #: check for required tags
        required_tags = []
        #: case where 'SGID.' is in table_name
        if len(name_parts) == 3:
            [database, schema, feature_class_name] = name_parts
            required_tags.append(database)
            required_tags.append(schema.title())
        #: case where 'SGID.' is not in table_name
        elif len(name_parts) == 2:
            database = 'SGID'
            [schema, feature_class_name] = name_parts
            required_tags.append(database)
            required_tags.append(schema.title())

        if metadata.tags is None:
            missing_tags = required_tags
        else:
            tags = get_tags_from_string(metadata.tags)
            missing_tags = set(required_tags) - set(tags)

        if len(missing_tags):
            report['issues'].append(f'missing tags: {missing_tags}')
            self.tags_to_add = list(missing_tags)

        if metadata.tags is not None:
            #: check casing for existing tags
            for tag in tags:
                formatted_tag = title_case_tag(tag)
                if tag != formatted_tag:
                    report['issues'].append(f'incorrectly cased tag: {tag} (should be: {formatted_tag})')
                    self.tags_to_remove.append(tag)
                    self.tags_to_add.append(formatted_tag)

        #: check summary
        if metadata.summary is not None:
            if len(metadata.summary) > 2048:
                report['issues'].append('Summary is longer than 2048 characters.')
            description_text = get_description_text_only(metadata.description)
            if len(metadata.summary) > len(description_text):
                report['issues'].append('Summary is longer than Description!')

        #: check description for data page link
        if metadata.description is not None:
            if not DATA_PAGE_LINK_REGEX.search(metadata.description):
                report['issues'].append('Description is missing link to gis.utah.gov data page.')

        #: check use limitations
        if metadata.accessConstraints is None or metadata.accessConstraints == '':
            report['issues'].append('Use limitations text is missing.')
            self.use_limitations_needs_update = True
        elif metadata.accessConstraints != STANDARD_LIMITATIONS:
            report['issues'].append('Use limitations text is not standard.')
            self.use_limitations_needs_update = True

        return report

    def try_fix(self):
        print(f'Try Fix Workspace is:   {self.workspace}')
        report = {'title': 'Metadata Try Fix', 'feature_class': self.table_name, 'issues': [], 'fixes': []}

        #: commented out these lines, they were preventing fixes to limitations text when tags were good
        # if len(self.tags_to_add) == 0 and len(self.tags_to_remove) == 0:
        #     return report

        metadata = md.Metadata(join(self.workspace, self.table_name))

        try:
            metadata.tags = ', '.join(update_tags(get_tags_from_string(metadata.tags), self.tags_to_remove, self.tags_to_add))

            if len(self.tags_to_remove) > 0:
                report['fixes'].append(f'Tags removed: {self.tags_to_remove}')

            if len(self.tags_to_add) > 0:
                report['fixes'].append(f'Tags added: {self.tags_to_add}')

            metadata.save()
        except Exception as error:
            report['issues'].append(f'Error updating tags: {error}!')

        if self.use_limitations_needs_update:
            try:
                metadata.accessConstraints = STANDARD_LIMITATIONS

                report['fixes'].append('Standard use limitations text applied.')

                metadata.save()
            except Exception as error:
                report['issues'].append(f'Error updating use limitations: {error}!')

        return report

    def clone(self, table_name):
        print(f'cloning to {table_name}')
        user = table_name.split('.')[0].upper()
        user_workspace = credentials.CONNECTIONS[user]
        return MetadataTest(user_workspace, table_name)
