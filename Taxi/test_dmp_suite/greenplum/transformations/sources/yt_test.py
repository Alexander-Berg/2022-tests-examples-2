import mock
import pytest
from qb2.api.v1 import filters as qf

from connection import greenplum as gp
from dmp_suite import datetime_utils as dtu
from dmp_suite import yt
from dmp_suite.greenplum import (
    Int as GPInt, String as GPString, Datetime as GPDatetime, GPTable,
    resolve_meta
)
from dmp_suite.greenplum.transformations import Transformation
from dmp_suite.greenplum.transformations.sources.yt import (
    RawHistoryIncrementSliceSource, YtTableSourceException,
)
from dmp_suite.greenplum.transformations.sources.yt import (
    YtTableSource, RawHistoryIncrementSource
)
from dmp_suite.nile import NileBackend
from dmp_suite.yt import (
    Int as YTInt, String as YTString, Datetime as YTDatetime
)
from dmp_suite.yt import YTMeta, etl, datetime
from dmp_suite.yt.dyntable_operation import dynamic_table_loaders
from dmp_suite.yt.dyntable_operation import operations as dyn_op
from test_dmp_suite.yt import utils as yt_test_utils
from .tables import YTSourceTable, GPTargetTable
from ...utils import TestLayout, random_name


class DummyTransformation(Transformation):
    def run(self):
        pass


def prepare_yt_table_source(
        yt_data,
        stream_transformation=None,
        chunk_size=None,
):
    yt_meta = YTMeta(YTSourceTable)
    etl.init_target_table(yt_meta)
    etl.write_serialized_data(yt_meta.target_path(), yt_meta, yt_data)
    source = YtTableSource(yt_table=YTSourceTable, chunk_size=chunk_size) \
        .with_stream_transformation(stream_transformation) \
        .with_extractors(value_2=lambda d: 'abc')
    return source


def assert_source(source, expected, gp_table=GPTargetTable):
    transformation = DummyTransformation(source=source, target=gp_table)
    source.prepare(transformation)
    with source.source_table(transformation) as src, gp.connection.transaction():
        sql = 'select * from {table} order by id'.format(table=src)
        actual = [dict(row) for row in gp.connection.query(sql)]

    assert actual == expected


def upload_data_to_dyn_table(data, table):
    dynamic_table_loaders.upload(
        data=data,
        yt_table_or_meta=table,
        extractors={},
    )

    meta = yt.YTMeta(table)
    dyn_op.unmount_all_partitions(meta)
    dyn_op.mount_all_partitions(meta)


@pytest.mark.slow("gp")
def test_stg_table_source():
    source = prepare_yt_table_source(
        yt_data=[dict(id=1, value='abc'), dict(id=2, value='def'), dict(id=None, value='none')],
    )
    expected = [
        dict(id=1, value='abc', value_2='abc'),
        dict(id=2, value='def', value_2='abc'),
        dict(id=None, value='none', value_2='abc'),
    ]
    assert_source(source, expected)


@pytest.mark.slow("gp")
def test_stg_table_source_stream_transformation():

    def stream_transformation(stream):
        return stream.filter(qf.compare('value', '==', value='abc'))

    source = prepare_yt_table_source(
        yt_data=[dict(id=1, value='abc'), dict(id=2, value='def'), dict(id=None, value='abc')],
        stream_transformation=stream_transformation,
    )
    expected = [
        dict(id=1, value='abc', value_2='abc'),
        dict(id=None, value='abc', value_2='abc'),
    ]
    assert_source(source, expected)


@pytest.mark.slow("gp")
def test_empty_stg_table_source():
    source = prepare_yt_table_source(yt_data=[])
    assert_source(source, [])


@pytest.mark.slow("gp")
def test_stg_table_source_chunk_size():
    source = prepare_yt_table_source(
        yt_data=[dict(id=1, value='abc'), dict(id=2, value='def')],
        chunk_size=1000,
    )
    expected = [
        dict(id=1, value='abc', value_2='abc'),
        dict(id=2, value='def', value_2='abc'),
    ]
    assert_source(source, expected)


data = [
    dict(id=1,
         value='abc',
         utc_created_dttm=datetime(year=2020, month=1, day=1),
         utc_updated_dttm=datetime(year=2020, month=1, day=1)
         ),
    dict(id=2,
         value='def',
         utc_created_dttm=datetime(year=2020, month=1, day=1),
         utc_updated_dttm=datetime(year=2021, month=1, day=1)
         )
]

expected_period_by_updated = [
    dict(id=1,
         value='abc',
         utc_created_dttm=datetime(year=2020, month=1, day=1),
         utc_updated_dttm=datetime(year=2020, month=1, day=1),
         ),
]

expected_period_by_created = data


@pytest.mark.slow("gp")
@pytest.mark.parametrize('should_partition_yt, period_filter_field, data, expected, should_raise_value_error', [
    # with_period c непартицированной таблицей без указания period_filter_field должен выбросить ValueError
    (False, None, data, expected_period_by_updated, True),
    # with_period с непартицированной таблицей с указанием period_filter_field должен работать корректно
    (False, 'utc_updated_dttm', data, expected_period_by_updated, False),
    # with_period с партицированной таблицей без указания period_filter_field должен фильтровать по полю партиции
    (True, None, data, expected_period_by_updated, False),
    # with_period с партицированной таблицей с указанием period_filter_field должен фильтровать по period_filter_field
    (True, 'utc_created_dttm', data, expected_period_by_created, False),
])
def test_period(should_partition_yt, period_filter_field, data, expected, should_raise_value_error):

    @yt_test_utils.random_yt_table
    class DummyYtTable(yt.YTTable):
        __unique_keys__ = True
        __dynamic__ = True

        id = YTInt(sort_key=True, sort_position=0)
        value = YTString()
        utc_created_dttm = YTDatetime()
        utc_updated_dttm = YTDatetime()

    class GPDummyTable(GPTable):
        __layout__ = TestLayout(name=random_name(8))
        id = GPInt()
        value = GPString()
        utc_created_dttm = GPDatetime()
        utc_updated_dttm = GPDatetime()

    if should_partition_yt:
        setattr(DummyYtTable, "__partition_scale__", yt.ShortMonthPartitionScale('utc_updated_dttm'))

    upload_data_to_dyn_table(data, DummyYtTable)

    source = YtTableSource(DummyYtTable).with_period(
        period=dtu.Period('2019-12-01 00:00:00', '2020-12-01 00:00:00'),
        period_filter_field=period_filter_field
    )

    if should_raise_value_error:
        with pytest.raises(ValueError):
            assert_source(source, expected, gp_table=GPDummyTable)
    else:
        assert_source(source, expected, gp_table=GPDummyTable)


@pytest.mark.slow("gp")
def test_raw_history_slice_source():

    @yt_test_utils.random_yt_table
    class DummyYtTable(yt.YTTable):
        __unique_keys__ = True
        __dynamic__ = True
        __partition_scale__ = yt.ShortMonthPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        doc = yt.Any()

    data = [
        {
            'utc_updated_dttm': '2020-01-01 00:00:00',
            'id': 1,
            'doc': {
                'id': 1,
                'value': 'b',
                'value_2': '2020-01-01 00:00:00',
            },
        },
        {
            'utc_updated_dttm': '2020-01-01 00:00:00',
            'id': 2,
            'doc': {
                'id': 2,
                'value': 'b',
                'value_2': '2020-01-01 00:00:00',
            },
        },
        {
            'utc_updated_dttm': '2020-01-01 00:00:01',
            'id': 1,
            'doc': {
                'id': 1,
                'value': 'b',
                'value_2': '2020-01-01 00:00:01',
            },
        },
        {
            'utc_updated_dttm': '2019-01-01 00:00:01',
            'id': 3,
            'doc': {
                'id': 3,
                'value': 'b',
                'value_2': '2019-01-01 00:00:01',
            },
        },
    ]

    upload_data_to_dyn_table(data, DummyYtTable)

    source = RawHistoryIncrementSliceSource(DummyYtTable).with_period(
        dtu.Period('2019-12-01 00:00:00', '2020-12-01 00:00:00')
    )

    expected = [
        {
            'id': 1,
            'value': 'b',
            'value_2': '2020-01-01 00:00:01',
        },
        {
            'id': 2,
            'value': 'b',
            'value_2': '2020-01-01 00:00:00',
        },
    ]

    assert_source(source, expected)

    def transform(docs):
        for doc in docs:
            result = dict(doc)
            result['id'] = doc['id'] + 1
            yield result

    source = source.with_transform(transform)

    expected = [
        {
            'id': 2,
            'value': 'b',
            'value_2': '2020-01-01 00:00:01',
        },
        {
            'id': 3,
            'value': 'b',
            'value_2': '2020-01-01 00:00:00',
        },
    ]

    assert_source(source, expected)


def test_yt_table_source_yt_table():
    @yt_test_utils.random_yt_table
    class DummyYtTable(yt.YTTable):
        __unique_keys__ = True
        __dynamic__ = True
        __partition_scale__ = yt.ShortMonthPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        doc = yt.Any()

    assert YtTableSource(DummyYtTable).yt_table is DummyYtTable


@pytest.mark.slow('gp')
def test_static_table_raw_history_increment_source():
    @yt_test_utils.random_yt_table
    class DummyStaticYtTable(yt.YTTable):
        __unique_keys__ = True
        __partition_scale__ = yt.YearPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        doc = yt.Any()

    class DummyGPTable(GPTable):
        __layout__ = TestLayout(name=random_name(8))
        id = GPInt()

    gp_meta = resolve_meta(DummyGPTable)

    meta = YTMeta(DummyStaticYtTable)
    partition_meta = meta.with_partition('2020-01-01')
    etl.init_target_table(partition_meta)

    source = RawHistoryIncrementSource(
        DummyStaticYtTable,
        mr_use_threshold=100
    )

    assert source._has_static_partition()

    with mock.patch('dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource._serialize_tsv_in_memory') as in_mem, \
        mock.patch('dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource._serialize_tsv_mapreduce', return_value=('1','2')) as mr:
        source._serialize_tsv('1', gp_meta)
        assert in_mem.call_count == 0
        assert mr.call_count == 1


@pytest.mark.slow('gp')
def test_dynamic_table_raw_history_increment_source():
    @yt_test_utils.random_yt_table
    class DummyDynamicYtTable(yt.YTTable):
        __unique_keys__ = True
        __dynamic__ = True
        __partition_scale__ = yt.YearPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        doc = yt.Any()

    class DummyGPTable(GPTable):
        __layout__ = TestLayout(name=random_name(8))
        id = GPInt()

    gp_meta = resolve_meta(DummyGPTable)

    meta = YTMeta(DummyDynamicYtTable)
    partition_meta = meta.with_partition('2020-01-01')
    etl.init_target_table(partition_meta)

    source = RawHistoryIncrementSource(
        DummyDynamicYtTable,
        mr_use_threshold=100
    )

    assert not source._has_static_partition()

    with mock.patch(
        'dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource._serialize_tsv_in_memory',
        return_value=('11', '22')
    ) as in_mem, \
    mock.patch(
        'dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource._serialize_tsv_mapreduce',
        return_value=('1', '2')
    ) as mr, \
    mock.patch(
        'dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource.get_rows_count_to_load',
        return_value=1
    ):
        source._serialize_tsv('1', gp_meta)
        assert in_mem.call_count == 1
        assert mr.call_count == 0


@pytest.mark.slow('gp')
def test_dynamic_and_static_table_raw_history_increment_source():
    @yt_test_utils.random_yt_table
    class DummyDynamicYtTable(yt.YTTable):
        __unique_keys__ = True
        __dynamic__ = True
        __partition_scale__ = yt.YearPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        doc = yt.Any()

    @yt_test_utils.random_yt_table
    class DummyStaticYtTable(yt.YTTable):
        __unique_keys__ = True
        __partition_scale__ = yt.YearPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        doc = yt.Any()

    class DummyGPTable(GPTable):
        __layout__ = TestLayout(name=random_name(8))
        id = GPInt()

    gp_meta = resolve_meta(DummyGPTable)

    meta_dynamic = YTMeta(DummyDynamicYtTable)
    meta_static = YTMeta(DummyStaticYtTable)

    partition_meta = meta_static.with_partition('2020-01-01')
    etl.init_target_table(partition_meta)

    partition_meta = meta_dynamic.with_partition('2021-01-01')
    etl.init_target_table(partition_meta)

    source = RawHistoryIncrementSource(
        DummyStaticYtTable,
        mr_use_threshold=100
    )

    assert source._has_static_partition()

    with mock.patch('dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource._serialize_tsv_in_memory') as in_mem, \
        mock.patch('dmp_suite.greenplum.transformations.sources.yt.RawHistoryIncrementSource._serialize_tsv_mapreduce', return_value=('1','2')) as mr:
        source._serialize_tsv('1', gp_meta)
        assert in_mem.call_count == 0
        assert mr.call_count == 1


def test_raises_on_backend_conflict():

    class _DummyTableOne(yt.YTTable):
        __unique_keys__ = True
        __partition_scale__ = yt.YearPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)

    assert YtTableSource(_DummyTableOne).nile_backend_type is None
    assert RawHistoryIncrementSource(_DummyTableOne).nile_backend_type is None
    assert (
        RawHistoryIncrementSource(_DummyTableOne)
        .with_transform((lambda x: 'wow'))
        .nile_backend_type
    ) == NileBackend.YT

    class _DummyTableTwo(_DummyTableOne):
        dec = yt.Decimal(5, 3)

    assert YtTableSource(_DummyTableTwo).nile_backend_type == NileBackend.YQL
    assert RawHistoryIncrementSource(_DummyTableTwo).nile_backend_type == NileBackend.YQL

    with pytest.raises(YtTableSourceException):
        _ = (
            RawHistoryIncrementSource(_DummyTableTwo)
            .with_transform((lambda x: 'wow'))
        )


def test_extractor_patches():

    class _DummyTable(yt.YTTable):
        __unique_keys__ = True
        __partition_scale__ = yt.DayPartitionScale('utc_updated_dttm')

        utc_updated_dttm = yt.Datetime(sort_key=True, sort_position=0)
        id = yt.Int(sort_key=True, sort_position=1)
        native_dttm = yt.NativeDatetime()

    def _dummy(x, y):
        return 'dummy'

    assert (
        YtTableSource(_DummyTable)
        .extractors.get('native_dttm')
    )({'some_field': 0}, 'some_field') == '1970-01-01 00:00:00'

    assert (
        YtTableSource(_DummyTable)
        .with_extractors(native_dttm=_dummy)
        .extractors.get('native_dttm')
    ) is _dummy

    assert (
        YtTableSource(_DummyTable)
        .with_stream_transformation((lambda x: 'wow'))
        .extractors
    ) is None

    assert (
        YtTableSource(_DummyTable)
        .with_extractors(native_dttm=_dummy)
        .with_stream_transformation((lambda x: 'wow'))
        .extractors.get('native_dttm')
    ) is _dummy

    assert (
        RawHistoryIncrementSource(_DummyTable)
        .extractors.get('native_dttm')
    )({'some_field': 0}, 'some_field') == '1970-01-01 00:00:00'

    assert (
        RawHistoryIncrementSource(_DummyTable)
        .with_stream_transformation((lambda x: 'wow'))
        .extractors
    ) is None

    assert (
        RawHistoryIncrementSource(_DummyTable)
        .with_transform((lambda x: 'wow'))
        .extractors
    ) is None

    assert (
        RawHistoryIncrementSource(_DummyTable)
        .with_extractors(native_dttm=_dummy)
        .with_stream_transformation((lambda x: 'wow'))
        .extractors.get('native_dttm')
    ) is _dummy
