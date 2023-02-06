#!/usr/bin/env python
# coding: utf-8

from unittest import TestCase

import mock
import pytest

from dmp_suite.clickhouse import CHMeta
from dmp_suite.clickhouse.table import *


class PatchedCHMeta(CHMeta):
    def __init__(self, *args, **kwargs):
        if 'prefix_managed' in kwargs:
            raise ValueError()
        super(PatchedCHMeta, self).__init__(prefix_manager=fake_prefix_resolver, *args, **kwargs)


class BaseTestTable(CHTable):
    __layout__ = CHLayout('name', db='db')


class NullableTest(TestCase):
    def test_instance_creation(self):
        with self.assertRaises(DWHError):
            field = Nullable(Array(Float))

        class Foo(object):
            pass
        self.assertRaises(DWHError, Nullable, Foo)

        Nullable(Float)

        with self.assertRaises(NotImplementedError):
            Array(Nullable(Float))

    def test_serializer(self):
        f = Nullable(Float)
        self.assertEqual(f.serializer(15.0), 15.0)
        self.assertEqual(f.serializer(None), b'\N')

        f = Nullable(String)
        self.assertEqual(f.serializer('some_string'), 'some_string')
        self.assertEqual(f.serializer('NULL'), 'NULL')
        self.assertEqual(f.serializer(None), b'\N')


class ArrayTest(TestCase):
    def test_instance(self):
        self.assertRaises(DWHError, Array, int)

        class Foo(object):
            pass
        self.assertRaises(DWHError, Array, Foo)

        Array(Float)
        Array(Float())
        Array(Array(Float))
        Array(Array(Float()))

    def test_default(self):
        a = Array(Int)
        assert b'[]' == a.serializer(None)
        assert b'[]' == a.serializer([])

        a = Array(Array(Int))
        in_data = [[1, None], None]
        out_data = a.serializer(in_data)
        assert b'[[1, 0], []]' == out_data

        a = Array(String)
        in_data = ['abc\t', 'cde']
        out_data = a.serializer(in_data)
        assert b"['abc\\\t', 'cde']" == out_data

        a = Array(DateTime)
        in_data = ['2017-05-05 01:01:01', None]
        out_data = a.serializer(in_data)
        true_result = (
            b"['2017-05-05 01:01:01', '" +
            DateTime.default_value.encode('utf-8') +
            b"']"
        )
        assert true_result, out_data

        with self.assertRaises(NotImplementedError):
            a = Array(Nullable(Float))
            in_data = [350.0, None]
            a.serializer(in_data)

        with self.assertRaises(NotImplementedError):
            a = Array(Nullable(String))
            in_data = ['abc', 'NULL', None]
            a.serializer(in_data)

    def test_inner_serializer(self):
        a = Array(Int)
        self.assertEqual(a._inner_serializer(1), 1)

        b = Array(Array(Int))
        self.assertEqual(b._inner_serializer([1]), b'[1]')

    def test_str_serializer(self):
        a = Array(String)
        assert a._str_serializer("1") == b"'1'"
        self.assertEqual(a._str_serializer(r"1'"), br"'1\''")
        self.assertEqual(a._str_serializer(r"\1"), br"'\\1'")
        self.assertEqual(
            a._str_serializer(r"'hello' quotes"), br"'\'hello\' quotes'")
        self.assertEqual(a._str_serializer(r"\c"), br"'\\c'")

    def test_serializer(self):
        a = Array(Int)
        in_data = [1, 2, 3]
        out_data = a.serializer(in_data)
        assert b'[1, 2, 3]' == out_data

        out_data = a.serializer(in_data)
        assert b'[1, 2, 3]' == out_data

        a = Array(String)
        in_data = ['qwe\t', 'rty\\']
        out_data = a.serializer(in_data)
        assert b"['qwe\\\t', 'rty\\\\']" == out_data

        a = Array(Array(Int))
        in_data = [[1, 6], []]
        out_data = a.serializer(in_data)
        assert b"[[1, 6], []]" == out_data

        a = Array(Array(Array(String)))
        in_data = [[['q']], [['w', 'a']]]
        out_data = a.serializer(in_data)
        assert b"[[['q']], [['w', 'a']]]" == out_data


class CHTableTest(TestCase):
    def test_log_engine(self):
        class TestTable(BaseTestTable):
            __engine__ = LogEngine()

        self.assertEqual(
            TestTable.__engine__.sql_desc(TestTable),
            'Log() '
        )

    def test_merge_tree_engine(self):
        class ValidTable(BaseTestTable):
            __engine__ = MergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                replicated=False
            )

            dt = Date()
            id = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "MergeTree() PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) SETTINGS index_granularity=8192"
        )

        class ValidTable(BaseTestTable):
            __engine__ = MergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                replicated=True
            )

            dt = Date()
            id = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "ReplicatedMergeTree('/clickhouse/tables/{shard}/pfx_db/name', '{replica}') PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) SETTINGS index_granularity=8192"
        )

        class ValidTable(BaseTestTable):
            __engine__ = MergeTreeEngine(
                partition_key='',
                primary_keys=[]
            )

            dt = Date()
            id = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "ReplicatedMergeTree('/clickhouse/tables/{shard}/pfx_db/name', '{replica}') PARTITION BY tuple() ORDER BY tuple() SETTINGS index_granularity=8192"
        )

        class ValidTable(BaseTestTable):
            __engine__ = MergeTreeEngine(
                partition_key=None,
                primary_keys=None,
                replicated=False
            )

            dt = Date()
            id = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "MergeTree() PARTITION BY tuple() ORDER BY tuple() SETTINGS index_granularity=8192"
        )

        class ValidTable(BaseTestTable):
            __engine__ = MergeTreeEngine(
                partition_key=None,
                primary_keys=tuple()
            )

            dt = Date()
            id = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "ReplicatedMergeTree('/clickhouse/tables/{shard}/pfx_db/name', '{replica}') PARTITION BY tuple() ORDER BY tuple() SETTINGS index_granularity=8192"
        )

        # TODO TAXIDWH-620 uncomment after fix
        # TODO https://st.yandex-team.ru/TAXIDWH-620
        # class NamedColumnTable(BaseTestTable):
        #     __engine__ = MergeTreeEngine(
        #         partition_key='dt',
        #         primary_keys=['id', 'dt']
        #     )
        #
        #     dt = Date(name='created')
        #     id = Int()
        #
        # self.assertEqual(
        #     CHMeta(NamedColumnTable).table_engine(),
        #     'MergeTree(created, (id, created), 8192)'
        # )

        class ColumnTable(BaseTestTable):
            __engine__ = MergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt']
            )

            dt = Date()

        self.assertRaises(
            ValueError,
            PatchedCHMeta,
            ColumnTable
        )

    def test_collapsing_merge_tree_engine(self):
        class ValidTable(BaseTestTable):
            __engine__ = CollapsingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt']
            )

            dt = Date()
            id = Int()
            sign = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/pfx_db/name', '{replica}', sign) PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) SETTINGS index_granularity=8192"
        )

        class ValidTable(BaseTestTable):
            __engine__ = CollapsingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                replicated=False
            )

            dt = Date()
            id = Int()
            sign = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "CollapsingMergeTree(sign) PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) SETTINGS index_granularity=8192"
        )

        class ValidTable(BaseTestTable):
            __engine__ = CollapsingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                replicated=True
            )

            dt = Date()
            id = Int()
            sign = Int()

        self.assertEqual(
            PatchedCHMeta(ValidTable).table_engine(),
            "ReplicatedCollapsingMergeTree('/clickhouse/tables/{shard}/pfx_db/name', '{replica}', sign) PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) SETTINGS index_granularity=8192"
        )

        class SignSkippedTable(BaseTestTable):
            __engine__ = CollapsingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt']
            )

            dt = Date()
            id = Int()

        self.assertRaises(
            ValueError,
            PatchedCHMeta,
            SignSkippedTable
        )

    def test_replacing_merge_tree_engine(self):
        class DefaultTable(BaseTestTable):
            __engine__ = ReplacingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt']
            )
            dt = Date()
            id = Int()

        self.assertEqual(
            "ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/pfx_db/name', "
            "'{replica}') PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) SETTINGS "
            "index_granularity=8192",
            PatchedCHMeta(DefaultTable).table_engine()
        )

        class NonReplicatedTable(BaseTestTable):
            __engine__ = ReplacingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                replicated=False
            )
            dt = Date()
            id = Int()

        self.assertEqual(
            "ReplacingMergeTree() PARTITION BY toYYYYMM(dt) "
            "ORDER BY (id, dt) SETTINGS index_granularity=8192",
            PatchedCHMeta(NonReplicatedTable).table_engine()
        )

        class ExplicitlyReplicatedTable(BaseTestTable):
            __engine__ = ReplacingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                replicated=True
            )
            dt = Date()
            id = Int()

        self.assertEqual(
            "ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/pfx_db/name', "
            "'{replica}') PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) "
            "SETTINGS index_granularity=8192",
            PatchedCHMeta(ExplicitlyReplicatedTable).table_engine()
        )

        class VersionedTable(BaseTestTable):
            __engine__ = ReplacingMergeTreeEngine(
                partition_key='dt',
                primary_keys=['id', 'dt'],
                version_key='ver'
            )
            dt = Date()
            id = Int()
            ver = Int()

        self.assertEqual(
            "ReplicatedReplacingMergeTree('/clickhouse/tables/{shard}/pfx_db/name', "
            "'{replica}', ver) PARTITION BY toYYYYMM(dt) ORDER BY (id, dt) "
            "SETTINGS index_granularity=8192",
            PatchedCHMeta(VersionedTable).table_engine()
        )


def fake_prefix_resolver(service):
    if service == 'custom_service':
        return 'custom_service'
    return 'pfx'


@pytest.mark.parametrize('layout, expected_full', [
    (CHLayout('name', db='ct_db'), 'pfx_ct_db.name'),
    (CHLayout('name', db='ct_db', prefix_key='custom_service'), 'custom_service_ct_db.name'),
    (CHLayout('name'), 'pfx_db.name'),
])
def test_gp_location(layout, expected_full):
    class Tab(CHTable):
        __layout__ = layout

    with mock.patch('dmp_suite.clickhouse.table.get_db_by_prefix_key', return_value='db'):
        resolver = CHLocation(Tab, prefix_manager=fake_prefix_resolver)
        assert resolver.full() == expected_full


def test_gp_location_with_partition():
    class Tab(CHTable):
        __layout__ = CHLayout('name', db='ct_db')

    resolver = CHLocation(Tab, prefix_manager=fake_prefix_resolver)
    assert resolver.full() == 'pfx_ct_db.name'
    assert resolver.rotation_full('abc') == 'pfx_ct_db.rotation_name_abc'
    assert resolver.rotation_full() == 'pfx_ct_db.rotation_name'
