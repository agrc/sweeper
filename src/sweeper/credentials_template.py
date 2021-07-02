"""
credentials_template.py: An example template of all the credentials and settings that need to be set.
"""

import socket

ORG = ''  #: URL to AGOL organization (https://www.arcgis.com)
USERNAME = ''  #: User whose items will be audited
PASSWORD = ''  #: USERNAME's password
DB = ''  #: Full path to sde connection file
METATABLE = ''  #: Full path to SGID.META.AGOLItems metatable
AGOL_TABLE = ''  #: URL for Feature Service REST endpoint for AGOL-hosted metatable
REPORT_BASE_PATH = ''  #: File path for report CSVs of everything that was fixed; rotated on each run
LOG_ROTATE_COUNT = 90  #: Number of logs to rotate through (the n+1 oldest log will be deleted at rotate)
CACHE_MAX_AGE = None  #: Number of seconds for the Cache Control/cacheMaxAge property (int)
EMAIL_SETTINGS = {  #: Settings for EmailHandler
    'smtpServer': '',
    'smtpPort': 25,
    'from_address': '',
    'to_addresses': '',
    'prefix': f'Auditor on {socket.gethostname()}: ',
}