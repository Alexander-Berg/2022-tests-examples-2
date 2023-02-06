#!/usr/bin/env python
# coding: utf-8
import mock

from dmp_suite.clickhouse import CHTable, String, Date, MergeTreeEngine, CHMeta, CHLayout
from dmp_suite import datetime_utils as dtu

import unittest

from dmp_suite.table import Table


class T(Table):
    pass


class TestTable(CHTable):
    __layout__ = CHLayout('test', db='db')

    id = String()
    dt = Date()
    name = String()


class TestMergeTreeTable(CHTable):
    __layout__ = CHLayout('merge_tree_table', db='db')
    __engine__ = MergeTreeEngine(
        partition_key='dt',
        primary_keys=['dt', 'id']
    )

    id = String()
    dt = Date()
    name = String()


def fake_prefix_manager(service):
    return 'pfx'


class TestCHMeta(unittest.TestCase):
    def test(self):
        meta = CHMeta(TestTable, prefix_manager=fake_prefix_manager)
        self.assertEqual(meta.partition, None)
        self.assertEqual(
            meta.table_full_name(),
            'pfx_db.test'
        )
        self.assertEqual(
            meta.rotation_table_full_name(),
            'pfx_db.rotation_test'
        )

        meta = CHMeta(TestTable, '2017-05', prefix_manager=fake_prefix_manager)
        self.assertEqual(meta.partition, '201705')
        self.assertEqual(
            meta.table_full_name(),
            'pfx_db.test'
        )
        self.assertEqual(
            meta.rotation_table_full_name(),
            'pfx_db.rotation_test_201705'
        )

        meta = CHMeta(TestTable, dtu.parse_datetime('2017-05-04'), prefix_manager=fake_prefix_manager)
        self.assertEqual(meta.partition, '201705')
        self.assertEqual(
            meta.table_full_name(),
            'pfx_db.test'
        )
        self.assertEqual(
            meta.rotation_table_full_name(),
            'pfx_db.rotation_test_201705'
        )

    def test_partition_key(self):
        meta = CHMeta(TestMergeTreeTable, prefix_manager=fake_prefix_manager)
        self.assertEqual(meta.partition_key(), 'dt')

    def test_correct_table_class(self):
        self.assertRaises(ValueError, CHMeta, T)
