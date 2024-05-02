import json
from pathlib import Path

try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError("A config.json not found in current working directory. Please create one.")

SENDGRID_API_KEY = config["SENDGRID_API_KEY"]
TO_ADDRESSES = config["TO_ADDRESSES"]
CONNECTIONS_FOLDER = config["CONNECTIONS_FOLDER"]
CHANGE_DETECTION_CONNECTION = config["CHANGE_DETECTION_CONNECTION"]
CHANGE_DETECTION_TABLE = config["CHANGE_DETECTION_TABLE"]

# set this to the current working directory
LOG_FILE_PATH = Path(Path.cwd(), "sweeper.log")
