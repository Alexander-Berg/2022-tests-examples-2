import inspect
from unittest import TestCase

import copy
import os
import pytest
from mock import patch
from nile.api.v1 import Record, extractors as ne, filters as nf
from nile.api.v1.clusters import MockCluster
from nile.api.v1.local import StreamSource, ListSink
from yt.yson.yson_types import YsonUnicode

import dmp_suite.yt.operation as op
from dmp_suite import datetime_utils as dtu, scales
from dmp_suite.common_utils import deep_update_dict
from dmp_suite.datetime_utils import Period
from dmp_suite.exceptions import (
    MissingTablesError,
    UnsupportedTableError
)
from dmp_suite.nile import cluster_utils
from dmp_suite.yt import NotLayeredYtLayout, NotLayeredYtTable, MonthPartitionScale, Datetime, YTMeta, etl
from test_dmp_suite.testing_utils import NileJobTestCase, JsonFileFormat


class Table(NotLayeredYtTable):
    __layout__ = NotLayeredYtLayout('same', 'path')
    __partition_scale__ = MonthPartitionScale('partition_key')
    partition_key = Datetime()


class TableRange(Table):
    __layout__ = NotLayeredYtLayout('test_period_range_path_stream/same', 'path')


class UnpartitionedTable(NotLayeredYtTable):
    dttm = Datetime()
    __layout__ = NotLayeredYtLayout('same/path', 'some_table')


class ClusterUtilsTest(TestCase):
    def test_format_range_path(self):
        self.assertEqual(
            cluster_utils.format_range_path('/some/folder', ['2017-01-01']),
            '/some/folder/{2017-01-01}'
        )
        self.assertEqual(
            cluster_utils.format_range_path('/some/folder/', ['2017-01-01']),
            '/some/folder/{2017-01-01}'
        )
        self.assertEqual(
            cluster_utils.format_range_path(
                '/some/folder/',
                ['2017-01-01', 'deleted']
            ),
            '/some/folder/{2017-01-01,deleted}'
        )
        with self.assertRaises(ValueError):
            cluster_utils.format_range_path('/some/folder', [])

    def test_period_range_path(self):
        meta = YTMeta(Table)

        period = Period('2017-09-12', '2017-11-23')
        self.assertEqual(
            cluster_utils.range_path_by_meta(meta, period),
            meta.target_folder_path + '/{2017-09-01,2017-10-01,2017-11-01}'
        )

        period = Period('2017-12-12', '2018-01-23')
        self.assertEqual(
            cluster_utils.range_path_by_meta(meta, period),
            meta.target_folder_path + '/{2017-12-01,2018-01-01}'
        )

        period = Period('2017-11-12', '2017-11-23')
        self.assertEqual(
            cluster_utils.range_path_by_meta(meta, period),
            meta.target_folder_path + '/{2017-11-01}'
        )

        period = Period('2017-11-12', '2017-11-12')
        self.assertEqual(
            cluster_utils.range_path_by_meta(meta, period),
            meta.target_folder_path + '/{2017-11-01}'
        )

        period = Period('2017-11-12 12:12:12', '2017-11-12 12:13:13')
        self.assertEqual(
            cluster_utils.range_path_by_meta(meta, period),
            meta.target_folder_path + '/{2017-11-01}'
        )


@pytest.mark.parametrize('kwargs, cluster_partitions, expected', [
    (
        dict(yt_table=YTMeta(Table), start='2018-01-01', end='2018-01-01'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(yt_table=Table, start='2018-01-02', end='2018-01-03'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(yt_table=Table, start='2018-01-01', end='2018-01-31'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(yt_table=Table, start='2018-01-01', end='2018-02-01'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(yt_table=Table, start='2018-01-12', end='2018-02-15'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(yt_table=Table, start='2018-01-31', end='2018-02-15'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(yt_table=Table, start='2018-01-31', end='2018-10-23'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(yt_table=Table, start='2018-02-21', end=None),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-02-01,2018-03-01}'
    ),
    (
        dict(yt_table=Table, start=None, end='2018-04-21'),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01,2018-03-01}'
    ),
    (
        dict(yt_table=Table, start=None, end=None),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01,2018-03-01}'
    ),
    (
        dict(yt_table=Table, start='2018-04-01', end='2018-04-15'),
        ['2018-01-01', '2018-02-01'],
        MissingTablesError
    ),
    (
        dict(yt_table=UnpartitionedTable, start='2018-01-31', end='2018-10-23'),
        ['2018-01-01', '2018-02-01'],
        UnsupportedTableError
    ),
])
def test_range_path(kwargs, cluster_partitions, expected):
    with patch('dmp_suite.nile.cluster_utils.op.get_yt_children',
               return_value=[YsonUnicode(t) for t in cluster_partitions]):  # type: ignore
        if inspect.isclass(expected) and issubclass(expected, BaseException):
            with pytest.raises(expected):
                cluster_utils.range_path(**kwargs)
        else:
            assert cluster_utils.range_path(**kwargs) == expected


@pytest.mark.parametrize('kwargs, cluster_partitions, expected', [
    (
        dict(start='2018-01-01', end='2018-01-01'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(start='2018-01-02', end='2018-01-03'),
        ['2018-01-01', '2018-02-01'],
        # Внимание! пропущена 2018-01-01, хотя для YTMeta возращается
        MissingTablesError
    ),
    (
        dict(start='2018-01-01', end='2018-01-31'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(start='2018-01-01', end='2018-02-01'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(start='2018-01-12', end='2018-02-15'),
        ['2018-01-01', '2018-02-01'],
        # Внимание! отсутствует 2018-01-01, хотя для YTMeta возращается
        '//dummy/same/path/{2018-02-01}'
    ),
    (
        dict(start='2018-01-31', end='2018-02-15'),
        ['2018-01-01', '2018-02-01'],
        # Внимание! отсутствует 2018-01-01, хотя для YTMeta возращается
        '//dummy/same/path/{2018-02-01}'
    ),
    (
        dict(start='2018-01-31', end='2018-10-23'),
        ['2018-01-01', '2018-02-01'],
        # Внимание! отсутствует 2018-01-01, хотя для YTMeta возращается
        '//dummy/same/path/{2018-02-01}'
    ),
    (
        dict(start='2018-02-21', end=None),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        # Внимание! отсутствует 2018-02-01, хотя для YTMeta возращается
        '//dummy/same/path/{2018-03-01}'
    ),
    (
        dict(start=None, end='2018-04-21'),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01,2018-03-01}'
    ),
    (
        dict(start=None, end=None),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01,2018-03-01}'
    ),
    (
        dict(start='2018-04-01', end='2018-04-15'),
        ['2018-01-01', '2018-02-01'],
        MissingTablesError
    ),
])
def test_range_folder(kwargs, cluster_partitions, expected):
    folder_path = '//dummy/same/path'
    with patch('dmp_suite.nile.cluster_utils.op.get_yt_children',
               return_value=cluster_partitions):
        if inspect.isclass(expected) and issubclass(expected, BaseException):
            with pytest.raises(expected):
                cluster_utils.range_folder(folder_path, **kwargs)
        else:
            assert cluster_utils.range_folder(folder_path, **kwargs) == expected


@pytest.mark.parametrize('kwargs, cluster_partitions, expected', [
    (
        dict(start='2018-01-01', end='2018-01-01'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(start='2018-01-02', end='2018-01-03'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(start='2018-01-01', end='2018-01-31'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01}'
    ),
    (
        dict(start='2018-01-01', end='2018-02-01'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(start='2018-01-12', end='2018-02-15'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(start='2018-01-31', end='2018-02-15'),
        ['2018-01-01', '2018-02-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01}'
    ),
    (
        dict(start='2018-02-21', end=None),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-02-01,2018-03-01}'
    ),
    (
        dict(start=None, end='2018-04-21'),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01,2018-03-01}'
    ),
    (
        dict(start=None, end=None),
        ['2018-01-01', '2018-02-01', '2018-03-01'],
        '//dummy/same/path/{2018-01-01,2018-02-01,2018-03-01}'
    ),
    (
        dict(start='2018-04-01', end='2018-04-15'),
        ['2018-01-01', '2018-02-01'],
        MissingTablesError
    )
])
def test_range_scaled_folder(kwargs, cluster_partitions, expected):
    folder_path = '//dummy/same/path'
    kwargs = dict(
        scale=scales.month,
        date_formatter=lambda d: dtu.format_date(dtu.get_start_of_month(d)),
        **kwargs
    )
    with patch('dmp_suite.nile.cluster_utils.op.get_yt_children',
               return_value=cluster_partitions):
        if inspect.isclass(expected) and issubclass(expected, BaseException):
            with pytest.raises(expected):
                cluster_utils.range_scaled_folder(folder_path, **kwargs)
        else:
            assert cluster_utils.range_scaled_folder(folder_path, **kwargs) == expected


@pytest.mark.slow
def test_period_range_path_stream():
    meta = YTMeta(Table)
    for partition in ('2019-08-01', '2019-09-01', '2019-10-01'):
        meta_with_partition = meta.with_partition(partition)
        etl.init_target_table(meta_with_partition)
        partition_period = Period(dtu.get_start_of_month(partition), dtu.get_end_of_month(partition))
        data = [{'partition_key': dtu.format_datetime(hour)} for hour in partition_period.split_in_hours()]
        op.write_yt_table(meta_with_partition.target_path(), data)

    period = Period('2019-09-29 13:00:00', '2019-10-01 15:00:00')
    expected_data = [{'partition_key': dtu.format_datetime(hour)} for hour in period.split_in_hours()]

    with op.get_temp_table() as tmp:
        job = etl.cluster_job(meta)
        cluster_utils.period_range_stream(meta, period, job) \
            .put(tmp, merge_strategy='never')
        job.run()

        actual_data = sorted(op.read_yt_table(tmp), key=lambda x: x.get('partition_key'))

        assert expected_data == actual_data, \
            'Expected data is different from actual:\nexpected\n{},\nactual\n{}'.format(
                expected_data, actual_data
            )


@pytest.mark.slow
def test_period_range_path_stream_unpartitioned():
    meta = YTMeta(UnpartitionedTable)
    etl.init_target_table(meta)
    for partition in ('2019-08-01', '2019-09-01', '2019-10-01'):
        partition_period = Period(dtu.get_start_of_month(partition), dtu.get_end_of_month(partition))
        data = [{'dttm': dtu.format_datetime(hour)} for hour in partition_period.split_in_hours()]
        op.write_yt_table(meta.target_path(), data, append=True)

    period = Period('2019-09-29 13:00:00', '2019-10-01 15:00:00')
    expected_data = [{'dttm': dtu.format_datetime(hour)} for hour in period.split_in_hours()]

    with op.get_temp_table() as tmp:
        job = etl.cluster_job(meta)
        cluster_utils.period_range_stream(meta, period, job, by_field='dttm') \
            .put(tmp, merge_strategy='never')
        job.run()

        actual_data = sorted(op.read_yt_table(tmp), key=lambda x: x.get('dttm'))

        assert expected_data == actual_data, \
            'Expected data is different from actual:\nexpected\n{},\nactual\n{}'.format(
                expected_data, actual_data
            )


class ConditionalTransformationTest(NileJobTestCase):
    def test_transform_if(self):
        def process_even(stream):
            return stream.project(ne.all(), f=ne.custom(lambda x: x // 2))

        def process_odd(stream):
            return stream.project(ne.all(), f=ne.custom(lambda x: 3 * x + 1))

        process = cluster_utils.transform_if(
            nf.custom(lambda x: x % 2 == 0),
            process_even,
            process_odd,
        )

        job = MockCluster().job()

        job.table("dummy").label("input").call(process).label("result")

        self.assertCorrectLocalRun(
            job,
            sources={
                "input": StreamSource([
                    Record(x=4),
                    Record(x=5),
                ])
            },
            expected_sinks={
                "result": StreamSource([
                    Record(x=4, f=2),
                    Record(x=5, f=16),
                ])
            }
        )


class BetweenValuesTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_simple(self):
        pfx = 'cluster_utils/between_values'
        job = MockCluster().job()
        t = job.table('///dummy').label('in')
        t.filter(cluster_utils.between_values('dt', '2018-01-01', '2018-01-03')).label('out')
        t.put('///dummy')
        self.assertCorrectLocalRun(
            job,
            sources={"in": os.path.join(pfx, "in.json")},
            expected_sinks={"out": os.path.join(pfx, "out.json")},
        )


class BetweenFieldsTest(NileJobTestCase):
    file_format = JsonFileFormat()

    def test_simple(self):
        pfx = 'cluster_utils/between_fields'
        job = MockCluster().job()
        t = job.table('///dummy').label('in')
        t.filter(cluster_utils.between_fields('dt', 'start', 'end')).label('out')
        t.put('///dummy')
        self.assertCorrectLocalRun(
            job,
            sources={"in": os.path.join(pfx, "in.json")},
            expected_sinks={"out": os.path.join(pfx, "out.json")},
        )


def test_combine_source_streams():
    job = MockCluster().job()

    @cluster_utils.applicable_period(end="2019-08-03")
    def old_records(period, stream):
        return stream.project(
            processor=ne.const("old"),
            start=ne.const(dtu.format_datetime(period.start)),
            end=ne.const(dtu.format_datetime(period.end)),
        )

    @cluster_utils.applicable_period(start="2019-08-04")
    def new_records(period, stream):
        return stream.project(
            processor=ne.const("new"),
            start=ne.const(dtu.format_datetime(period.start)),
            end=ne.const(dtu.format_datetime(period.end)),
        )

    s = job.table("singleton").label("singleton")
    cluster_utils.combine_sources(
        [old_records, new_records], dtu.date_period("2019-07-20", "2019-08-20"), s
    ).label("result")
    result = []
    job.local_run(
        sources={"singleton": StreamSource([Record()])},
        sinks={"result": ListSink(result)},
    )
    assert sorted(result) == sorted([
        Record(processor="old", start="2019-07-20 00:00:00", end="2019-08-03 23:59:59"),
        Record(processor="new", start="2019-08-04 00:00:00", end="2019-08-20 23:59:59"),
    ])


@pytest.mark.parametrize(
    "given_period, given_input, expect_result",
    [
        pytest.param(
            dtu.date_period("2019-07-20", "2019-08-20"),
            [Record(dttm="2019-07-22 00:00:00"), Record(dttm="2019-08-15 00:00:00")],
            [
                Record(dttm="2019-07-22 00:00:00", transformed_flg=True),
                Record(dttm="2019-08-15 00:00:00"),
            ],
            id="transform_partial",
        ),
        pytest.param(
            dtu.date_period("2019-07-20", "2019-08-02"),
            [Record(dttm="2019-07-22 00:00:00"), Record(dttm="2019-08-01 00:00:00")],
            [
                Record(dttm="2019-07-22 00:00:00", transformed_flg=True),
                Record(dttm="2019-08-01 00:00:00", transformed_flg=True),
            ],
            id="transform_all",
        ),
        pytest.param(
            dtu.date_period("2019-08-05", "2019-08-20"),
            [Record(dttm="2019-08-06 00:00:00"), Record(dttm="2019-08-15 00:00:00")],
            [
                Record(dttm="2019-08-06 00:00:00"),
                Record(dttm="2019-08-15 00:00:00"),
            ],
            id="transform_none",
        ),
    ],
)
def test_apply_only_when_needed(given_period, given_input, expect_result):
    @cluster_utils.applicable_period(end="2019-08-03")
    def legacy_transformation(stream, period):
        return stream.project(ne.all(), transformed_flg=ne.const(True))

    job = MockCluster().job()
    (
        job.table("source")
        .label("source")
        .call(
            cluster_utils.apply_only_when_needed(
                legacy_transformation, by_field="dttm"
            ),
            given_period,
        )
        .project(ne.all())
        .label("result")
    )

    result = []
    job.local_run(
        sources={"source": StreamSource(given_input)},
        sinks={"result": ListSink(result)},
    )
    assert sorted(result) == sorted(expect_result)


@pytest.mark.parametrize(
    "cont_1,cont_2",
    [
        ({'a': {'alpha': 5}}, {'b': 17}),
        ({1: 100, 2: 200, 3: 300}, {2: {15: 100}}),
    ]
)
def test_nile_nesting(cont_1, cont_2):
    """
    On each level assert that _nile_settings is
    correctly updated by patch_nile_settings(...).
    """
    true_cont_1 = copy.deepcopy(cont_1)
    true_cont_2 = copy.deepcopy(cont_1)
    deep_update_dict(true_cont_2, cont_2)
    assert cluster_utils._nile_settings.environment_extras == {}
    with cluster_utils.patch_nile_settings(environment_extras=cont_1):
        assert cluster_utils._nile_settings.environment_extras == true_cont_1
        with cluster_utils.patch_nile_settings(environment_extras=cont_2):
            assert cluster_utils._nile_settings.environment_extras == true_cont_2
        assert cluster_utils._nile_settings.environment_extras == true_cont_1
    assert cluster_utils._nile_settings.environment_extras == {}


def test_nile_backend_update():
    assert cluster_utils._nile_settings.nile_backend_type is None
    with cluster_utils.patch_nile_settings(nile_backend_type=cluster_utils.NileBackend.YQL):
        assert cluster_utils._nile_settings.nile_backend_type == cluster_utils.NileBackend.YQL
        with cluster_utils.patch_nile_settings(nile_backend_type=cluster_utils.NileBackend.YT):
            assert cluster_utils._nile_settings.nile_backend_type == cluster_utils.NileBackend.YT
        assert cluster_utils._nile_settings.nile_backend_type == cluster_utils.NileBackend.YQL
    assert cluster_utils._nile_settings.nile_backend_type is None
