#!/usr/bin/env python
# * coding: utf8 *
'''
report.py
A module that contains the templates for the reports and functions to format data into the report
'''

import os
from datetime import datetime

def _print_items(report, key, writer):
    '''print out issues or fixes
    report: report dictionary
    key: 'issues' | 'fixes'
    writer: function
    '''
    try:
        items = report[key]
    except KeyError:
        return

    items_found = len(items)
    if items_found == 0:
        writer(r'No {key} found!')
        writer('---')

        return

    writer(f'{items_found} {key} found:')

    if type(items) == list:
        for oid in items:
            writer(f'    ObjectID {oid}')
    else:
        #: must be dict
        for oid in items:
            writer(f'    ObjectID {oid}: {items[oid]}')

    writer(f'\nSelect statement to view {key} in ArcGIS:')
    statement = f'OBJECTID IN ({", ".join([str(oid) for oid in items])})'

    writer(statement)

    writer('---')

def _generate_report(writer, reports):
    if len(reports) == 0:
        writer('No issues found!')

        return None

    #: loop through each report dict in the list of dicts
    for report in reports:
        writer(f'{report["title"]} Report for {report["feature_class"]}')

        _print_items(report, 'fixes', writer)
        _print_items(report, 'issues', writer)

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
