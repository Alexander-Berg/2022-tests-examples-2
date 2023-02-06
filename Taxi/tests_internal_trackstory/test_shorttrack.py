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
                        'position': [point['lon'], point['lat']],
                    },
                ],
                'time_shift': 0,
            },
        ],
        'sensors': [],
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


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_two_channels_minimal(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
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

    track_old = [
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

    await shorttrack_payload_sender.send_universal_signals_payload(
        track_old, 'Verified', 'db1_u1', 'test$positions$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    request_body = {'sources': ['AndroidGps', 'Invalid', 'Verified']}

    response = await taxi_internal_trackstory_adv.post(
        'test/shorttrack',
        json=request_body,
        params={'uuid': 'u1', 'dbid': 'db1'},
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track),
            'Verified': _format_points(track_old),
        },
    ]


@pytest.mark.now('2022-01-01T00:01:00Z')
async def test_max_age(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.692343,
            'lat': 55.722466,
            'timestamp': to_unix_time('2022-01-01T00:00:25Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:35Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:45Z'),
            'lat': 55.720928,
        },
    ]

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    request_body = {'sources': ['AndroidGps'], 'max_age': 30000}

    response = await taxi_internal_trackstory_adv.post(
        'test/shorttrack',
        json=request_body,
        params={'uuid': 'u1', 'dbid': 'db1'},
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track[1:]),
        },
    ]


@pytest.mark.now('2022-01-01T00:01:00Z')
async def test_amount(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.692343,
            'lat': 55.722466,
            'timestamp': to_unix_time('2022-01-01T00:00:25Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:35Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:45Z'),
            'lat': 55.720928,
        },
    ]

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    request_body = {'sources': ['AndroidGps'], 'num_positions': 2}

    response = await taxi_internal_trackstory_adv.post(
        'test/shorttrack',
        json=request_body,
        params={'uuid': 'u1', 'dbid': 'db1'},
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track[1:]),
        },
    ]


@pytest.mark.now('2022-01-01T00:01:00Z')
async def test_max_age_and_less_amount(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.692343,
            'lat': 55.722466,
            'timestamp': to_unix_time('2022-01-01T00:00:25Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:35Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:45Z'),
            'lat': 55.720928,
        },
    ]

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    request_body = {
        'sources': ['AndroidGps'],
        'num_positions': 1,
        'max_age': 30000,
    }

    response = await taxi_internal_trackstory_adv.post(
        'test/shorttrack',
        json=request_body,
        params={'uuid': 'u1', 'dbid': 'db1'},
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track[2:]),
        },
    ]


@pytest.mark.now('2022-01-01T00:01:00Z')
async def test_max_age_and_more_amount(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.692343,
            'lat': 55.722466,
            'timestamp': to_unix_time('2022-01-01T00:00:25Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:35Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:45Z'),
            'lat': 55.720928,
        },
    ]

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    request_body = {
        'sources': ['AndroidGps'],
        'num_positions': 2,
        'max_age': 20000,
    }

    response = await taxi_internal_trackstory_adv.post(
        'test/shorttrack',
        json=request_body,
        params={'uuid': 'u1', 'dbid': 'db1'},
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track[2:]),
        },
    ]


async def test_wrong_pipeline(taxi_internal_trackstory_adv):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    request_body = {'sources': ['Verified']}

    response = await taxi_internal_trackstory_adv.post(
        'invalid_pipeline/shorttrack',
        json=request_body,
        params={'uuid': 'u1', 'dbid': 'db1'},
    )

    assert response.status_code == 400
