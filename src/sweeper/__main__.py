#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates  --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep empties     --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep invalids    --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep addresses   --workspace=<workspace> --table-name=<table-name> --field-name=<field_name> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep metadata    --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep             --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]

Arguments:
  workspace     - path to workspace eg: `c:\\my.gdb`
  table_name    - name of feature class or table eg: `Roads` (needs to be fully qualified (eg: `SGID.Transportation.Roads`) for metadata sweeper)
  report_path   - folder to save report to eg: `c:\\temp`
  backup_path   - place to create a temp gdb and import original table
  field_name    - name of the field to check

Examples:
  sweeper sweep           --workspace=c:\\data\\thing --try-fix --save-report=c:\\temp --backup-to=c:\\temp\\backup.gdb
  sweeper sweep addresses --workspace=c:\\data\\thing --try-fix --save-report=c:\\temp --backup-to=c:\\temp\\backup.gdb --field-name=ADDRESS
'''
import os
import sys
import pkg_resources

from docopt import docopt

from . import backup, report, workspace_info
from .sweepers.duplicates import DuplicateTest
from .sweepers.empties import EmptyTest
from .sweepers.addresses import AddressTest
from .sweepers.metadata import MetadataTest


def main():
    '''Main entry point for program. Parse arguments and pass to sweeper modules.
    '''
    args = docopt(__doc__, version=pkg_resources.require('agrc-sweeper')[0].version)

    #: backup input file before quality checks
    if args['--backup-to']:
        backup.backup_data(args['--workspace'], args['--table-name'], args['--backup-to'])

    #: create a list to hold the instantiated objects.
    closet = []

    #: check what quality check to run.
    if args['duplicates']:
        closet.append(DuplicateTest(args['--workspace'], args['--table-name']))
    elif args['invalids']:
        pass
    elif args['empties']:
        closet.append(EmptyTest(args['--workspace'], args['--table-name']))
    elif args['addresses']:
        closet.append(AddressTest(args['--workspace'], args['--table-name'], args['--field-name']))
    elif args['metadata']:
        closet.append(MetadataTest(args['--workspace'], args['--table-name']))
    else:
        closet.append(DuplicateTest(args['--workspace'], args['--table-name']))
        closet.append(EmptyTest(args['--workspace'], args['--table-name']))
        closet.append(MetadataTest(args['--workspace'], args['--table-name']))

    reports = execute_sweepers(closet, args['--try-fix'])

    report.print_report(reports)

    if args['--save-report']:
        report.save_report(reports, args['--save-report'])


def execute_sweepers(closet, try_fix):
    '''
    orchestrate the sweeper calls.

    closet: array of sweepers.
    try_fix: bool whether to fix or not.
    '''

    feature_class_names = []
    reports = []

    def run_tool(tool):
        reports.append(tool.sweep())

        if try_fix:
            reports.append(tool.try_fix())

            #: run sweeper again to ensure all errors were fixed.
            reports.append(tool.sweep())

    print(f'running {len(closet)} sweepers. try fix: {try_fix}')
    for tool in closet:
        if tool.table_name:
            run_tool(tool)

            continue

        print('missing table, executing over workspace')

        #: get feature class names once
        if len(feature_class_names) == 0:
            feature_class_names = workspace_info.get_featureclasses(tool.workspace)

        #: explode sweeper class for each feature class
        for table_name in feature_class_names:
            new_tool = tool.clone(table_name)

            run_tool(new_tool)

    return reports


if __name__ == '__main__':
    sys.exit(main())
