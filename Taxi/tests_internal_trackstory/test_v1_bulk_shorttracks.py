# pylint: disable=import-error
import datetime as dt

from geobus_tools import geobus  # noqa: F401 C5521
import pytest


def to_unix_time(timestamp):
    date = dt.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    return int(date.timestamp())


def _format_point(point):
    res = {
        'geodata': [
            {
                'positions': [
                    {
                        # 'direction': p['direction'],
                        'speed': pytest.approx(point['speed'], 1e-6),
                        'lat': point['lat'],
                        'lon': point['lon'],
                    },
                ],
                'time_shift': 0,
            },
        ],
        'sensors': {},
        'timestamp': point['timestamp'] * 1000,
    }
    if 'direction' in point:
        res['geodata'][0]['positions'][0]['direction'] = point['direction']
    if 'accuracy' in point:
        res['geodata'][0]['positions'][0]['accuracy'] = float(
            point['accuracy'],
        )
    return res


def _format_points(points):
    return [_format_point(p) for p in points]


def required_headers():
    return {'X-YaFts-Client-Service-Tvm': '123'}


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_exists(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track1 = [
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 55.720928,
        },
    ]

    track2 = [
        {
            'speed': 16.6,
            'lon': 38.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
        },
        {
            'speed': 16.6,
            'lon': 38.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 55.720928,
        },
    ]

    track_old1 = [
        {
            'speed': 16.6,
            'lon': 37.666666,
            'lat': 55.777777,
            'timestamp': to_unix_time('2022-01-01T00:00:02Z'),
            'direction': 1,
            'accuracy': 2,
        },
        {
            'speed': 16.6,
            'lon': 37.777777,
            'timestamp': to_unix_time('2022-01-01T00:00:09Z'),
            'lat': 55.666666,
            'direction': 2,
            'accuracy': 1,
        },
    ]
    track_old2 = [
        {
            'speed': 16.6,
            'lon': 37.666666,
            'lat': 56.777777,
            'timestamp': to_unix_time('2022-01-01T00:00:02Z'),
            'direction': 1,
            'accuracy': 2,
        },
        {
            'speed': 16.6,
            'lon': 37.777777,
            'timestamp': to_unix_time('2022-01-01T00:00:09Z'),
            'lat': 56.666666,
            'direction': 2,
            'accuracy': 1,
        },
    ]
    await shorttrack_payload_sender.send_universal_signals_payload(
        track_old1, 'Verified', 'db1_u1', 'test$positions$@0',
    )
    await shorttrack_payload_sender.send_universal_signals_payload(
        track_old2, 'Verified', 'db1_u2', 'test$positions$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track1, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )
    await shorttrack_payload_sender.send_universal_signals_payload(
        track2, 'AndroidNetwork', 'db1_u2', 'test$signals$@0',
    )

    request_body = {'uuids': ['db1_u1', 'db1_u2']}

    response = await taxi_internal_trackstory_adv.post(
        'v1/bulk/shorttrack',
        json=request_body,
        params={
            'pipeline': 'test',
            'sources': 'AndroidNetwork,AndroidGps,Invalid,Verified',
        },
        headers=required_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        'db1_u1': {
            'AndroidGps': _format_points(track1),
            'Verified': _format_points(track_old1),
            'AndroidNetwork': [],
        },
        'db1_u2': {
            'AndroidGps': [],
            'Verified': _format_points(track_old2),
            'AndroidNetwork': _format_points(track2),
        },
    }


async def test_wrong_pipeline(taxi_internal_trackstory_adv):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    request_body = {'uuids': ['db1_u1', 'db1_u2']}

    response = await taxi_internal_trackstory_adv.post(
        'v1/bulk/shorttrack',
        json=request_body,
        params={'pipeline': 'invalid', 'sources': 'AndroidGps,Invalid,Raw'},
        headers=required_headers(),
    )

    assert response.status_code == 404


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_dublicate_drivers(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track1 = [
        {
            'speed': 16.6,
            'lon': 36.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
            'lat': 54.720928,
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 55.720928,
        },
    ]

    track2 = [
        {
            'speed': 16.6,
            'lon': 34.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:05Z'),
            'lat': 53.720928,
        },
        {
            'speed': 16.6,
            'lon': 38.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 56.720928,
        },
    ]

    await shorttrack_payload_sender.send_universal_signals_payload(
        track1, 'Verified', 'db1_u1', 'test$signals$@0',
    )
    await shorttrack_payload_sender.send_universal_signals_payload(
        track2, 'Verified', 'db1_u2', 'test$signals$@0',
    )

    request_body = {'uuids': ['db1_u1', 'db1_u2', 'db1_u1']}

    response = await taxi_internal_trackstory_adv.post(
        'v1/bulk/shorttrack',
        json=request_body,
        params={'pipeline': 'test', 'sources': 'Verified'},
        headers=required_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        'db1_u1': {'Verified': _format_points(track1)},
        'db1_u2': {'Verified': _format_points(track2)},
    }
