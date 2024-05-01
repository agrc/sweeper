from unittest.mock import Mock

# ruff: isort: off
from . import mock_arcpy  # noqa: F401
import arcpy

# ruff: isort: on

import pytest


@pytest.fixture()
def skip_if_no_arcpy():
    if isinstance(arcpy, Mock):
        pytest.skip("No arcpy detected, skipping test")
