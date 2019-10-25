#!/usr/bin/env python
# * coding: utf8 *
'''
report.py
A module that contains the templates for the reports and functions to format data into the report
'''

import os
from datetime import datetime

def _generate_report(writer, reports):
    if len(reports) == 0:
        writer('No issues found!')

        return None

    #: loop through each report dict in the list of dicts
    for report in reports:
        writer(f'{report["title"]} Report for {report["feature_class"]}')
        issues_found = len(report['issues'])
        if issues_found == 0:
            writer('No issues found!')
            writer('---')

            continue

        writer(f'{issues_found} issues found')
        writer('  Issues found:')

        for oid in report['issues']:
            writer(f'    ObjectID {oid}')

        writer('\nSelect statement to view issues in ArcGIS:')
        statement = f'OBJECTID IN ({", ".join(report["issues"])})'

        writer(statement)

        writer('---')

def save_report(reports, save_directory):
    '''
    save_directory 
      - folder sweeper-run-{date}
        - feature class name-sweeper name-numberofissues.txt `Counties-Empties-5.txt`   `Counties-Empties-0.txt`
    '''
    report_directory = _create_report_directory(save_directory)

    for report in reports:
        file_name = _get_file_name(report)
        file_path = os.path.join(report_directory, file_name)

        with open(file_path, 'w') as textfile:
            def write_lines(text):
                textfile.writelines(f'{text}\n')

            _generate_report(write_lines, [report])

def print_report(reports):
    _generate_report(print, reports)

def _get_file_name(report):
    title = report['title'].replace(' ', '')
    
    return f'{report["feature_class"]}_{title}_{len(report["issues"])}.txt'

def _create_report_directory(parent_directory):
    now = datetime.now().strftime('%Y%m%d_%H%M')

    report_directory = os.path.join(parent_directory, f'sweeper_run_{now}')
    os.makedirs(report_directory)

    return report_directory
