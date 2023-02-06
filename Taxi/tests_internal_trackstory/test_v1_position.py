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
async def test_single(taxi_internal_trackstory_adv, shorttrack_payload_sender):
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

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    response = await taxi_internal_trackstory_adv.get(
        'v1/position',
        params={
            'pipeline': 'test',
            'uuid': 'db1_u1',
            'sources': 'AndroidGps,Invalid',
        },
        headers=required_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data == {'db1_u1': {'AndroidGps': _format_points(track[-1:])}}


@pytest.mark.now('2022-01-01T00:01:00Z')
async def test_max_age(
        taxi_internal_trackstory_adv, shorttrack_payload_sender,
):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    track = [
        {
            'speed': 16.6,
            'lon': 37.698035,
            'lat': 55.721591,
            'timestamp': to_unix_time('2022-01-01T00:00:30Z'),
        },
        {
            'speed': 16.6,
            'lon': 37.699561,
            'timestamp': to_unix_time('2022-01-01T00:00:35Z'),
            'lat': 55.720928,
        },
    ]

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_uu1', 'test$signals$@0',
    )

    response = await taxi_internal_trackstory_adv.get(
        'v1/position',
        params={
            'pipeline': 'test',
            'uuid': 'db1_uu1',
            'sources': 'AndroidGps',
            'max_age': 20,
        },
        headers=required_headers(),
    )

    assert response.status_code == 200

    data = response.json()
    assert data == {'db1_uu1': {'AndroidGps': []}}


async def test_wrong_pipeline(taxi_internal_trackstory_adv):
    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    response = await taxi_internal_trackstory_adv.get(
        'v1/position',
        params={
            'pipeline': 'invalid',
            'uuid': 'db1_uu1',
            'sources': 'AndroidGps',
        },
        headers=required_headers(),
    )

    assert response.status_code == 404


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_algorithm_immidiate(
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

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    response = await taxi_internal_trackstory_adv.get(
        'v1/position',
        params={
            'uuid': 'db1_u1',
            'pipeline': 'test',
            'sources': 'AndroidGps',
            'max_wait': 50,
        },
        headers=required_headers(),
    )

    assert with_retry_algo_iteration.times_called == 1

    assert response.status_code == 200

    data = response.json()

    assert data == {'db1_u1': {'AndroidGps': _format_points(track[-1:])}}


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_algorithm_one_source_one_retry(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
        testpoint,
):
    expected_data = {'remaining': [{'uuid': 'u1', 'dbid': 'db1'}], 'retry': 0}

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

    response_task = asyncio.create_task(
        taxi_internal_trackstory_adv.get(
            'v1/position',
            params={
                'uuid': 'db1_u1',
                'pipeline': 'test',
                'sources': 'AndroidGps',
                'max_wait': 50,
            },
            headers=required_headers(),
        ),
    )

    await with_retry_algo_iteration.wait_call()

    expected_data = {'remaining': [], 'retry': 1}

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    response = await response_task

    assert with_retry_algo_iteration.times_called == 1

    assert response.status_code == 200

    data = response.json()

    assert data == {'db1_u1': {'AndroidGps': _format_points(track[-1:])}}


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_algorithm_multiple_sources(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
        testpoint,
):
    expected_data = {'remaining': [{'uuid': 'u1', 'dbid': 'db1'}], 'retry': 0}

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

    response_task = asyncio.create_task(
        taxi_internal_trackstory_adv.get(
            'v1/position',
            params={
                'uuid': 'db1_u1',
                'pipeline': 'test',
                'sources': 'All',
                'max_wait': 150,
                'min_pos_req': 2,
            },
            headers=required_headers(),
        ),
    )

    await with_retry_algo_iteration.wait_call()

    expected_data['retry'] = 1

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    await with_retry_algo_iteration.wait_call()

    expected_data['remaining'] = []
    expected_data['retry'] = 2

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidNetwork', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidFused', 'db1_u1', 'test$signals$@0',
    )

    await with_retry_algo_iteration.wait_call()

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidPassive', 'db1_u1', 'test$signals$@0',
    )

    response = await response_task

    assert with_retry_algo_iteration.times_called == 0

    assert response.status_code == 200

    data = response.json()

    # minimum points requested is 2, but on the second try 3 were availible,
    # so all 3 are returned
    assert data == {
        'db1_u1': {
            'AndroidGps': _format_points(track[-1:]),
            'AndroidNetwork': _format_points(track[-1:]),
            'AndroidFused': _format_points(track[-1:]),
            'AndroidPassive': [],
            'Verified': [],
        },
    }


@pytest.mark.now('2022-01-01T00:00:11Z')
async def test_algorithm_multiple_sources_one_retry(
        taxi_internal_trackstory_adv,
        now,
        redis_store,
        mocked_time,
        shorttrack_payload_sender,
        testpoint,
):
    expected_data = {'remaining': [{'uuid': 'u1', 'dbid': 'db1'}], 'retry': 0}

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

    response_task = asyncio.create_task(
        taxi_internal_trackstory_adv.get(
            'v1/position',
            params={
                'uuid': 'db1_u1',
                'pipeline': 'test',
                'sources': 'All',
                'max_wait': 50,
            },
            headers=required_headers(),
        ),
    )

    await with_retry_algo_iteration.wait_call()

    expected_data['retry'] = 1

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidGps', 'db1_u1', 'test$signals$@0',
    )

    # only one retry
    await with_retry_algo_iteration.wait_call()

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidNetwork', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidFused', 'db1_u1', 'test$signals$@0',
    )

    await shorttrack_payload_sender.send_universal_signals_payload(
        track, 'AndroidPassive', 'db1_u1', 'test$signals$@0',
    )

    response = await response_task

    assert with_retry_algo_iteration.times_called == 0

    assert response.status_code == 200

    data = response.json()

    # minimum points requested is 2, but on the second try 3 were availible,
    # so all 3 are returned

    assert data == {
        'db1_u1': {
            'AndroidGps': _format_points(track[-1:]),
            'AndroidNetwork': [],
            'AndroidFused': [],
            'AndroidPassive': [],
            'Verified': [],
        },
    }
