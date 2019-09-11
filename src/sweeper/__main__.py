#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates <table_name> --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep empties <table_name> --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep invalids <table_name> --workspace=<workspace> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]

Arguments:
  workspace   - path to feature class eg: `c:\\my.gdb`
  table_name  - name of feature class or table eg: `Roads`
  report_path - folder to save report to eg: `c:\\temp`
  backup_path - place to create a temp gdb and import original table

Examples:
  sweeper sweep empties thing --workspace c:\data\thing
'''
import sys
from docopt import docopt


def main():
    '''Main entry point for program. Parse arguments and pass to sweeper modules
    '''

    args = docopt(__doc__, version='1.0.0')

    if args['duplicates']:
        #: do something
        print(args)
        # duplicates.find(args['--input'])
    elif args['invalids']:
        #: do something
        print(args)
    elif args['nulls']:
        #: do something
        print(args)


if __name__ == '__main__':
    sys.exit(main())
