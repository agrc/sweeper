import logging
from pathlib import Path

from .. import config

log = logging.getLogger("sweeper")


class SweeperBase:
    def clone(self, table_name, workspace):
        log.info(f"cloning to {table_name}")
        parts = table_name.split(".")
        if len(parts) == 3:
            user = parts[0].upper()
            workspace = str(Path(config.get_config("CONNECTIONS_FOLDER"), f"{user}.sde"))

        return self.__class__(workspace, table_name)
