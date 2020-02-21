#!/usr/bin/env python
# * coding: utf8 *
'''
addresses.py

A sweeper that works on address fields
'''

import arcpy
from ..address_parser import Address


class AddressTest():
    '''A class that validates address data
    '''
    def __init__(self, workspace, table_name, field_name):
        self.workspace = workspace
        self.table_name = table_name
        self.field_name = field_name
        self.oids_with_issues = []

    def sweep(self):
        '''Loop through all values and check addresses for problems returning a report
        '''
        report = {'title': 'Address Test', 'feature_class': self.table_name, 'issues': {}}
        required_street_address_parts = set(['address_number', 'street_name'])

        with arcpy.EnvManager(workspace=self.workspace):
            with arcpy.da.SearchCursor(self.table_name, ['OID@', self.field_name]) as search_cursor:
                for oid, address in search_cursor:
                    error_message = None
                    try:
                        parsed_address = Address(address)
                    except Exception as exception:
                        error_message = str(exception)

                    parts_found = set(parsed_address.__dict__)
                    missing_parts = required_street_address_parts - parts_found
                    if len(missing_parts) > 0 and 'po_box' not in parts_found:
                        error_message = f'missing address parts: {", ".join(missing_parts)}'

                    if error_message is not None:
                        report['issues'][oid] = error_message
                        self.oids_with_issues.append(oid)

        return report

    def try_fix(self):
        report = {'title': 'Address Try Fix', 'feature_class': self.table_name, 'issues': {}}

        with arcpy.EnvManager(workspace=self.workspace):
            describe = arcpy.da.Describe(self.table_name)
            where = f'{describe["OIDFieldName"]} IN ({", ".join([str(oid) for oid in self.oids_with_issues])})'
            with arcpy.da.UpdateCursor(self.table_name, ['OID@', self.field_name], where_clause=where) as update_cursor:
                for oid, address in update_cursor:
                    try:
                        parsed_address = Address(address)
                        update_cursor.updateRow((oid, parsed_address.normalized))
                        report['issues'][oid] = f'{address} -> {parsed_address.normalized}'
                    except Exception as exception:
                        report['issues'][oid] = str(exception)

        return report
