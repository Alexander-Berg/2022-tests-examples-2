import json

import pytest

SELECT_EVENTS = 'SELECT park_id, profile_id, status FROM deptrans.status_queue'


def _make_event(park_id, profile_id, status):
    return {
        'park_id': park_id,
        'profile_id': profile_id,
        'status': status,
        'updated_ts': '2020-12-15T21:56:18.0+03:00',
        'orders': [],
    }


@pytest.mark.parametrize(
    'event,enabled',
    [
        pytest.param(
            _make_event('park1', 'driver1', 'online'),
            True,
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                ),
                pytest.mark.geoareas(filename='geoareas.json'),
                pytest.mark.tariffs(filename='tariffs.json'),
            ],
            id='enabled',
        ),
        pytest.param(
            _make_event('park1', 'driver1', 'online'),
            False,
            marks=[
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                ),
            ],
            id='empty zone',
        ),
        pytest.param(
            _make_event('park1', 'driver1', 'online'),
            False,
            marks=[
                pytest.mark.geoareas(filename='geoareas.json'),
                pytest.mark.tariffs(filename='tariffs.json'),
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['econom'],
                    },
                ),
            ],
            id='disabled by zone',
        ),
        pytest.param(
            _make_event('park1', 'driver1', 'online'),
            False,
            marks=[
                pytest.mark.geoareas(filename='geoareas.json'),
                pytest.mark.tariffs(filename='tariffs.json'),
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                ),
            ],
            id='disabled by category',
        ),
        pytest.param(
            _make_event('park1', 'driver1', 'online'),
            False,
            marks=[
                pytest.mark.geoareas(filename='geoareas.json'),
                pytest.mark.tariffs(filename='tariffs.json'),
                pytest.mark.config(
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={
                        'supported_zones': ['moscow'],
                    },
                    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
                        'supported_categories': ['comfort'],
                    },
                ),
            ],
            id='disabled by category',
        ),
    ],
)
@pytest.mark.now('2020-12-15T21:00:00Z')
async def test_status_events_basic(
        taxi_deptrans_driver_status,
        pgsql,
        testpoint,
        driver_trackstory,
        driver_categories_api,
        event,
        enabled,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    response = await taxi_deptrans_driver_status.post(
        'tests/logbroker/messages',
        json={
            'consumer': 'deptrans-driver-status-consumer',
            'data': json.dumps(event),
            'topic': '/taxi/testing-contractor-statuses-events',
            'cookie': 'cookie',
        },
    )
    assert response.status_code == 200

    await commit.wait_call()
    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute(SELECT_EVENTS)
    rows = cursor.fetchall()
    if enabled:
        assert rows == [
            (event['park_id'], event['profile_id'], event['status']),
        ]
    else:
        assert not rows


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'suitable_events,unsuitable_by_zone,unsuitable_by_categories',
    [
        pytest.param(
            [
                ('park1', 'driver1', 'online'),
                ('park1', 'driver2', 'online'),
                ('park2', 'driver1', 'online'),
            ],
            [],
            [],
            id='all suitable',
        ),
        pytest.param(
            [('park1', 'driver1', 'online'), ('park2', 'driver1', 'online')],
            [('park1', 'driver2', 'online')],
            [],
            id='filter by zone',
        ),
        pytest.param(
            [('park1', 'driver1', 'online'), ('park2', 'driver1', 'online')],
            [],
            [('park1', 'driver2', 'online')],
            id='filter by categories',
        ),
        pytest.param(
            [('park2', 'driver1', 'online')],
            [('park1', 'driver1', 'online')],
            [('park1', 'driver2', 'online')],
            id='filter by zone and categories',
        ),
    ],
)
@pytest.mark.now('2020-12-15T21:00:00Z')
async def test_multiple_events(
        taxi_deptrans_driver_status,
        pgsql,
        testpoint,
        driver_trackstory,
        driver_categories_api,
        suitable_events,
        unsuitable_by_zone,
        unsuitable_by_categories,
):
    for event in unsuitable_by_zone:
        driver_trackstory.set_data(f'{event[0]}_{event[1]}', 27.5, 25.5)

    for event in unsuitable_by_categories:
        driver_categories_api.set_data(f'{event[0]}_{event[1]}', ['comfort'])

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    suitable_events_list = [_make_event(*event) for event in suitable_events]
    ussuitable_events_list = [
        _make_event(*event)
        for event in [*unsuitable_by_zone, *unsuitable_by_categories]
    ]
    all_events = suitable_events_list + ussuitable_events_list

    data = '\n'.join(json.dumps(event) for event in all_events)
    response = await taxi_deptrans_driver_status.post(
        'tests/logbroker/messages',
        json={
            'consumer': 'deptrans-driver-status-consumer',
            'data': data,
            'topic': '/taxi/testing-contractor-statuses-events',
            'cookie': 'cookie',
        },
    )
    assert response.status_code == 200

    await commit.wait_call()
    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute(SELECT_EVENTS)
    rows = cursor.fetchall()
    assert sorted(rows) == sorted(
        (event['park_id'], event['profile_id'], event['status'])
        for event in suitable_events_list
    )


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2020-12-15T21:00:00Z')
async def test_status_event_conflict_in_queue(
        taxi_deptrans_driver_status,
        pgsql,
        testpoint,
        driver_trackstory,
        driver_categories_api,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    first_driver_events = [
        _make_event('park1', 'driver1', 'online'),
        _make_event('park1', 'driver1', 'busy'),
        _make_event('park1', 'driver1', 'offline'),
    ]
    second_driver_events = [
        _make_event('park1', 'driver2', 'busy'),
        _make_event('park1', 'driver2', 'offline'),
        _make_event('park1', 'driver2', 'online'),
    ]
    for events in zip(first_driver_events, second_driver_events):
        data = '\n'.join(json.dumps(event) for event in events)
        response = await taxi_deptrans_driver_status.post(
            'tests/logbroker/messages',
            json={
                'consumer': 'deptrans-driver-status-consumer',
                'data': data,
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'cookie',
            },
        )
        assert response.status_code == 200

        await commit.wait_call()
        cursor = pgsql['deptrans_driver_status'].cursor()
        cursor.execute(SELECT_EVENTS)
        rows = cursor.fetchall()
        assert sorted(rows) == sorted(
            (event['park_id'], event['profile_id'], event['status'])
            for event in events
        )


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2020-12-15T21:00:00Z')
async def test_skip_on_error(
        taxi_deptrans_driver_status,
        pgsql,
        testpoint,
        driver_trackstory,
        driver_categories_api,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie'

    driver_categories_api.set_timeouts_count(2)

    events = [
        _make_event('park1', 'driver1', 'online'),
        _make_event('park1', 'driver2', 'busy'),
        _make_event('park1', 'driver1', 'offline'),
    ]

    data = '\n'.join(json.dumps(event) for event in events)
    response = await taxi_deptrans_driver_status.post(
        'tests/logbroker/messages',
        json={
            'consumer': 'deptrans-driver-status-consumer',
            'data': data,
            'topic': '/taxi/testing-contractor-statuses-events',
            'cookie': 'cookie',
        },
    )
    assert response.status_code == 200

    await commit.wait_call()
    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute(SELECT_EVENTS)
    rows = cursor.fetchall()
    assert sorted(rows) == sorted(
        (event['park_id'], event['profile_id'], event['status'])
        for event in events[1:]
    )
