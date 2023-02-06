# -*- coding: utf-8 -*-
import pytest

from test.gp_table import get_gp_object, create_gp_object, drop_gp_object, check_table_exists, \
    DATABASE_NAME, SCHEMA_NAME, TABLE_NAME, VIEW_NAME, SEQUENCE_NAME
from suite.gp import GPMeta

GP_OBJECT: GPMeta = get_gp_object(SCHEMA_NAME, TABLE_NAME, DATABASE_NAME)


@pytest.mark.slow
def test_create_table_and_column_list():
    create_gp_object()

    column_list = GP_OBJECT.columns

    assert column_list == ['"dttm_column"', '"id_column"', '"seq_column"', '"text_column"']


@pytest.mark.slow
def test_table_name():
    assert '{0}.{1}'.format(SCHEMA_NAME, TABLE_NAME) == GP_OBJECT.full_name_without_quote
    assert '{0}."{1}"'.format(SCHEMA_NAME, TABLE_NAME) == GP_OBJECT.full_name_without_schema_quote
    assert '"{0}"."{1}"'.format(SCHEMA_NAME, TABLE_NAME) == GP_OBJECT.full_name
    assert '"{0}"'.format(SCHEMA_NAME) == GP_OBJECT.schema
    assert '"{0}"'.format(TABLE_NAME) == GP_OBJECT.name
    assert '{0}'.format(TABLE_NAME) == GP_OBJECT.name_without_quote
    assert '"test_{0}"'.format(SCHEMA_NAME) == GP_OBJECT.schema_by_prefix('test_')
    assert 'test_{0}'.format(SCHEMA_NAME) == GP_OBJECT.schema_by_prefix_without_quote('test_')
    assert 't___{0}'.format(SCHEMA_NAME) == GP_OBJECT.schema_by_prefix_without_quote('t___')
    assert '"test{0}"'.format(SCHEMA_NAME) != GP_OBJECT.schema_by_prefix('test_')


@pytest.mark.slow
def test_child_partition():
    partition_list = GP_OBJECT.partitions

    assert partition_list == [
        {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first"'},
        {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_last"'},
    ]


@pytest.mark.slow
@pytest.mark.parametrize(
    'table_name,result',
    [
        (
                TABLE_NAME + '_1_prt_first',
                [
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2012"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2013"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2014"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2015"'},
                ]
        ),
        (
                TABLE_NAME + '_1_prt_last',
                [
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_last_2_prt_2012"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_last_2_prt_2013"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_last_2_prt_2014"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_last_2_prt_2015"'},
                ]
        )
    ]
)
def test_subpartition_list(table_name: str, result: list):
    gp_obj = get_gp_object(SCHEMA_NAME, table_name, DATABASE_NAME)
    partition_list = gp_obj.partitions

    assert partition_list == result


@pytest.mark.slow
def test_dependent_partition_filter():
    partition_list = GP_OBJECT.get_dependent_partition_by_filter_from_db({'list': ['first']}, {})

    assert partition_list == [{'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first"'}]


@pytest.mark.slow
@pytest.mark.parametrize(
    'table_name,partition,subpartition,result',
    [
        (
                TABLE_NAME + '_1_prt_first',
                {'list': ['first']},
                {'start_dttm': '2013-01-01 00:00:00', 'end_dttm': '2015-01-01 00:00:00'},
                [
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2013"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2014"'},
                    {'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_first_2_prt_2015"'}
                ]
        ),
        (
                TABLE_NAME + '_1_prt_last',
                {'list': ['last']},
                {'start_dttm': '2019-01-01 00:00:00', 'end_dttm': '2030-01-01 00:00:00'},
                []
        ),
        (
                TABLE_NAME + '_1_prt_last',
                {'list': ['last']},
                {'start_dttm': '2014-06-11 00:00:00', 'end_dttm': '2014-09-14 00:00:00'},
                [{'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + TABLE_NAME + '_1_prt_last_2_prt_2014"'}]
        )
    ]
)
def test_dependent_subpartition_filter(table_name: str, partition: dict, subpartition: dict, result: list):
    gp_obj = get_gp_object(SCHEMA_NAME, table_name, DATABASE_NAME)
    partition_list = gp_obj.get_dependent_partition_by_filter_from_db(partition, subpartition)

    assert partition_list == result


@pytest.mark.slow
def test_dependent_view():
    assert GP_OBJECT.views == [{'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + VIEW_NAME + '"'}]


@pytest.mark.slow
def test_dependent_sequence():
    assert GP_OBJECT.sequences == [{'schema': '"' + SCHEMA_NAME + '"', 'name': '"' + SEQUENCE_NAME + '"'}]


@pytest.mark.slow
def test_prefix():
    assert GP_OBJECT.schema_by_prefix('test_') == '"test_' + SCHEMA_NAME + '"'
    assert GP_OBJECT.schema_by_prefix('test__') == '"test__' + SCHEMA_NAME + '"'


@pytest.mark.slow
def test_drop_objects():
    drop_gp_object()
    assert not check_table_exists()
