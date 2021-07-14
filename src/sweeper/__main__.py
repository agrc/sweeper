#!/usr/bin/env python
# * coding: utf8 *
'''
sweeper

Usage:
  sweeper sweep duplicates  --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --change-detect --scheduled --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep empties     --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --change-detect --scheduled --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep invalids    --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --change-detect --scheduled --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep addresses   --workspace=<workspace> --table-name=<table-name> --field-name=<field_name> [--verbose --try-fix --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep metadata    --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --change-detect --scheduled --save-report=<report_path> --backup-to=<backup_path>]
  sweeper sweep             --workspace=<workspace> [--table-name=<table_name> --verbose --try-fix --change-detect --scheduled --save-report=<report_path> --backup-to=<backup_path>]

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
import datetime
import logging
import pkg_resources
from io import StringIO

from docopt import docopt

from supervisor.models import MessageDetails, Supervisor
from supervisor.message_handlers import EmailHandler

from . import backup, report, workspace_info, credentials
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

    # if args['--scheduled']:
    #     #: set up supervisor, add email handler
    #     sweeper_supervisor = Supervisor(
    #         project_name='sweeper', logger=summary_logger, log_path=credentials.REPORT_BASE_PATH
    #     )
    #     sweeper_supervisor.add_message_handler(EmailHandler(credentials.EMAIL_SETTINGS))

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

    reports = execute_sweepers(closet, args['--try-fix'], args['--change-detect'])

    report.print_report(reports)

    if args['--save-report']:
        report.save_report(reports, args['--save-report'])

    if args['--scheduled']:
        final_message = report.format_message(reports)
        print(final_message.getvalue())
        
        # #: Build and send summary message
        # summary_message = MessageDetails()
        # summary_message.message = final_message.getvalue()
        # summary_message.project_name = 'sweeper'
        # summary_message.attachments = [credentials.REPORT_BASE_PATH]
        # summary_message.subject = f'Sweeper Report {datetime.datetime.today()}'

        # sweeper_supervisor.notify(summary_message)


        # if args['--scheduled']:
        #     # invoke supervisor, compile summary report, send via email

        #     #: Logger that will gather the summary information.
        #     summary_logger = logging.getLogger(__name__)
        #     summary_logger.setLevel(logging.DEBUG)
            
        #     #: Create a string stream for summary report
        #     summary_stream = StringIO()
        #     summary_handler = logging.StreamHandler(stream=summary_stream)
        #     stream_formatter = logging.Formatter(
        #         fmt='<pre>%(levelname)-7s %(asctime)s %(module)10s:%(lineno)5s %(message)s</pre>',
        #         datefmt='%m-%d %H:%M:%S'
        #     )
        #     summary_handler.setFormatter(stream_formatter)
        #     summary_logger.addHandler(summary_handler)

        #     now = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        #     report_dir = os.path.join(args['--save-report'], f'sweeper_run_{now}')

        #     #: set up supervisor, add email handler
        #     sweeper_supervisor = Supervisor(
        #         project_name='sweeper', logger=summary_logger, log_path=credentials.REPORT_BASE_PATH
        #     )
        #     sweeper_supervisor.add_message_handler(EmailHandler(credentials.EMAIL_SETTINGS))

        #     #: Build and send summary message
        #     summary_message = MessageDetails()
        #     summary_message.message = summary_stream.getvalue()
        #     summary_message.project_name = 'sweeper'
        #     summary_message.attachments = [credentials.REPORT_BASE_PATH]
        #     summary_message.subject = f'Sweeper Report {datetime.datetime.today()}'

        #     sweeper_supervisor.notify(summary_message)



def execute_sweepers(closet, try_fix, change_detect):
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

        #: get feature class names once
        if len(feature_class_names) == 0:
            if change_detect:
                print('Getting table names from change detection table')
                feature_class_names = workspace_info.get_change_detection()
            else:
                print('Missing table name, executing over workspace')
                feature_class_names = workspace_info.get_featureclasses(tool.workspace)
                if any('SGID.' in fc for fc in feature_class_names):
                    feature_class_names = [fc.split('SGID.', 1)[1] for fc in feature_class_names if 'SGID.' in fc]

        print(f'feature_class_names is: {feature_class_names}')

        if change_detect and feature_class_names is None:
            #: reset variable to empty list
            print('Change detection found no updated tables')
            feature_class_names = []

            continue

        #: explode sweeper class for each feature class
        for table_name in feature_class_names:
            new_tool = tool.clone(table_name)

            run_tool(new_tool)

    return reports


if __name__ == '__main__':
    sys.exit(main())
