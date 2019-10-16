#!/usr/bin/env python
# * coding: utf8 *
'''
report.py
A module that contains the templates for the reports and functions to format data into the report
'''

import os
from datetime import datetime


def save_report(data_dict, title, fc, path):
    now = datetime.now().strftime('%Y%m%d_%H%M')
    name = f'{fc}_{len(data_dict)}_{title}_{now}.txt'

    filename = os.path.join(path, name)

    with open(filename, 'w') as textfile:
        textfile.write(f"{title.title()} Report for '{fc}' \n \n")

        if len(data_dict) == 0:
            textfile.write('No issues found!')

            return filename

        lines = []
        textfile.write(f'{len(data_dict)} issues found in feature class \n \n')
        textfile.write('Issues found: \n')

        for key, value in data_dict.items():
            lines.append(f'ObjectID {key}: {value} \n')

        textfile.writelines(lines)
        textfile.write('\n')
        textfile.write('Select statement to view issues in ArcGIS: \n')

        statement = f'OBJECTID IN ({",".join(str(key) for key in data_dict)})'

        textfile.write(statement)

        return filename

def print_report(data_dict, title, fc):
    report = f"{title.title()} Report for '{fc}' \n"

    if len(data_dict) == 0:
        report += 'No issues found! \n'
        print(report)

        return report

    report += f'{len(data_dict)} issues found in feature class \n'
    report += 'Issues found: \n'

    for key, value in data_dict.items():
        report += f'ObjectID {key}: {value} \n'

    report += 'Select statement to view issues in ArcGIS: \n'
    statement = f'OBJECTID IN ({",".join(str(key) for key in data_dict)}) \n'

    report += statement

    print(report)

    return report
