#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates <input> [--verbose]
  sweeper sweep nulls <input> [--verbose]
  sweeper sweep invalids <input> [--verbose]

Arguments:
  input

Examples:
  sweeper sweep c:\data\thing
'''
import sys
from docopt import docopt
from . import duplicates, empties, invalids


def main():
    '''Main entry point for program. Parse arguments and pass to engine module
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
