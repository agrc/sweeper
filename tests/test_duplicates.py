import sys
from unittest.mock import MagicMock, patch

#: Mock arcpy before importing the module under test
arcpy_mock = MagicMock()
sys.modules["arcpy"] = arcpy_mock
sys.modules["arcpy.da"] = arcpy_mock.da
sys.modules["arcpy._mp"] = arcpy_mock._mp
sys.modules["arcpy.typing"] = arcpy_mock.typing
sys.modules["arcpy.typing.gp"] = arcpy_mock.typing.gp
sys.modules["xxhash"] = MagicMock()

from sweeper.sweepers.duplicates import DuplicateTest  # noqa: E402


class TestChunkOidList:
    def test_chunk_oid_list_small_list_returns_single_chunk(self):
        lst = [1, 2, 3]
        result = list(DuplicateTest._chunk_oid_list(lst, 10))

        assert result == [[1, 2, 3]]

    def test_chunk_oid_list_exact_chunk_size_returns_single_chunk(self):
        lst = list(range(10))
        result = list(DuplicateTest._chunk_oid_list(lst, 10))

        assert result == [list(range(10))]

    def test_chunk_oid_list_large_list_returns_multiple_chunks(self):
        lst = list(range(25))
        result = list(DuplicateTest._chunk_oid_list(lst, 10))

        assert len(result) == 3
        assert result[0] == list(range(10))
        assert result[1] == list(range(10, 20))
        assert result[2] == list(range(20, 25))

    def test_chunk_oid_list_empty_list_returns_single_empty_chunk(self):
        result = list(DuplicateTest._chunk_oid_list([], 10))

        assert result == [[]]

    def test_chunk_oid_list_exactly_two_chunks(self):
        lst = list(range(20))
        result = list(DuplicateTest._chunk_oid_list(lst, 10))

        assert len(result) == 2
        assert result[0] == list(range(10))
        assert result[1] == list(range(10, 20))


class TestMakeFeatureLayer:
    def setup_method(self):
        arcpy_mock.reset_mock()

    def test_make_feature_layer_is_table_calls_make_table_view(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.is_table = True
        sweeper._make_feature_layer("temp_layer")

        arcpy_mock.management.MakeTableView.assert_called_once_with("my_table", "temp_layer")

    def test_make_feature_layer_is_not_table_calls_make_feature_layer(self):
        sweeper = DuplicateTest("workspace", "my_fc")
        sweeper._make_feature_layer("temp_layer")

        arcpy_mock.management.MakeFeatureLayer.assert_called_once_with("my_fc", "temp_layer")


class TestDeleteFeaturesOrRows:
    def setup_method(self):
        arcpy_mock.reset_mock()

    def test_delete_features_or_rows_is_table_calls_delete_rows(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.is_table = True
        layer_mock = MagicMock()
        sweeper._delete_features_or_rows(layer_mock)

        arcpy_mock.management.DeleteRows.assert_called_once_with(layer_mock)

    def test_delete_features_or_rows_is_not_table_calls_delete_features(self):
        sweeper = DuplicateTest("workspace", "my_fc")
        layer_mock = MagicMock()
        sweeper._delete_features_or_rows(layer_mock)

        arcpy_mock.management.DeleteFeatures.assert_called_once_with(layer_mock)


class TestTryFix:
    def setup_method(self):
        arcpy_mock.reset_mock()
        arcpy_mock.management.SelectLayerByAttribute.side_effect = None
        arcpy_mock.EnvManager.return_value.__enter__ = MagicMock(return_value=None)
        arcpy_mock.EnvManager.return_value.__exit__ = MagicMock(return_value=False)
        self._valid_selection_patcher = patch.object(DuplicateTest, "_valid_selection", return_value=True)
        self._valid_selection_patcher.start()

    def teardown_method(self):
        self._valid_selection_patcher.stop()

    def test_try_fix_no_oids_returns_empty_report(self):
        sweeper = DuplicateTest("workspace", "my_table")

        report = sweeper.try_fix()

        assert report["title"] == "Duplicate Try Fix"
        assert report["feature_class"] == "my_table"
        assert report["issues"] == []
        assert report["fixes"] == []

    def test_try_fix_successful_deletes_reports_count(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = [1, 2, 3]
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock

        report = sweeper.try_fix()

        assert "3 records deleted successfully" in report["fixes"]
        assert report["issues"] == []

    def test_try_fix_failed_batch_reports_error(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = [1, 2, 3]
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock
        arcpy_mock.management.SelectLayerByAttribute.side_effect = [Exception("delete error"), MagicMock()]

        report = sweeper.try_fix()

        assert any("unable to delete features in batch 1" in issue for issue in report["issues"])
        assert any("1 batch(es) with 3 total records had errors deleting." in issue for issue in report["issues"])

    def test_try_fix_clear_selection_called_in_finally(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = [1, 2]
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock
        arcpy_mock.management.SelectLayerByAttribute.side_effect = [Exception("fail"), None]

        sweeper.try_fix()

        clear_calls = [
            c for c in arcpy_mock.management.SelectLayerByAttribute.call_args_list if "CLEAR_SELECTION" in c.args
        ]
        assert len(clear_calls) >= 1

    def test_try_fix_is_table_uses_make_table_view(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = [1]
        sweeper.is_table = True
        table_view_mock = MagicMock()
        arcpy_mock.management.MakeTableView.return_value = table_view_mock

        report = sweeper.try_fix()

        arcpy_mock.management.MakeTableView.assert_called_once_with("my_table", "temp_layer")
        assert "1 records deleted successfully" in report["fixes"]

    def test_try_fix_multiple_batches_accumulates_successful_deletes(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = list(range(1500))
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock
        arcpy_mock.management.SelectLayerByAttribute.side_effect = None
        arcpy_mock.management.SelectLayerByAttribute.return_value = MagicMock()

        report = sweeper.try_fix()

        assert "1500 records deleted successfully" in report["fixes"]

    def test_try_fix_partial_failure_reports_correct_counts(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = list(range(1500))
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock

        call_count = 0

        def select_side_effect(*args, **kwargs):
            nonlocal call_count
            if "CLEAR_SELECTION" in args:
                return MagicMock()
            call_count += 1
            if call_count == 1:
                raise Exception("batch 1 failed")

            return MagicMock()

        arcpy_mock.management.SelectLayerByAttribute.side_effect = select_side_effect

        report = sweeper.try_fix()

        assert any("500 records deleted successfully" in fix for fix in report["fixes"])
        assert any("1 batch(es) with 1000 total records had errors deleting." in issue for issue in report["issues"])

    def test_try_fix_invalid_selection_reports_error(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = [1, 2, 3]
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock

        with patch.object(DuplicateTest, "_valid_selection", return_value=False):
            report = sweeper.try_fix()

        assert any("Invalid selection for batch 1" in issue for issue in report["issues"])
        assert any("1 batch(es) with 3 total records had errors deleting." in issue for issue in report["issues"])

    def test_try_fix_continues_after_invalid_selection_batch(self):
        sweeper = DuplicateTest("workspace", "my_table")
        sweeper.oids_with_issues = list(range(1500))
        layer_mock = MagicMock()
        arcpy_mock.management.MakeFeatureLayer.return_value = layer_mock

        #: Return False for batch 1, True for all subsequent batches
        valid_selection_results = iter([False, True, True])
        with patch.object(DuplicateTest, "_valid_selection", side_effect=valid_selection_results):
            report = sweeper.try_fix()

        assert any("500 records deleted successfully" in fix for fix in report["fixes"])
        assert any("Invalid selection for batch 1" in issue for issue in report["issues"])
        assert any("1 batch(es) with 1000 total records had errors deleting." in issue for issue in report["issues"])


class TestValidSelection:
    def setup_method(self):
        arcpy_mock.reset_mock()

    def _make_cursor_mock(self, rows):
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

    def test_valid_selection_returns_true_when_oids_match(self):
        self._make_cursor_mock([(1,), (2,), (3,)])

        result = DuplicateTest._valid_selection(MagicMock(), [1, 2, 3])

        assert result is True

    def test_valid_selection_returns_false_when_oids_do_not_match(self):
        self._make_cursor_mock([(1,), (2,)])

        result = DuplicateTest._valid_selection(MagicMock(), [1, 2, 3])

        assert result is False

    def test_valid_selection_returns_false_when_selection_is_empty(self):
        self._make_cursor_mock([])

        result = DuplicateTest._valid_selection(MagicMock(), [1, 2, 3])

        assert result is False

    def test_valid_selection_returns_true_for_single_oid_match(self):
        self._make_cursor_mock([(42,)])

        result = DuplicateTest._valid_selection(MagicMock(), [42])

        assert result is True


#: This test class was added by copilot when creating tests for the try_fix method. They pass, but I've not verified if they're actually sane.
class TestSweep:
    def setup_method(self):
        arcpy_mock.reset_mock()
        arcpy_mock.EnvManager.return_value.__enter__ = MagicMock(return_value=None)
        arcpy_mock.EnvManager.return_value.__exit__ = MagicMock(return_value=False)

    def _make_field(self, name: str) -> MagicMock:
        field = MagicMock()
        field.name = name

        return field

    def test_sweep_table_no_duplicates_returns_empty_issues(self):
        sweeper = DuplicateTest("workspace", "my_table")
        description = {
            "dataType": "Table",
            "hasGlobalID": False,
            "hasOID": True,
            "OIDFieldName": "OBJECTID",
            "fields": [self._make_field("Name"), self._make_field("OBJECTID")],
            "shapeFieldName": "Shape",
            "globalIDFieldName": "GlobalID",
        }
        arcpy_mock.da.Describe.return_value = description

        rows = [("Alice", 1), ("Bob", 2)]
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

        # import xxhash  #: This is unused; not sure if manually inserting the mock into sys.modules works; this was a copilot-created test.

        real_hashes = {}

        def fake_xxh64(data):
            hasher = MagicMock()
            hasher.hexdigest.return_value = str(hash(data))
            real_hashes[data] = hasher.hexdigest.return_value

            return hasher

        sys.modules["xxhash"].xxh64.side_effect = fake_xxh64

        report = sweeper.sweep()

        assert report["issues"] == []
        assert sweeper.is_table is True

    def test_sweep_table_with_duplicates_reports_oids(self):
        sweeper = DuplicateTest("workspace", "my_table")
        description = {
            "dataType": "Table",
            "hasGlobalID": False,
            "hasOID": True,
            "OIDFieldName": "OBJECTID",
            "fields": [self._make_field("Name"), self._make_field("OBJECTID")],
            "shapeFieldName": "Shape",
            "globalIDFieldName": "GlobalID",
        }
        arcpy_mock.da.Describe.return_value = description

        rows = [("Alice", 1), ("Alice", 2)]
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

        digest_counter = {"count": 0}

        def fake_xxh64(data):
            hasher = MagicMock()
            digest_counter["count"] += 1
            #: Return the same hash for both rows to simulate duplicate
            hasher.hexdigest.return_value = "same_hash"

            return hasher

        sys.modules["xxhash"].xxh64.side_effect = fake_xxh64

        report = sweeper.sweep()

        assert "2" in report["issues"]
        assert 2 in sweeper.oids_with_issues

    def test_sweep_feature_class_skips_none_shape(self):
        sweeper = DuplicateTest("workspace", "my_fc")
        description = {
            "dataType": "FeatureClass",
            "hasGlobalID": False,
            "hasOID": True,
            "OIDFieldName": "OBJECTID",
            "shapeFieldName": "Shape",
            "globalIDFieldName": "GlobalID",
            "fields": [self._make_field("Name"), self._make_field("OBJECTID"), self._make_field("Shape")],
        }
        arcpy_mock.da.Describe.return_value = description

        rows = [("Alice", 1, None)]
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

        report = sweeper.sweep()

        assert report["issues"] == []
        assert sweeper.is_table is False

    def test_sweep_feature_class_with_duplicates_reports_oids(self):
        sweeper = DuplicateTest("workspace", "my_fc")
        description = {
            "dataType": "FeatureClass",
            "hasGlobalID": False,
            "hasOID": True,
            "OIDFieldName": "OBJECTID",
            "shapeFieldName": "Shape",
            "globalIDFieldName": "GlobalID",
            "fields": [self._make_field("Name"), self._make_field("OBJECTID"), self._make_field("Shape")],
        }
        arcpy_mock.da.Describe.return_value = description

        rows = [
            ("Alice", 1, "POINT (1.123456 2.123456)"),
            ("Alice", 2, "POINT (1.123456 2.123456)"),
        ]
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

        def fake_xxh64(data):
            hasher = MagicMock()
            hasher.hexdigest.return_value = "same_hash"

            return hasher

        sys.modules["xxhash"].xxh64.side_effect = fake_xxh64

        report = sweeper.sweep()

        assert "2" in report["issues"]
        assert 2 in sweeper.oids_with_issues

    def test_sweep_skips_global_id_field(self):
        sweeper = DuplicateTest("workspace", "my_table")
        description = {
            "dataType": "Table",
            "hasGlobalID": True,
            "globalIDFieldName": "GlobalID",
            "hasOID": True,
            "OIDFieldName": "OBJECTID",
            "shapeFieldName": "Shape",
            "fields": [self._make_field("Name"), self._make_field("GlobalID"), self._make_field("OBJECTID")],
        }
        arcpy_mock.da.Describe.return_value = description

        rows = [("Alice", 1)]
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

        def fake_xxh64(data):
            hasher = MagicMock()
            hasher.hexdigest.return_value = "unique_hash"

            return hasher

        sys.modules["xxhash"].xxh64.side_effect = fake_xxh64

        sweeper.sweep()

        call_args = arcpy_mock.da.SearchCursor.call_args
        fields_used = call_args[0][1]
        assert "GlobalID" not in fields_used

    def test_sweep_returns_correct_report_structure(self):
        sweeper = DuplicateTest("workspace", "my_table")
        description = {
            "dataType": "Table",
            "hasGlobalID": False,
            "hasOID": False,
            "OIDFieldName": "OBJECTID",
            "shapeFieldName": "Shape",
            "globalIDFieldName": "GlobalID",
            "fields": [self._make_field("Name")],
        }
        arcpy_mock.da.Describe.return_value = description

        rows = []
        cursor_mock = MagicMock()
        cursor_mock.__enter__ = MagicMock(return_value=iter(rows))
        cursor_mock.__exit__ = MagicMock(return_value=False)
        arcpy_mock.da.SearchCursor.return_value = cursor_mock

        report = sweeper.sweep()

        assert "title" in report
        assert "feature_class" in report
        assert "issues" in report
        assert report["title"] == "Duplicate Test"
        assert report["feature_class"] == "my_table"
