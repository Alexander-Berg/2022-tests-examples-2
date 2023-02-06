import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/events/feed/total/devices'


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.parametrize(
    'park_id, body, expected_code, expected_response',
    [
        ('p1', {}, 200, {'threads_amount': 2}),
        (
            'p1',
            {'filter': {'event_types': ['distraction']}},
            200,
            {'threads_amount': 1},
        ),
        (
            'p1',
            {'filter': {'event_types': ['driver_lost']}},
            200,
            {'threads_amount': 0},
        ),
        (
            'p1',
            {
                'period': {
                    'from': '2020-02-28T10:00:00+00:00',
                    'to': '2021-04-10T00:00:00+00:00',
                },
            },
            200,
            {'threads_amount': 1},
        ),
        (
            'p1',
            {
                'period': {
                    'from': '2021-04-10T00:00:00+00:00',
                    'to': '2020-04-10T00:00:00+00:00',
                },
            },
            400,
            None,
        ),
    ],
)
async def test_ok_total_devices(
        taxi_signal_device_api_admin,
        park_id,
        body,
        expected_code,
        expected_response,
        mockserver,
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

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == expected_code, response.text
    if expected_code != 200:
        return
    assert response.json() == expected_response


ERROR_RESPONSE = {'code': 'bad_group', 'message': 'Incorrect group provided'}


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.parametrize(
    'park_id, body, expected_code, expected_response',
    [
        (
            'p1',
            {'filter': {'group_id': '635ffb7b-8c06-476d-a30a-4bc9ae65d272'}},
            200,
            {'threads_amount': 2},
        ),
        (
            'p1',
            {'filter': {'group_id': '3bd269aa-3aca-494b-8bbb-88f99847464a'}},
            200,
            {'threads_amount': 1},
        ),
        (
            'p1',
            {'filter': {'group_id': '29a168a6-2fe3-401d-9959-ba1b14fd4862'}},
            200,
            {'threads_amount': 0},
        ),
        (
            'p1',
            {'filter': {'group_id': '12bb68a6-aae3-421d-9119-ca1c14fd4862'}},
            400,
            ERROR_RESPONSE,
        ),
    ],
)
async def test_ok_total_devices_filter_group(
        taxi_signal_device_api_admin,
        park_id,
        body,
        expected_code,
        expected_response,
        mockserver,
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

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': [],
        'events': web_common.DEMO_EVENTS,
        'vehicles': [],
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
)
@pytest.mark.parametrize(
    'body, expected_code, expected_response',
    [
        ({}, 200, {'threads_amount': 2}),
        ({'filter': {'group_id': 'g1'}}, 200, {'threads_amount': 0}),
    ],
)
async def test_demo_ok_total_devices(
        taxi_signal_device_api_admin,
        body,
        expected_code,
        expected_response,
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

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
