#!/usr/bin/env python
# * coding: utf8 *
"""
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
"""

import datetime
import logging
import logging.handlers
import sys
from pathlib import Path

import pkg_resources
from docopt import docopt
from supervisor.message_handlers import SendGridHandler
from supervisor.models import MessageDetails, Supervisor

from . import backup, config, report, utilities, workspace_info
from .sweepers.addresses import AddressTest
from .sweepers.duplicates import DuplicateTest
from .sweepers.empties import EmptyTest
from .sweepers.metadata import MetadataTest


def main():
    """Main entry point for program. Parse arguments and pass to sweeper modules."""
    args = docopt(__doc__, version=pkg_resources.require("ugrc-sweeper")[0].version)

    log = setup_logging(args["--save-report"], args["--scheduled"])

    if args["--scheduled"]:
        #: set up supervisor, add email handler
        sweeper_supervisor = Supervisor()
        sweeper_supervisor.add_message_handler(
            SendGridHandler(
                {
                    "from_address": "noreply@utah.gov",
                    "to_addresses": config.get_config("TO_ADDRESSES"),
                    "api_key": config.get_config("SENDGRID_API_KEY"),
                },
                client_name="ugrc-sweeper",
                client_version=pkg_resources.require("ugrc-sweeper")[0].version,
            )
        )

    #: backup input file before quality checks
    if args["--backup-to"]:
        backup.backup_data(args["--workspace"], args["--table-name"], args["--backup-to"])

    #: create a list to hold the instantiated objects.
    closet = []

    #: check what quality check to run.
    if args["duplicates"]:
        closet.append(DuplicateTest(args["--workspace"], args["--table-name"]))
    elif args["invalids"]:
        raise NotImplementedError('"Invalids" sweep/check not implemented yet.')
    elif args["empties"]:
        closet.append(EmptyTest(args["--workspace"], args["--table-name"]))
    elif args["addresses"]:
        closet.append(AddressTest(args["--workspace"], args["--table-name"], args["--field-name"]))
    elif args["metadata"]:
        closet.append(MetadataTest(args["--workspace"], args["--table-name"]))
    else:
        closet.append(DuplicateTest(args["--workspace"], args["--table-name"]))
        closet.append(EmptyTest(args["--workspace"], args["--table-name"]))
        closet.append(MetadataTest(args["--workspace"], args["--table-name"]))

    reports = execute_sweepers(closet, args["--try-fix"], args["--change-detect"], log)

    report.print_report(reports)

    if args["--save-report"]:
        report.save_report(reports, args["--save-report"])

    if args["--scheduled"]:
        report.add_to_log(reports)

        final_message = report.format_message(reports)
        log.info(final_message.getvalue())

        #: Build and send summary message
        summary_message = MessageDetails()
        summary_message.message = final_message.getvalue()
        summary_message.attachments = [config.LOG_FILE_PATH]
        summary_message.subject = f"Sweeper Report {datetime.datetime.today()}"

        sweeper_supervisor.notify(summary_message)


def execute_sweepers(closet, try_fix, using_change_detection, log):
    """
    orchestrate the sweeper calls.

    closet: array of sweepers.
    try_fix: bool whether to fix or not.
    """

    feature_class_names = []
    reports = []

    def run_tool(tool):
        reports.append(tool.sweep())

        if try_fix:
            reports.append(tool.try_fix())

            #: run sweeper again to ensure all errors were fixed.
            reports.append(tool.sweep())

    log.info(f"running {len(closet)} sweepers. try fix: {try_fix}")
    for tool in closet:
        log.info(f"running sweeper: {tool.key}")
        if tool.table_name:
            run_tool(tool)

            continue

        #: get feature class names once
        if len(feature_class_names) == 0:
            if using_change_detection:
                log.info("Getting table names from change detection table")
                feature_class_names = workspace_info.get_change_detection()
            else:
                log.info("Missing table name, executing over workspace")
                feature_class_names = workspace_info.get_featureclasses(tool.workspace)
                if any("SGID." in fc for fc in feature_class_names):
                    feature_class_names = [fc.split("SGID.", 1)[1] for fc in feature_class_names if "SGID." in fc]

            #: apply exclusions
            if config.has_config():
                try:
                    exclusions_config = config.get_config("EXCLUSIONS")
                except KeyError:
                    exclusions_config = {}

                exclusions = exclusions_config.get(tool.key, [])
            feature_class_names = utilities.apply_exclusions(feature_class_names, exclusions)

        log.info(f"feature_class_names is: {feature_class_names}")

        if using_change_detection and feature_class_names is None:
            #: reset variable to empty list
            log.info("Change detection found no updated tables")
            feature_class_names = []

            continue

        #: explode sweeper class for each feature class
        for table_name in feature_class_names:
            new_tool = tool.clone(table_name, tool.workspace)

            run_tool(new_tool)

    if using_change_detection:
        workspace_info.update_last_check_date()

    return reports


def setup_logging(save_report, scheduled):
    logger = logging.getLogger("sweeper")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(levelname)-7s %(asctime)s %(module)10s:%(lineno)5s %(message)s", datefmt="%m-%d %H:%M:%S"
    )

    #: always set up console_handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)

    #: use log file when report location not provided and when running from scheduled task
    if scheduled and not save_report:
        log_file = Path(config.LOG_FILE_PATH)
        file_handler = logging.handlers.RotatingFileHandler(log_file, backupCount=10)
        file_handler.doRollover()
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    sys.exit(main())
