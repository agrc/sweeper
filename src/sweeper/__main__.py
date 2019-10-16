#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]
  sweeper sweep empties --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]
  sweeper sweep invalids --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]
  sweeper sweep all-checks --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path> --table-name=<table_name>]  

Arguments:
  workspace - path to workspace eg: `c:\\my.gdb`
  table_name - name of feature class or table eg: `Roads`
  report_path - folder to save report to eg: `c:\\temp`
  backup_path - place to create a temp gdb and import original table

Examples:
  sweeper sweep all-checks --workspace=c:\\data\\thing --save-report=c:\\temp --try-fix --backup-to=c:\\temp
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

    #: backup input file before quality checks
    if args['--backup-to']:
        backup.backup_data(os.path.join(args['--workspace'], args['--table-name']), args['--backup-to'])

    #: check what quality check to run.
    if args['duplicates']:
        call_sweeper(args, "DuplicateTest")
    elif args['invalids']:
        call_sweeper(args, "InvalidsTest")
    elif args['empties']:
        call_sweeper(args, "EmptyTest")
    elif args['all-checks']:
        call_sweeper(args, "DuplicateTest")
        call_sweeper(args, "EmptyTest")


def call_sweeper(args, sweeper_test):
    '''
    orchestrate the sweeper calls.

    args: the docopt arguments.
    sweeper_test: the name of the sweeper function to call.
    '''
    print(args)

    #: if table name was provided, then run quality check on single table.
    if args['--table-name']:
        #: call the quality check.
        if sweeper_test == "DuplicateTest":
            sweeper = DuplicateTest(args['--workspace'], args['--table-name'])
            save_report(args, sweeper, args['--table-name'], 'duplicates')
        elif sweeper_test == "EmptyTest":
            sweeper = EmptyTest(args['--workspace'], args['--table-name']) 
            save_report(args, sweeper, args['--table-name'], 'empties')
        #: attempt to fix flagged items.
        if args['--try-fix']:
            sweeper.try_fix()
    #: if table name was not provided, then run quality check on all tables in the workpace.
    else:
        #: get a list of feature classes that are contained in the workspace.
        featureclasses = workspace_info.get_featureclasses(args['--workspace'])
        for fc in featureclasses:
            print(fc)
            #: call the quality check.
            if sweeper_test == "DuplicateTest":
                sweeper = DuplicateTest(args['--workspace'], fc)
                save_report(args, sweeper, fc, 'duplicates')
            elif sweeper_test == "EmptyTest":
                sweeper = EmptyTest(args['--workspace'], fc)
                save_report(args, sweeper, fc, 'empties')
            #: attempt to fix flagged items.
            if args['--try-fix']:
                sweeper.try_fix()


def save_report(args, sweeper, table_name, quality_check):
    '''
    save the quality check report or print it to console.

    args: the docopt arguments.
    sweeper: the sweeper variable returned from the class.
    table_name: the name of the feature class table.
    quality_check: the name of the quality check (example: 'duplicates', 'empties').
    '''

    report_data = sweeper.sweep()
    if args['--save-report']:
        report.save_report(report_data, quality_check, table_name, args['--save-report'])
    else:
        report.print_report(report_data, quality_check, table_name)


if __name__ == '__main__':
    sys.exit(main())
