#!/usr/bin/env python
# * coding: utf8 *
'''
report.py
A module that contains the templates for the reports and functions to format data into the report
'''

def save_report(data_dict, title, fc, path):
    import os
    from datetime import datetime
    
    now = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    name = f'{title}_report_{now}.txt'
    filename = os.path.join(path, name)
    if len(data_dict) > 0:
        lines = []
        with open(filename, 'w') as file:
            file.write(f"{title.title()} Report for '{fc}' \n \n")
            file.write(f'{len(data_dict)} empty geometries found in feature class \n \n')
            file.write('Issues found: \n')
            for k,v in data_dict.items():
                lines.append(f'ObjectID {k}: {v} \n')
            file.writelines(lines)
            file.write('\n')
            file.write('Select statement to view issues in ArcGIS: \n')
            statement = 'OBJECTID IN ({})'.format(','.join(str(key) for key in data_dict))
            file.write(statement)
    else:
        with open(filename, 'w') as file:
            file.write(f"{title.title()} Report for '{fc}' \n \n")
            file.write('No empty geometries found!')
            
def print_report(data_dict, title, fc):
    if len(data_dict) > 0:
        print(f"{title.title()} Report for '{fc}' \n")
        print(f'{len(data_dict)} empty geometries found in feature class \n')
        print('Issues found:')
        for k,v in data_dict.items():
            print(f'ObjectID {k}: {v}')
        print('\nSelect statement to view issues in ArcGIS:')
        statement = 'OBJECTID IN ({}) \n'.format(','.join(str(key) for key in data_dict))
        print(statement)
    else:
        print(f"{title.title()} Report for '{fc}' \n")
        print('No empty geometries found! \n')
