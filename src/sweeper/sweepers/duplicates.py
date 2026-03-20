#!/usr/bin/env python
# * coding: utf8 *
import logging
import re
import typing
from typing import Generator

import arcpy
from xxhash import xxh64

from .base import SweeperBase

log = logging.getLogger("sweeper")


class DuplicateTest(SweeperBase):
    """A class that finds and removes duplicate geometries or attributes or both"""

    key = "duplicates"

    def __init__(self, workspace, table_name):
        self.workspace = workspace
        self.table_name = table_name
        self.oids_with_issues = []
        self.is_table = False

    def sweep(self):
        """A method that finds duplicate records and returns a report dictionary"""
        report = {"title": "Duplicate Test", "feature_class": self.table_name, "issues": []}
        digests = set([])

        truncate_shape_precision = re.compile(r"(\d+\.\d{2})(\d+)")

        with arcpy.EnvManager(workspace=self.workspace):
            description = arcpy.da.Describe(self.table_name)
            log.info(f"Working on Duplicates for: {self.table_name}")
            if description["dataType"].casefold() == "table":
                self.is_table = True
                skip_fields = ["guid"]
            else:
                skip_fields = ["guid", description["shapeFieldName"]]

            if description["hasGlobalID"]:
                skip_fields.append(description["globalIDFieldName"])

            if description["hasOID"]:
                skip_fields.append(description["OIDFieldName"])

            fields = [field.name for field in description["fields"] if field.name not in skip_fields]
            fields.append("OID@")

            #: include or exclude shape field depending on if working on table or feature class
            if self.is_table:
                oid_index = fields.index("OID@")

                with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                    for row in search_cursor:
                        object_id = row[oid_index]

                        hasher = xxh64(f"{row[:-1]}")
                        digest = hasher.hexdigest()

                        if digest in digests:
                            report["issues"].append(str(object_id))
                            self.oids_with_issues.append(object_id)

                        digests.add(digest)
            else:
                oid_index = fields.index("OID@")
                fields.append("SHAPE@WKT")

                shapefield_index = fields.index("SHAPE@WKT")
                oid_index = fields.index("OID@")

                with arcpy.da.SearchCursor(self.table_name, fields) as search_cursor:
                    for row in search_cursor:
                        shape_wkt = row[shapefield_index]
                        object_id = row[oid_index]

                        if shape_wkt is None:
                            continue

                        #: trim some digits to help with hash matching
                        generalized_wkt = truncate_shape_precision.sub(r"\1", shape_wkt)

                        hasher = xxh64(f"{row[:-2]} {generalized_wkt}")
                        digest = hasher.hexdigest()

                        if digest in digests:
                            report["issues"].append(str(object_id))
                            self.oids_with_issues.append(object_id)

                        digests.add(digest)

        return report

    def try_fix(self):
        """a method that tries to remove the duplicate records"""
        report = {"title": "Duplicate Try Fix", "feature_class": self.table_name, "issues": [], "fixes": []}

        if len(self.oids_with_issues) == 0:
            return report

        chunk_size = 1000

        # sql = f'"OBJECTID" IN ({",".join([str(oid) for oid in self.oids_with_issues])})'
        lists_of_oids = list(self._chunk_oid_list(self.oids_with_issues, chunk_size))
        temp_feature_layer = "temp_layer"

        log.info(f"Workspace is:   {self.workspace}")
        log.info(
            f"Attempting to delete a total of {len(self.oids_with_issues)} duplicate records in {len(lists_of_oids)} batch(es) of {chunk_size} records each"
        )

        successful_deletes = 0
        failed_deletes = 0
        failed_batches = 0

        with arcpy.EnvManager(workspace=self.workspace):
            all_features = self._make_feature_layer(self.table_name, temp_feature_layer, self.is_table)

            for index, list_of_oids in enumerate(lists_of_oids, start=1):
                sql = f'"OBJECTID" IN ({",".join([str(oid) for oid in list_of_oids])})'

                try:
                    log.info(f"Batch {index}: attempting to delete {len(list_of_oids)} duplicate records")
                    arcpy.management.SelectLayerByAttribute(all_features, "NEW_SELECTION", sql)
                    self._delete_features_or_rows(all_features, self.is_table)
                    successful_deletes += len(list_of_oids)
                except Exception as error:
                    error_message = f"unable to delete features in batch {index}: {error}"
                    log.info(error_message)
                    report["issues"].append(error_message)
                    failed_deletes += len(list_of_oids)
                    failed_batches += 1
                finally:
                    arcpy.management.SelectLayerByAttribute(all_features, "CLEAR_SELECTION")

            if arcpy.Exists(temp_feature_layer):
                arcpy.management.Delete(temp_feature_layer)
            if successful_deletes > 0:
                report["fixes"].append(f"{successful_deletes} records deleted successfully")
            if failed_deletes > 0:
                report["issues"].append(
                    f"{failed_batches} batch(es) with {failed_deletes} total records had errors deleting."
                )

        return report

    @staticmethod
    def _chunk_oid_list(lst: list, chunk_size: int) -> Generator[list, None, None]:
        """Breaks a list into chunks of chunk_size

        Args:
            lst (list): Input List
            chunk_size (int): The desired size per chunk

        Yields:
            Generator[list, None, None]: The next chunk_size sized chunk
        """
        if len(lst) <= chunk_size:
            yield lst
            return
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    @staticmethod
    def _make_feature_layer(feature_class: str, temp_layer_name: str, is_table: bool) -> typing.Any:
        """Single method to handle table or layer creation based on is_table parameter"""
        #: arcpy's typing gets really convoluted, so we're just using typing.Any.

        if is_table:
            return arcpy.management.MakeTableView(feature_class, temp_layer_name)
        else:
            return arcpy.management.MakeFeatureLayer(feature_class, temp_layer_name)

    @staticmethod
    def _delete_features_or_rows(feature_layer: typing.Any, is_table: bool):
        """Single method to handle deleting features or rows based on is_table parameter"""
        if is_table:
            arcpy.management.DeleteRows(feature_layer)
        else:
            arcpy.management.DeleteFeatures(feature_layer)
