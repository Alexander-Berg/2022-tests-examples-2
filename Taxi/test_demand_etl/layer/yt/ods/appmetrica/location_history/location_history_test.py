# coding: utf-8
from pprint import pformat

import pytest
from nile.api.v1 import MockCluster, Record
from nile.api.v1.local import StreamSource, ListSink

from demand_etl.layer.yt.ods.appmetrica_device.device_geolocation_prolonged.loader import build_increment


@pytest.mark.parametrize(
    'source_events, expected_increment',
    [
        pytest.param(
            [
                Record(
                    utc_event_dt='2019-07-02',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_event_dt='2019-07-03',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                ),
            ],
            [
                Record(
                    utc_dt='2019-07-02',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-03',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                )
            ],
            id='Event not prolonged'
        ),
        pytest.param(
            [
                Record(
                    utc_event_dt='2019-05-02',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_event_dt='2019-07-14',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                ),
            ],
            [
                Record(
                    utc_dt='2019-07-01',
                    device_lat=None,
                    device_lon=None,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-02',
                    device_lat=None,
                    device_lon=None,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-03',
                    device_lat=None,
                    device_lon=None,
                    appmetrica_device_id='aaa'
                )
            ],
            id='Events behind and far off'
        ),
        pytest.param(
            [
                Record(
                    utc_event_dt='2019-07-16',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_event_dt='2019-07-17',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                ),
            ],
            [],
            id='Events far off'
        ),
        pytest.param(
            [
                Record(
                    utc_event_dt='2019-06-25',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_event_dt='2019-07-03',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                ),
            ],
            [
                Record(
                    utc_dt='2019-07-01',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-02',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-03',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                )
            ],
            id='One event prolonged'
        ),
        pytest.param(
            [
                Record(
                    utc_event_dt='2019-06-24',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_event_dt='2019-07-03',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                ),
            ],
            [
                Record(
                    utc_dt='2019-07-01',
                    device_lat=55.05,
                    device_lon=43.02,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-02',
                    device_lat=None,
                    device_lon=None,
                    appmetrica_device_id='aaa'
                ),
                Record(
                    utc_dt='2019-07-03',
                    device_lat=100.35,
                    device_lon=12.02,
                    appmetrica_device_id='aaa'
                )
            ],
            id='One event prolonged to week, not week+1'
        ),
    ]
)
def test_increment_build(source_events, expected_increment):
    start_dt = '2019-07-01'
    end_dt = '2019-07-03'

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_increment = []
    job.table('stub') \
        .label('source_events') \
        .call(build_increment, start_dt, end_dt) \
        .label('actual_increment')
    job.local_run(
        sources={'source_events': StreamSource(source_events)},
        sinks={'actual_increment': ListSink(actual_increment)}
    )

    actual_increment = sorted(actual_increment, key=lambda rec: (rec.get('appmetrica_device_id'), rec.get('utc_dt')))

    assert expected_increment == actual_increment, \
        'Expected increment is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat(expected_increment), pformat(actual_increment)
        )
