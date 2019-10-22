#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]
  sweeper sweep empties --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]
  sweeper sweep invalids --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]
  sweeper sweep --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]  

Arguments:
  workspace - path to workspace eg: `c:\\my.gdb`
  table_name - name of feature class or table eg: `Roads`
  report_path - folder to save report to eg: `c:\\temp`
  backup_path - place to create a temp gdb and import original table

Examples:
  sweeper sweep --workspace=c:\\data\\thing --try-fix --save-report=c:\\temp --backup-to=c:\\temp\\backup.gdb
'''
import os
import sys

from docopt import docopt

from . import backup, report, workspace_info
from .sweepers.duplicates import DuplicateTest
from .sweepers.empties import EmptyTest


def main():
    '''Main entry point for program. Parse arguments and pass to sweeper modules.
    '''
    args = docopt(__doc__, version='1.0.0')
    print(args)
    
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
    else:
        closet.append(DuplicateTest(args['--workspace'], args['--table-name']))
        closet.append(EmptyTest(args['--workspace'], args['--table-name']))

    reports = execute_sweepers(closet, args['--try-fix'])

    report.print_report(reports)

    if (args['--save-report']):
        report.save_report(reports, args['--save-report'])


def execute_sweepers(closet, try_fix):
    '''
    orchestrate the sweeper calls.

    closet: array of sweepers.
    try_fix: bool whether to fix or not.
    '''

    feature_class_names = []
    reports = []

    print(f'running {len(closet)} sweepers. try fix: {try_fix}')
    for tool in closet:
        if tool.table_name:
            report = tool.sweep()

            reports.append(report)

            if try_fix:
                tool.try_fix()

            continue

        print('missing table, executing over workspace')
        #: get all feature classes
        #: explode current tool to match the numbner of feature classes
        #: execute sweep on new exploded tools

        #: get feature class names once
        if len(feature_class_names) == 0:
            feature_class_names = workspace_info.get_featureclasses(tool.workspace)
        
        #: explode sweeper class for each feature class
        for table_name in feature_class_names:
            new_tool = tool.clone(table_name)
            report = new_tool.sweep()

            reports.append(report)

            if try_fix:
                tool.try_fix()

    return reports


if __name__ == '__main__':
    sys.exit(main())