import contextlib
import inspect

import mock
import pytest
from pyspark.sql.functions import col

from dmp_suite.spark import create_spark_session
from dmp_suite.task.execution import run_task
from dmp_suite.yt import etl, YTMeta, ETLTable, table as yt
from dmp_suite.yt import operation as op
from dmp_suite.yt.task.etl import transform
from dmp_suite.yt.task.etl.external_transform import external_source
from dmp_suite.yt.task.etl.spark_transform import (
    spark_config,
    spark_source,
    filtered_date_range,
)
from dmp_suite.yt.task.processing import use_yt_complex_types
from test_dmp_suite.yt import utils
from test_dmp_suite.yt.task.etl.transform_test import read_actual_data
from test_dmp_suite.yt.task.etl.utils import (
    MockTask, Table, DttmTable,
    PartitionedTable, assert_filtered_date_range_partitioned,
    assert_filtered_date_range_non_partition,
)
from test_dmp_suite.testing_utils.spark_testing_utils import spark_session


table = utils.fixture_random_yt_table(Table)


@pytest.mark.slow
def test_spark_source(table, spark_session):
    @spark_source(data=table)
    def accessor(args, data):
        return data.select(
            col('b').alias('a'),
            col('a').alias('b')
        )

    env = transform.TransformationEnvironment(
        task=MockTask(),
    )
    source = accessor.get_value(None, env)
    etl.init_target_table(table)
    op.write_yt_table(YTMeta(table).target_path(), [dict(a=1, b=2)])
    path_factory = etl.temporary_buffer_table(table)
    session_patch = mock.patch(
        'dmp_suite.yt.task.etl.spark_transform.create_spark_session',
        return_value=contextlib.nullcontext(spark_session)
    )
    with session_patch:
        with source.source_table(path_factory) as src:
            assert [dict(a=2, b=1)] == list(op.read_yt_table(src))


@pytest.mark.parametrize('config_first, config, expected', [
    (True, dict(num_executors=3, cores_per_executor=5), dict(num_executors=3, cores_per_executor=5, app_name='Spark transformation task mock_task')),
    (False, dict(num_executors=3, cores_per_executor=5), dict(num_executors=3, cores_per_executor=5, app_name='Spark transformation task mock_task')),
    (True, dict(app_name='spark_task'), dict(app_name='spark_task')),
    (False, dict(app_name='spark_task'), dict(app_name='spark_task')),
    (True, dict(), dict(app_name='Spark transformation task mock_task')),
    (False, dict(), dict(app_name='Spark transformation task mock_task')),
])
def test_spark_config(table, config_first, config, expected):
    table_path = YTMeta(table).target_path()

    def accessor(args, dataframe):
        return dataframe

    def get_source(func, env):
        config_decorator = spark_config(**config)
        source_decorator = spark_source(dataframe=table_path)
        if config_first:
            accessor = config_decorator(func)
            accessor = source_decorator(accessor)
        else:
            accessor = source_decorator(func)
            accessor = config_decorator(accessor)
        return accessor.get_value(None, env)

    env = transform.TransformationEnvironment(task=MockTask())

    env.task.name = 'mock_task'
    source = get_source(accessor, env)
    patch_session = mock.patch('dmp_suite.yt.task.etl.spark_transform.create_spark_session')
    patch_transform_yt_etl = mock.patch('dmp_suite.yt.task.etl.transform.etl')
    with patch_session as session_mock, patch_transform_yt_etl:
        with source.source_table(contextlib.nullcontext('target')) as src:
            # если декоратор с конфигами применяется первым, то у декорируемой
            # ф-ции появляется доп атрибут
            assert hasattr(accessor, '__task_source_config__') is config_first
            assert session_mock.call_args[1] == expected


def test_spark_config_args_diff():
    session_args = set(inspect.getfullargspec(create_spark_session.__wrapped__).args)
    # что-то сомнительное
    session_args -= {'yt_proxy', 'spark_id'}
    spark_config_args = set(inspect.getfullargspec(spark_config).kwonlyargs)

    assert not spark_config_args.difference(session_args)
    assert not session_args.difference(spark_config_args)


dttm_table = utils.fixture_random_yt_table(DttmTable)
partitioned_table = utils.fixture_random_yt_table(PartitionedTable)


@pytest.mark.slow
def test_filtered_date_range_partitioned(partitioned_table, spark_session):

    @spark_source(data=filtered_date_range(partitioned_table))
    def accessor(args, data):
        return data.select('id')

    session_patch = mock.patch(
        'dmp_suite.yt.task.etl.spark_transform.create_spark_session',
        return_value=contextlib.nullcontext(spark_session)
    )
    with session_patch:
        assert_filtered_date_range_partitioned(partitioned_table, accessor)


@pytest.mark.slow
def test_filtered_date_range_non_partition(dttm_table, spark_session):

    @spark_source(data=filtered_date_range(dttm_table, by_field='dttm'))
    def accessor(args, data):
        return data.select('id')

    session_patch = mock.patch(
        'dmp_suite.yt.task.etl.spark_transform.create_spark_session',
        return_value=contextlib.nullcontext(spark_session)
    )
    with session_patch:
        assert_filtered_date_range_non_partition(dttm_table, accessor)


@pytest.mark.slow
def test_spark_transform_complex(spark_session):

    class _TableBlank(ETLTable):
        date = yt.Date(sort_key=True)
        decimal = yt.Decimal(5, 3)
        optional = yt.Optional(yt.String)
        optional_c = yt.Optional(yt.List[yt.Int])
        list = yt.List(yt.Int)
        listlist = yt.List(yt.List[yt.Int])
        struct = yt.Struct({'one': yt.Int, 'two': yt.List[yt.Int]})
        tuple = yt.Tuple((yt.Int, yt.String, yt.Double))
        variant_named = yt.VariantNamed({'one': yt.Int, 'two': yt.String})
        variant_unnamed = yt.VariantUnnamed((yt.Int, yt.String))
        dct = yt.Dict(yt.String, yt.Int)
        tagged = yt.Tagged('BAD', yt.String)

    @utils.random_yt_table
    class _TestTableOne(_TableBlank):
        pass

    @utils.random_yt_table
    class _TestTableTwo(_TableBlank):
        new_struct = yt.Struct({'one': yt.Int, 'two': yt.List[yt.Int]})
        new_dct = yt.Dict(yt.String, yt.Int)

    data = [
        {
            'date': '2020-08-10',
            'decimal': '10.200',
            'optional': None,
            'optional_c': [1, 2, 3],
            'list': [10, 20, 30],
            'listlist': [[1, 2, 3], [4, 5], [6]],
            'struct': {'one': 500, 'two': [15, 20]},
            'tuple': (3, 'dogs', 5.15),
            'variant_named': ('two', 'Gamgee'),
            'variant_unnamed': (1, 'Samwise'),
            'dct': {'foo': 7, 'boo': 13},
            'tagged': 'WOLF',
        }
    ]

    expected = [
        {
            'date': '2020-08-10',
            'decimal': b'\x80\x00\x27\xd8',
            'optional': None,
            'optional_c': [1, 2, 3],
            'list': [10, 20, 30],
            'listlist': [[1, 2, 3], [4, 5], [6]],
            'struct': {'one': 500, 'two': [15, 20]},
            'tuple': [3, 'dogs', 5.15],
            'variant_named': ['two', 'Gamgee'],
            'variant_unnamed': [1, 'Samwise'],
            'dct': [['foo', 7], ['boo', 13]],
            'tagged': 'WOLF',
            'new_struct': {'one': 500, 'two': [15, 20]},
            'new_dct': [['foo', 7], ['boo', 13]],
        }
    ]

    prepare_test_table_snapshot = transform.replace_by_snapshot(
        name='test_spark_type_v3',
        source=external_source(data),
        target_table=_TestTableOne,
    ).with_processing(
        use_yt_complex_types()
    )

    run_task(prepare_test_table_snapshot)

    @spark_source(t=_TestTableOne)
    def spark_data_source(_, t):
        return (
            t
            .withColumn("new_struct", t.struct)
            .withColumn("new_dct", t.dct)
        )

    spark_snapshot = transform.replace_by_snapshot(
        name='test_spark_type_v3',
        source=spark_data_source,
        target_table=_TestTableTwo,
    ).with_processing(
        use_yt_complex_types()
    )

    run_task(spark_snapshot)

    assert expected == read_actual_data(_TestTableTwo)
