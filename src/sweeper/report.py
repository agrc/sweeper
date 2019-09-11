#!/usr/bin/env python
# * coding: utf8 *
'''
report.py
A module that contains the templates for the reports and functions to format data into the report
'''

template = '''# Sweeper Empty Report

**{0}** empty geometries found

## ObjectId's of empty geometries

`{1}`

## Select features in arc

`objectid in ({1})`
'''

success_template = '''# Sweeper Empty Report

🚀🚀🚀 No empty geometries found 🚀🚀🚀


if len(report.oids) > 0:
  return string.format(template, len(report.oids), ','.join(report.oids))

return success


'sweeper-report-{}.{}.txt'.format(date.short, report_type)
'''
