import typing as tp
from unittest import TestCase

from meta_etl.layer.yt.ods.yt import get_path_wo_partition
from meta_etl.layer.yt.ods.yt.node.impl import denest_paths


class TestOdsYtObject(TestCase):
    def test_get_path_wo_partition(self):
        for path, expected_path_wo_parttion in (
            ('//home/taxi-dwh/ods/mdb/order/2020-01', '//home/taxi-dwh/ods/mdb/order'),
            ('//home/taxi-dwh/ods/mdb/order/2020-03-14', '//home/taxi-dwh/ods/mdb/order'),
            ('//home/taxi-dwh/ods/mdb/order/order', '//home/taxi-dwh/ods/mdb/order/order'),
            ('//home/taxi-dwh/ods/mdb/order', '//home/taxi-dwh/ods/mdb/order'),
            ('//home/taxi-dwh/etl/rotation/ods/mdb/order/2020-03-14', '//home/taxi-dwh/etl/rotation/ods/mdb/order'),
        ):
            actual_path_wo_partition = get_path_wo_partition(path)
            self.assertEqual(expected_path_wo_parttion, actual_path_wo_partition)


class TestDenestPaths(TestCase):
    """ Test `denest_paths` function from `meta_etl.layer.yt.ods.yt.object.impl` """
    @staticmethod
    def _prepare_path_list(paths: tp.List[str]) -> tp.List[str]:
        return sorted([f"//{path.strip('/')}/" for path in paths], key=lambda path: (path.count('/'), path,))

    def _perform_test(self, paths: tp.List[str], expected: tp.List[str], fail_msg: str):
        paths = self._prepare_path_list(paths)
        denested = denest_paths(paths)
        self.assertListEqual(sorted(denested), sorted(expected), fail_msg)

    def test_no_nesting(self):
        paths = ["//home/test1/", "//home/test2/", "//home/test3/"]
        expected = ["//home/test1", "//home/test2", "//home/test3"]
        self._perform_test(paths, expected, "Failed simple case without nesting")

    def test_one_level_nesting(self):
        paths = ["//home/test1/", "//home/test1/test2/", "//home/test3/"]
        expected = ["//home/test1", "//home/test3"]
        self._perform_test(paths, expected, "Failed one level nesting")

    def test_multiple_level_nesting(self):
        paths = ["//home/test1/", "//home/test1/test2/", "//home/test1/test2/test3/", "//home/test4/test5/"]
        expected = ["//home/test1", "//home/test4/test5"]
        self._perform_test(paths, expected, "Failed multiple levels deep nesting")

    def test_multiple_nesting_under_one_level(self):
        paths = ["//home/test1/", "//home/test1/test2/", "//home/test1/test3/", "//home/test4/test5/"]
        expected = ["//home/test1", "//home/test4/test5"]
        self._perform_test(paths, expected, "Failed multiple sublevels nesting under one level")

    def test_duplicate_levels(self):
        paths = ["//home/test1/", "//home/test1/test2/", "//home/test1/test2/", "//home/test4/", "//home/test4/"]
        expected = ["//home/test1", "//home/test4"]
        self._perform_test(paths, expected, "Failed duplicate levels deduplication")
