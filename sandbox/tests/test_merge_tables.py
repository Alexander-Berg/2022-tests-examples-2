import os

import pytest
from six import iteritems

import yt.wrapper as yt

from mapreduce.yt.python.table_schema import extract_column_attributes

from sandbox.projects.avia.lib.merge_tables import merge_table, TableMergeError
from sandbox.projects.avia.lib.yt_helpers import create_safe_temp_table

FIRST_SCHEMA = [
    {'name': 'int_column', 'type': 'int64', 'required': False},
    {'name': 'string_column', 'type': 'string', 'required': False},
    {'name': 'string_column2', 'type': 'string', 'required': False}
]

FIRST_VALUES = [
    {'int_column': 12, 'string_column': 'abc', 'string_column2': 'cdef'},
]

SECOND_SCHEMA = [
    {'name': 'int_column', 'type': 'int64', 'required': False},
    {'name': 'string_column', 'type': 'string', 'required': False},
]

SECOND_VALUES = [
    {'int_column': 24, 'string_column': 'efd'},
]

THIRD_SCHEMA = [
    {'name': 'int_column', 'type': 'int64', 'required': False},
    {'name': 'bool_column', 'type': 'boolean', 'required': False},
]

THIRD_VALUES = [
    {'int_column': 24, 'bool_column': True},
]

FOURTH_SCHEMA = [
    {'name': 'int_column', 'type': 'double', 'requidred': False},
]

FOURTH_VALUES = [
    {'int_column': 24.123},
]


def _are_records_equal(left, right):
    def without_none(dct):
        return {key: value for key, value in iteritems(dct) if value is not None}

    return without_none(left) == without_none(right)


def _are_tables_equal(left, right):
    used_right = set()

    for left_record in left:
        found = False
        for ind, right_record in enumerate(right):
            if ind in used_right:
                continue
            if _are_records_equal(left_record, right_record):
                used_right.add(ind)
                found = True
                break
        if not found:
            return False

    return len(used_right) == len(right)


def _get_yt():
    return yt.YtClient(proxy=os.environ['YT_PROXY'], config={'proxy': {'enable_proxy_discovery': False}})


def _create_and_fill_table(ytc, schema, values):
    table = create_safe_temp_table(ytc, __file__, attributes={'schema': schema})
    ytc.write_table(table, values)

    return table


def test_delete_field():
    ytc = _get_yt()
    dst_schema = _create_and_fill_table(ytc, FIRST_SCHEMA, FIRST_VALUES)
    src_table = _create_and_fill_table(ytc, SECOND_SCHEMA, SECOND_VALUES)

    ytc.set_attribute(dst_schema, 'processed', [])

    merge_table(ytc, src_table, dst_schema)

    new_dst_schema = ytc.get_attribute(dst_schema, 'schema')
    assert extract_column_attributes(sorted(new_dst_schema)) == sorted(FIRST_SCHEMA), 'Schema changed'
    assert _are_tables_equal(ytc.read_table(dst_schema), FIRST_VALUES + SECOND_VALUES)

    ytc.remove(dst_schema)
    ytc.remove(src_table)


def test_add_new_field():
    ytc = _get_yt()
    src_table = _create_and_fill_table(ytc, FIRST_SCHEMA, FIRST_VALUES)
    dst_table = _create_and_fill_table(ytc, SECOND_SCHEMA, SECOND_VALUES)

    ytc.set_attribute(dst_table, 'processed', [])

    merge_table(ytc, src_table, dst_table)

    new_dst_schema = ytc.get_attribute(dst_table, 'schema')
    assert extract_column_attributes(sorted(new_dst_schema)) == sorted(FIRST_SCHEMA), 'Schema changed'
    assert _are_tables_equal(ytc.read_table(dst_table), FIRST_VALUES + SECOND_VALUES)

    ytc.remove(src_table)
    ytc.remove(dst_table)


def test_same_schemas():
    ytc = _get_yt()
    dst_table = _create_and_fill_table(ytc, FIRST_SCHEMA, FIRST_VALUES)
    src_table = _create_and_fill_table(ytc, FIRST_SCHEMA, FIRST_VALUES)

    ytc.set_attribute(dst_table, 'processed', [])

    merge_table(ytc, src_table, dst_table)

    new_dst_schema = ytc.get_attribute(src_table, 'schema')
    assert extract_column_attributes(sorted(new_dst_schema)) == sorted(FIRST_SCHEMA), 'Schema changed'
    assert _are_tables_equal(ytc.read_table(dst_table), FIRST_VALUES + FIRST_VALUES)

    ytc.remove(dst_table)
    ytc.remove(src_table)


def test_add_and_delete_field():
    ytc = _get_yt()
    src_table = _create_and_fill_table(ytc, THIRD_SCHEMA, THIRD_VALUES)
    dst_table = _create_and_fill_table(ytc, FIRST_SCHEMA, FIRST_VALUES)

    ytc.set_attribute(dst_table, 'processed', [])

    merge_table(ytc, src_table, dst_table)

    right_schema = [
        {'name': 'int_column', 'type': 'int64', 'required': False},
        {'name': 'string_column', 'type': 'string', 'required': False},
        {'name': 'string_column2', 'type': 'string', 'required': False},
        {'name': 'bool_column', 'type': 'boolean', 'required': False},
    ]

    new_dst_schema = ytc.get_attribute(dst_table, 'schema')
    assert extract_column_attributes(sorted(new_dst_schema)) == sorted(right_schema), 'Schema changed'
    assert _are_tables_equal(ytc.read_table(dst_table), FIRST_VALUES + THIRD_VALUES)

    ytc.remove(src_table)
    ytc.remove(dst_table)


def test_incompatible_schemas():
    ytc = _get_yt()
    dst_table = _create_and_fill_table(ytc, FIRST_SCHEMA, FIRST_VALUES)
    src_table = _create_and_fill_table(ytc, FOURTH_SCHEMA, FOURTH_VALUES)

    ytc.set_attribute(dst_table, 'processed', [])

    with pytest.raises(TableMergeError):
        merge_table(ytc, src_table, dst_table)

    ytc.remove(src_table)
    ytc.remove(dst_table)
