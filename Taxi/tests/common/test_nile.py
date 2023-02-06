# coding: utf-8

import datetime

import pytest
import numpy as np
from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1 import filters as nf
from nile.api.v1.local import StreamSource, ListSink

from taxi.ml.nirvana.common.nile import dates
from taxi.ml.nirvana.common.nile import aggregators as pa
from taxi.ml.nirvana.common.nile import extractors as pe
from taxi.ml.nirvana.common.nile import filters as pf
from taxi.ml.nirvana.common.nile import mappers as pm


class TestDates:
    def test_range_1(self):
        value = dates.get_range('2019-01-02', '2019-01-04')
        assert value == ['2019-01-02', '2019-01-03', '2019-01-04']

    def test_range_2(self):
        value = dates.get_range(
            '2019-01-02', '2019-01-04', date_format='%Y-%m-01',
        )
        assert value == ['2019-01-01']


class TestExtractors:
    def test_is_none(self):
        extractor = pe.is_none('a')
        assert extractor(a=None)
        assert extractor(a=None, b=1)
        assert not extractor(a=0)
        assert not extractor(a=1)

    def test_is_not_none(self):
        extractor = pe.is_not_none('a')
        assert not extractor(a=None)
        assert not extractor(a=None, b=1)
        assert extractor(a=0)
        assert extractor(a=1)

    def test_fill_none(self):
        extractor = pe.fill_none('a', default_value=1)
        assert extractor(a=None) == 1
        assert extractor(a=None, b=1) == 1
        assert extractor(a=0) == 0
        assert extractor(a=1) == 1

    def test_fields_dict(self):
        extractor = pe.fields_dict('a', 'b')
        assert extractor(a=None, b=1) == dict(a=None, b=1)
        assert extractor(a=1, b=2) == dict(a=1, b=2)

    def test_ratio(self):
        extractor = pe.ratio('a', 'b')
        assert extractor(a=1, b=2) == 0.5
        assert extractor(a=0, b=2) == 0.0

    def test_optional_ratio(self):
        extractor = pe.optional_ratio('a', 'b')
        assert extractor(a=1, b=2) == 0.5
        assert extractor(a=0, b=2) == 0.0
        assert extractor(a=None, b=2) is None
        assert extractor(a=None, b=None) is None
        assert extractor(a=0, b=None) is None

    def test_optional_cast(self):
        extractor = pe.optional_cast('a', str)
        assert extractor(a=1, b=2) == '1'
        assert extractor(a=None, b=2) is None
        assert extractor(a=0.1, b=2) == '0.1'


class TestFilters:
    def test_between(self):
        func = pf.between(field='a', begin=1, end=3)
        assert not func(a=0)
        assert func(a=1)
        assert func(a=2)
        assert not func(a=3)
        assert not func(a=4)

    def test_ts_between(self):
        func = pf.ts_between(1546000000, 1547000000, ts_field='a')
        assert not func(a=1346398000)
        assert func(a=1546398000)
        assert not func(a=1846398000)

    def test_dttm_between(self):
        func = pf.dttm_between(
            begin=datetime.datetime(2019, 1, 2),
            end=datetime.datetime(2019, 1, 3),
            dt_field='a',
        )
        assert not func(a='2019-01-01 00:00:00')
        assert func(a='2019-01-02 12:00:00')
        assert not func(a='2019-01-04 00:00:00')

    def test_is_success_taxi_order(self):
        func = pf.is_success_taxi_order(
            status_field='a', taxi_status_field='b',
        )
        assert func(a=b'finished', b=b'complete')
        assert not func(a=b'finished1', b=b'complete')
        assert not func(a='finished', b='complete')
        assert not func(a=None, b=None)

        func = pf.is_success_taxi_order(
            status_field='a', taxi_status_field='b', ensure_binary=True,
        )
        assert func(a=b'finished', b=b'complete')
        assert not func(a=b'finished1', b=b'complete')
        assert func(a='finished', b='complete')
        assert not func(a=None, b=None)

    def test_sample_by_field(self):
        func = pf.sample_by_field(field_name='a', sample_prob=0.2)
        hits = 0
        for value in range(10000):
            hits += func(a=bytes(value))
        # 99% interval is 3 * sqrt(0.2*0.8/10000) = 0.012
        assert 1880 <= hits <= 2120


class TestMappers:
    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_create_bucketing_mapper(self):
        mapper = pm.create_bucketing_mapper(
            bucket_function=lambda record: record.a, buckets_count=3,
        )
        job = clusters.MockCluster().job()
        table0, table1, table2 = job.table('').label('input').map(mapper)
        table0.label('table0').put('output_table0')
        table1.label('table1').put('output_table1')
        table2.label('table2').put('output_table2')

        outputs = [[], [], []]
        job.local_run(
            sources={
                'input': StreamSource(
                    [Record(a=0, b=2), Record(a=0, b=1), Record(a=1, b=10)],
                ),
            },
            sinks={
                'table0': ListSink(outputs[0]),
                'table1': ListSink(outputs[1]),
                'table2': ListSink(outputs[2]),
            },
        )
        assert outputs == [
            [Record(a=0, b=2), Record(a=0, b=1)],
            [Record(a=1, b=10)],
            [],
        ]


class TestAggregators:
    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_list_(self):
        job = clusters.MockCluster().job()
        job.table('').label('input').groupby('key').aggregate(
            result_value=pa.list_('value'),
        ).label('output').put('output_table')
        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(key=0, value=1),
                        Record(key=0, value=2),
                        Record(key='0', value=3),
                        Record(key='0', value=1),
                        Record(key=b'0', value=4),
                        Record(key=b'0', value=1),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        key_2_record = {record.key: record for record in output}
        assert len(output) == 3
        assert sorted(key_2_record[0].result_value) == [1, 2]
        assert sorted(key_2_record['0'].result_value) == [1, 3]
        assert sorted(key_2_record[b'0'].result_value) == [1, 4]

    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_sum_mean(self):
        job = clusters.MockCluster().job()
        job.table('').label('input').groupby('key').aggregate(
            sum=pa.sum('value'), mean=pa.mean('value'),
        ).label('output').put('output_table')
        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(key=0, value=1),
                        Record(key=0, value=2),
                        Record(key='0', value=1),
                        Record(key='0', value=3),
                        Record(key=b'0', value=1),
                        Record(key=b'0', value=4),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        key_2_record = {record.key: record for record in output}
        assert len(output) == 3
        assert key_2_record[0].sum == 3
        assert key_2_record['0'].sum == 4
        assert key_2_record[b'0'].sum == 5
        assert key_2_record[0].mean == 1.5
        assert key_2_record['0'].mean == 2
        assert key_2_record[b'0'].mean == 2.5

    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_decimal_sum_mean(self):
        job = clusters.MockCluster().job()
        job.table('').label('input').groupby('key').aggregate(
            sum=pa.decimal_sum('value'), mean=pa.decimal_mean('value'),
        ).label('output').put('output_table')
        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(key=0, value=1),
                        Record(key=0, value=2),
                        Record(key='0', value=1),
                        Record(key='0', value=3),
                        Record(key=b'0', value=1),
                        Record(key=b'0', value=4),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        key_2_record = {record.key: record for record in output}
        assert len(output) == 3
        assert key_2_record[0].sum == '3'
        assert key_2_record['0'].sum == '4'
        assert key_2_record[b'0'].sum == '5'
        assert key_2_record[0].mean == '1.5'
        assert key_2_record['0'].mean == '2'
        assert key_2_record[b'0'].mean == '2.5'

    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_long_sum_mean(self):
        job = clusters.MockCluster().job()
        job.table('').label('input').groupby('key').aggregate(
            sum=pa.long_sum('value'), mean=pa.long_mean('value'),
        ).label('output').put('output_table')
        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(key=0, value=1),
                        Record(key=0, value=2),
                        Record(key='0', value=1),
                        Record(key='0', value=3),
                        Record(key=b'0', value=1),
                        Record(key=b'0', value=4),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        key_2_record = {record.key: record for record in output}
        assert len(output) == 3
        assert key_2_record[0].sum == '3'
        assert key_2_record['0'].sum == '4'
        assert key_2_record[b'0'].sum == '5'
        assert key_2_record[0].mean == '1.5'
        assert key_2_record['0'].mean == '2'
        assert key_2_record[b'0'].mean == '2.5'

    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_position_hits(self):
        job = clusters.MockCluster().job()
        job.table('').label('input').groupby().aggregate(
            recall_1=pa.position_hits('value', max_position=2),
            recall_2=pa.position_hits('value', max_position=None),
        ).label('output').put('output_table')
        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(value=1),
                        Record(value=None),
                        Record(value=1),
                        Record(),
                        Record(value=4),
                        Record(value=3),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        assert len(output) == 1
        assert output[0].recall_1 == {
            'total': 6,
            'not_none_total': 4,
            'cum_hits': [0, 2, 2],
            'hits': [0, 2, 0],
        }
        assert output[0].recall_2 == {
            'total': 6,
            'not_none_total': 4,
            'cum_hits': [0, 2, 2, 3, 4],
            'hits': [0, 2, 0, 1, 1],
        }

    @pytest.mark.filterwarnings('ignore::DeprecationWarning')
    def test_np_arr_sum_mean(self):
        job = clusters.MockCluster().job()

        def prepare(val):
            return np.array(val, dtype=np.float).tobytes()

        job.table('').label('input').groupby('key').aggregate(
            sum=pa.np_arr_sum('value', prepare_func=prepare, dtype=np.float),
            mean=pa.np_arr_mean('value', prepare_func=prepare, dtype=np.float),
        ).label('output').put('output_table')
        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(key=0, value=[1, 2]),
                        Record(key=0, value=[2, 4]),
                        Record(key='0', value=[1, 2]),
                        Record(key='0', value=[3, 6]),
                        Record(key=b'0', value=[1, 2]),
                        Record(key=b'0', value=[4, 8]),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        key_2_record = {record.key: record for record in output}

        def unpack(arr_bytes):
            return np.fromstring(arr_bytes, dtype=np.float)

        assert len(output) == 3
        assert (unpack(key_2_record[0].sum) == [3, 6]).all()
        assert (unpack(key_2_record['0'].sum) == [4, 8]).all()
        assert (unpack(key_2_record[b'0'].sum) == [5, 10]).all()
        assert (unpack(key_2_record[0].mean) == [1.5, 3]).all()
        assert (unpack(key_2_record['0'].mean) == [2, 4]).all()
        assert (unpack(key_2_record[b'0'].mean) == [2.5, 5]).all()

        @pytest.mark.filterwarnings('ignore::DeprecationWarning')
        def test_mode(self):
            job = clusters.MockCluster().job()

            job.table('').label('input').groupby('key').aggregate(
                mode=pa.mode('value'),
                mode_missing=pa.mode('value', missing=-1),
                mode_predicate=pa.mode(
                    'value', predicate=nf.custom(lambda value: value > 0),
                ),
            ).label('output').put('output_table')
            output = []
            job.local_run(
                sources={
                    'input': StreamSource(
                        [
                            Record(key=0),
                            Record(key=0),
                            Record(key=0),
                            Record(key=0, value=0),
                            Record(key=0, value=0),
                            Record(key=0, value=1),
                            Record(key=1, value=-3),
                            Record(key=1, value=-3),
                            Record(key=1, value=-2),
                            Record(key=1, value=-1),
                            Record(key=1),
                            Record(key=1),
                        ],
                    ),
                },
                sinks={'output': ListSink(output)},
            )
            key_2_record = {record.key: record for record in output}

            assert key_2_record[0].mode == 0
            assert key_2_record[0].mode_missing == -1
            assert key_2_record[0].mode_predicate == 1
            assert key_2_record[1].mode == -3
            assert key_2_record[1].mode_missing == -1
            assert 'mode_predicate' not in key_2_record[1]
