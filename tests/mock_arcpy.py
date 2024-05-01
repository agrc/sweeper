#!/usr/bin/env python
# * coding: utf8 *
"""This allows you to mock out the entire arcpy package so that you can test packages that use arcpy in github's CI
environment. You just need to 'import mock_arcpy' prior to importing arcpy directly or importing any other packages/
modules that import arcpy in turn.
"""

import sys
from unittest.mock import Mock

try:
    import arcpy
except ImportError:
    MODULE_NAME = "arcpy"
    arcpy = Mock(name=MODULE_NAME)
    sys.modules[MODULE_NAME] = arcpy
