import json
import logging
from pathlib import Path

log = logging.getLogger("sweeper")

try:
    with open("config.json") as f:
        config = json.load(f)
except FileNotFoundError:
    log.debug("A config.json not found in current working directory. This will prevent some features from working.")


def get_config(name):
    try:
        return config[name]
    except KeyError:
        raise KeyError(
            f"Config key {name} not found in config.json. Perhaps you need to create or update it? Note that it needs to be in the current working directory."
        )


# set this to the current working directory
LOG_FILE_PATH = Path(Path.cwd(), "sweeper.log")
