from nile.api.v1 import (
    MockCluster,
    Record,
)
from nile.local.sink import ListSink
from nile.local.source import StreamSource

from dmp_suite.nile import cluster_utils as cu


def test_meld():
    initial_data = [
        Record(id='00001', dttm='2018-01-01 10:00:00', value=1),
        Record(id='00002', dttm='2018-01-01 11:30:00', value=2)
    ]

    update_data = [
        Record(id='00000', dttm='2018-01-01 09:00:00', value=0),
        Record(id='00001', dttm='2018-01-01 10:30:00', value=3),
        Record(id='00002', dttm='2018-01-01 11:00:00', value=4),
        Record(id='00003', dttm='2018-01-01 12:00:00', value=5)
    ]

    cluster = MockCluster()
    job = cluster.job('test_pins_mapper')

    initial_stream = job.table('stub_1').label('input')
    update_stream = job.table('stub_2').label('update-input')

    result_data = []

    cu.meld(
        [initial_stream, update_stream],
        unique_key='id',
        priority_key='dttm',
        priority_mode='min'
    ).sort('id').label('result')

    job.local_run(
        sources={
            'input': StreamSource(initial_data),
            'update-input': StreamSource(update_data),
        },
        sinks={
            'result': ListSink(result_data),
        }
    )

    assert len(result_data) == 4
    assert result_data[0]['id'] == '00000'
    assert result_data[1]['id'] == '00001'
    assert result_data[2]['id'] == '00002'
    assert result_data[3]['id'] == '00003'

    assert result_data[0]['dttm'] == '2018-01-01 09:00:00'
    assert result_data[1]['dttm'] == '2018-01-01 10:00:00'
    assert result_data[2]['dttm'] == '2018-01-01 11:00:00'
    assert result_data[3]['dttm'] == '2018-01-01 12:00:00'

    assert result_data[0]['value'] == 0
    assert result_data[1]['value'] == 1
    assert result_data[2]['value'] == 4
    assert result_data[3]['value'] == 5
