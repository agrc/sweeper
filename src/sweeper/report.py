#!/usr/bin/env python
# * coding: utf8 *
"""
report.py
A module that contains the templates for the reports and functions to format data into the report
"""

import os
import io
from datetime import datetime
import logging

log = logging.getLogger("sweeper")


def _print_items(report, key, writer):
    """print out issues or fixes
    report: report dictionary
    key: 'issues' | 'fixes'
    writer: function
    """
    try:
        items = report[key]
    except KeyError:
        return

    items_found = len(items)
    if items_found == 0:
        writer(f"No {key} found!")
        writer("---")

        return

    writer(f"{items_found} {key} found:")

    has_oids = True
    if isinstance(items, list):
        for item in items:
            if isinstance(item, int):
                writer(f"    ObjectID {item}")
            else:
                #: issues not associated with a specific row (e.g. metadata)
                has_oids = False
                writer(f"    {item}")
    else:
        #: must be dict
        for oid in items:
            writer(f"    ObjectID {oid}: {items[oid]}")

    if has_oids:
        writer(f"\nSelect statement to view {key} in ArcGIS:")
        statement = f'OBJECTID IN ({", ".join([str(oid) for oid in items])})'

        writer(statement)

    writer("---")


def _generate_report(writer, reports):
    if len(reports) == 0:
        writer("No issues found!")

        return None

    #: loop through each report dict in the list of dicts
    for report in reports:
        writer(f'{report["title"]} Report for {report["feature_class"]}')

        _print_items(report, "fixes", writer)
        _print_items(report, "issues", writer)


def save_report(reports, save_directory):
    """
    save_directory
      - folder sweeper_run_YYYYMMDD_HHmm
        - featureclassname_sweepername_numberofissues.txt `Counties_Empties_5.txt`   `Counties_Empties_0.txt`
    """
    report_directory = _create_report_directory(save_directory)

    for report in reports:
        file_name = _get_file_name(report)
        file_path = os.path.join(report_directory, file_name)

        with open(file_path, "w") as textfile:

            def write_lines(text):
                textfile.writelines(f"{text}\n")

            _generate_report(write_lines, [report])


def print_report(reports):
    _generate_report(print, reports)


def _get_file_name(report):
    title = report["title"].replace(" ", "")

    return f'{report["feature_class"]}_{title}_{len(report["issues"])}.txt'


def _create_report_directory(parent_directory):
    now = datetime.now().strftime("%Y%m%d_%H%M")

    report_directory = os.path.join(parent_directory, f"sweeper_run_{now}")
    os.makedirs(report_directory)

    return report_directory


def format_message(reports):
    message = io.StringIO()
    now = datetime.now().strftime("%Y%m%d_%H%M")
    message.write(f"<pre>Email summary for {now} Sweeper run \n\n</pre>")

    if not reports:
        message.write("<pre>No changes identified or Sweeper tests run\n</pre>")
    else:
        for report in reports:
            message.write(
                f'<pre>{len(report["issues"]):4} Issues \t {report["title"]:<16} \t {report["feature_class"]:<50} \n</pre>'
            )

    return message


def _log_items(report, key):
    """print out issues or fixes to log
    report: report dictionary
    key: 'issues' | 'fixes'
    """
    try:
        items = report[key]
    except KeyError:
        return

    items_found = len(items)
    if items_found == 0:
        log.info(f"No {key} found!")
        log.info("---")

        return

    log.info(f"{items_found} {key} found:")

    has_oids = True
    if isinstance(items, list):
        for item in items:
            if isinstance(item, int):
                log.info(f"    ObjectID {item}")
            else:
                #: issues not associated with a specific row (e.g. metadata)
                has_oids = False
                log.info(f"    {item}")
    else:
        #: must be dict
        for oid in items:
            log.info(f"    ObjectID {oid}: {items[oid]}")

    if has_oids:
        log.info(f"\nSelect statement to view {key} in ArcGIS:")
        statement = f'OBJECTID IN ({", ".join([str(oid) for oid in items])})'

        log.info(statement)

    log.info("---")


def add_to_log(reports):
    if len(reports) == 0:
        log.info("No issues found!")

        return None

    #: loop through each report dict in the list of dicts
    for report in reports:
        log.info(f'{report["title"]} Report for {report["feature_class"]}')

        _log_items(report, "fixes")
        _log_items(report, "issues")
