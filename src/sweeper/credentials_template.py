"""
credentials_template.py: An example template of all the credentials and settings that need to be set.
"""

import socket

DB = ''  #: Full path to sde connection file
CHANGE_DETECTION = '' #: Change detection table name with 'SGID.' prefix
LAST_CHECKED_PATH = '' #: Full path to .last_checked file
REPORT_BASE_PATH = '' #: File path for report CSVs of everything that was fixed; rotated on each run
CONNECTIONS = '' #: Dictionary that holds SDE connection file paths
EMAIL_SETTINGS = {  #: Settings for EmailHandler
    'smtpServer': '',
    'smtpPort': 25,
    'from_address': '',
    'to_addresses': '',
    'prefix': f'Auditor on {socket.gethostname()}: ',
}