#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates <table_name> --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep empties <table_name> --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep invalids <table_name> --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]

Arguments:
  workspace   - path to workspace eg: `c:\\my.gdb`
  table_name  - name of feature class or table eg: `Roads`
  report_path - folder to save report to eg: `c:\\temp`
  backup_path - place to create a temp gdb and import original table

Examples:
  sweeper sweep empties thing --workspace c:\\data\\thing
'''
import os
import sys

from docopt import docopt

from . import backup, report
from .sweepers.duplicates import DuplicateTest
from .sweepers.empties import EmptyTest


def main():
    '''Main entry point for program. Parse arguments and pass to sweeper modules
    '''

    args = docopt(__doc__, version='1.0.0')

    #: backup input file before quality checks
    if args['--backup-to']:
        backup.backup_data(os.path.join(args['--workspace'], args['<table_name>']), args['--backup-to'])

    if args['duplicates']:
        #: do something
        print(args)
        # duplicates.find(args['--input'])
        sweeper = DuplicateTest(args['--workspace'], args['<table_name>'])
    elif args['invalids']:
        #: do something
        print(args)
    elif args['empties']:
        print(args)

        sweeper = EmptyTest(args['--workspace'], args['<table_name>'])

    report_data = sweeper.sweep()
    if args['--save-report']:
        report.save_report(report_data, 'empties', args['<table_name>'], args['<--save-report>'])
    else:
        report.print_report(report_data, 'empties', args['<table_name>'])

    if args['--try-fix']:
        sweeper.try_fix()


if __name__ == '__main__':
    sys.exit(main())
