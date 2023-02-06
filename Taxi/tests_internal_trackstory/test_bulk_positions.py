# pylint: disable=import-error
import asyncio
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

    request_body = {
        'contractor_ids': [
            {'uuid': 'u1', 'dbid': 'db1'},
            {'uuid': 'u2', 'dbid': 'db1'},
        ],
        'sources': ['AndroidGps', 'Invalid', 'AndroidNetwork', 'Verified'],
    }

    response = await taxi_internal_trackstory_adv.post(
        'test/bulk/positions', json=request_body,
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track1[-1:]),
            'Verified': _format_points(track_old1[-1:]),
            'AndroidNetwork': [],
        },
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u2'},
            'AndroidGps': [],
            'Verified': _format_points(track_old2[-1:]),
            'AndroidNetwork': _format_points(track2[-1:]),
        },
    ]


async def test_wrong_pipeline(taxi_internal_trackstory_adv):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    request_body = {
        'contractor_ids': [{'uuid': 'u1', 'dbid': 'db1'}],
        'sources': ['Verified'],
    }

    response = await taxi_internal_trackstory_adv.post(
        'invalid_pipeline/bulk/positions', json=request_body,
    )

    assert response.status_code == 400


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
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 55.720928,
        },
    ]

    track2 = [
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

    request_body = {
        'contractor_ids': [
            {'uuid': 'u1', 'dbid': 'db1'},
            {'uuid': 'u2', 'dbid': 'db1'},
            {'uuid': 'u1', 'dbid': 'db1'},
        ],
        'sources': ['Verified'],
    }

    response = await taxi_internal_trackstory_adv.post(
        'test/bulk/positions', json=request_body,
    )

    assert response.status_code == 200

    data = response.json()

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'Verified': _format_points(track1[-1:]),
        },
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u2'},
            'Verified': _format_points(track2[-1:]),
        },
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'Verified': _format_points(track1[-1:]),
        },
    ]


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_algorithm_first_try(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
        testpoint,
):
    expected_data = {'remaining': [], 'retry': 0}

    @testpoint('with_retry_algo_iteration')
    def with_retry_algo_iteration(data):
        assert data == expected_data

    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 55.720928,
        },
    ]

    request_body = {
        'contractor_ids': [
            {'uuid': 'u1', 'dbid': 'db1'},
            {'uuid': 'u2', 'dbid': 'db1'},
        ],
        'sources': ['All'],
        'algorithm': {
            'algorithm': 'WithRetry',
            'max_retries': 3,
            'timeout': 50,
            'min_positions_required_count': 2,
        },
    }

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u2', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidNetwork', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidFused', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidPassive', 'db1_u2', 'test$signals$@0',
    )

    response_task = asyncio.create_task(
        taxi_internal_trackstory_adv.post(
            'test/bulk/positions', json=request_body,
        ),
    )

    await with_retry_algo_iteration.wait_call()

    response = await response_task

    assert with_retry_algo_iteration.times_called == 0

    assert response.status_code == 200

    data = response.json()

    # minimum points requested is 2, but on the second try 3 were availible,
    # so all 3 are returned

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track[-1:]),
            'AndroidNetwork': _format_points(track[-1:]),
            'AndroidFused': _format_points(track[-1:]),
            'AndroidPassive': [],
            'Verified': [],
        },
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u2'},
            'AndroidGps': _format_points(track[-1:]),
            'AndroidNetwork': [],
            'AndroidFused': [],
            'AndroidPassive': _format_points(track[-1:]),
            'Verified': [],
        },
    ]


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_algorithm_multiple_sources(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
        testpoint,
):
    expected_data = {
        'remaining': [
            {'uuid': 'u1', 'dbid': 'db1'},
            {'uuid': 'u2', 'dbid': 'db1'},
        ],
        'retry': 0,
    }

    @testpoint('with_retry_algo_iteration')
    def with_retry_algo_iteration(data):
        assert sorted(data) == sorted(expected_data)

    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:10Z'),
            'lat': 55.720928,
        },
    ]

    request_body = {
        'contractor_ids': [
            {'uuid': 'u1', 'dbid': 'db1'},
            {'uuid': 'u2', 'dbid': 'db1'},
        ],
        'sources': ['All'],
        'algorithm': {
            'algorithm': 'WithRetry',
            'max_retries': 3,
            'timeout': 50,
            'min_positions_required_count': 2,
        },
    }

    response_task = asyncio.create_task(
        taxi_internal_trackstory_adv.post(
            'test/bulk/positions', json=request_body,
        ),
    )

    await with_retry_algo_iteration.wait_call()

    expected_data['retry'] = 1

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    await with_retry_algo_iteration.wait_call()

    expected_data['remaining'] = [{'uuid': 'u2', 'dbid': 'db1'}]
    expected_data['retry'] = 2

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u2', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidNetwork', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidFused', 'db1_u1', 'test$signals$@0',
    )

    await with_retry_algo_iteration.wait_call()

    expected_data['remaining'] = []
    expected_data['retry'] = 3

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidPassive', 'db1_u2', 'test$signals$@0',
    )

    await with_retry_algo_iteration.wait_call()

    response = await response_task

    assert with_retry_algo_iteration.times_called == 0

    assert response.status_code == 200

    data = response.json()

    # minimum points requested is 2, but on the second try 3 were availible,
    # so all 3 are returned

    assert data == [
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u1'},
            'AndroidGps': _format_points(track[-1:]),
            'AndroidNetwork': _format_points(track[-1:]),
            'AndroidFused': _format_points(track[-1:]),
            'AndroidPassive': [],
            'Verified': [],
        },
        {
            'contractor': {'dbid': 'db1', 'uuid': 'u2'},
            'AndroidGps': _format_points(track[-1:]),
            'AndroidNetwork': [],
            'AndroidFused': [],
            'AndroidPassive': _format_points(track[-1:]),
            'Verified': [],
        },
    ]
