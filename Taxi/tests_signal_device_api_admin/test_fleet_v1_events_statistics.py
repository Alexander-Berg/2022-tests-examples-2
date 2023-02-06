import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/events/statistics'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'park_id, device_id, period_from, period_to, expected_total',
    [
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            {'sleep': 1, 'driver_lost': 1},
        ),
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:30:00+00:00',
            {'sleep': 1, 'driver_lost': 1, 'distraction': 1},
        ),
    ],
)
async def test_v1_events_statistics(
        taxi_signal_device_api_admin,
        park_id,
        device_id,
        period_from,
        period_to,
        expected_total,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    thread_id = utils.to_base64(f'||{device_id}')
    query1 = {
        'period': {'from': period_from, 'to': period_to},
        'thread_id': thread_id,
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query1, headers=headers,
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == {'total': expected_total}

    query2 = {
        'period': {'from': period_from, 'to': period_to},
        'device_id': device_id,
    }
    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query2, headers=headers,
    )
    assert response2.status_code == 200, response2.text
    assert response2.json() == {'total': expected_total}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, device_id, driver_id, group_by,'
    'period_from, period_to, expected_total',
    [
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'd1',
            'device_id',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:30:00+00:00',
            {'distraction': 1},
        ),
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'd1',
            'driver_profile_id',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:30:00+00:00',
            {'distraction': 1},
        ),
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'd2',
            'device_id',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T13:00:00+00:00',
            {'sleep': 1, 'driver_lost': 1},
        ),
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            'd2',
            'driver_profile_id',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T13:00:00+00:00',
            {'sleep': 1, 'driver_lost': 1},
        ),
    ],
)
async def test_v1_events_statistics_by_choice(
        taxi_signal_device_api_admin,
        park_id,
        device_id,
        driver_id,
        group_by,
        period_from,
        period_to,
        expected_total,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    thread_id = utils.to_base64(f'{driver_id}||{device_id}')
    query1 = {
        'period': {'from': period_from, 'to': period_to},
        'thread_id': thread_id,
        'group_by': group_by,
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query1, headers=headers,
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == {'total': expected_total}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, group_by, period_from, period_to, expected_total',
    [
        (
            'p1',
            'device_id',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            {'sleep': 2, 'driver_lost': 1},
        ),
        (
            'p1',
            'driver_profile_id',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            {'sleep': 1, 'driver_lost': 1},
        ),
    ],
)
async def test_v1_events_statistics_with_no_constraints(
        taxi_signal_device_api_admin,
        park_id,
        group_by,
        period_from,
        period_to,
        expected_total,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    query1 = {
        'period': {'from': period_from, 'to': period_to},
        'group_by': group_by,
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query1, headers=headers,
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == {'total': expected_total}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_v1_events_statistics_wrong_request(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    query = {
        'period': {
            'from': '2019-02-27T11:00:00+00:00',
            'to': '2019-02-28T11:00:00+00:00',
        },
        'thread_id': utils.to_base64('||e58e753c44e548ce9edaec0e0ef9c8c1'),
        'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'p1'}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query, headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Can not have both thread_id and device_id in one request',
    }


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': [],
        'groups': web_common.DEMO_GROUPS,
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(  # noqa: E501 line too long
        ['tired', 'seatbelt'],
    ),
)
@pytest.mark.parametrize(
    'group_by, driver_id, period_from, period_to, expected_total',
    [
        (
            None,
            'dr1',
            '2020-02-20T00:00:00+03:00',
            '2020-02-26T23:59:59+03:00',
            {'tired': 1, 'kak teper zhit': 1},
        ),
        (
            'driver_profile_id',
            None,
            '2020-02-20T00:00:00+03:00',
            '2020-02-26T23:59:59+03:00',
            {'tired': 1, 'ushel v edu': 1, 'kak teper zhit': 1, 'sleep': 1},
        ),
    ],
)
async def test_demo_v1_events_statistics(
        taxi_signal_device_api_admin,
        group_by,
        driver_id,
        period_from,
        period_to,
        expected_total,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    query1 = {
        'period': {'from': period_from, 'to': period_to},
        'group_by': group_by,
    }
    if driver_id:
        thread_id = utils.to_base64(f'{driver_id}||')
        query1['thread_id'] = thread_id
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'no such park'}

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=query1, headers=headers,
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == {'total': expected_total}
