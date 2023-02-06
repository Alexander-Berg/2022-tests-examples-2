import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/dashboard/devices/statistics'

RESPONSE_P1_1 = {'amount': {'all': 1, 'active': 0}}
RESPONSE_P1_2 = {'amount': {'all': 3, 'active': 2}}
RESPONSE_P1_3 = {'amount': {'all': 4, 'active': 1}}
RESPONSE_P1_4 = {'amount': {'all': 3, 'active': 0}}

RESPONSE_P2_1 = {'amount': {'all': 1, 'active': 1}}
RESPONSE_P2_2 = {'amount': {'all': 1, 'active': 0}}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, expected_response',
    [
        (
            'p1',
            '2020-02-26T00:00:00+03',
            '2020-02-27T00:00:00+03',
            RESPONSE_P1_1,
        ),
        (
            'p1',
            '2020-02-27T00:00:00+03',
            '2020-02-28T00:00:00+03',
            RESPONSE_P1_2,
        ),
        (
            'p1',
            '2020-02-28T00:00:00+03',
            '2020-03-01T00:00:00+03',
            RESPONSE_P1_3,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03',
            '2020-03-02T00:00:00+03',
            RESPONSE_P1_4,
        ),
        (
            'p2',
            '2020-02-27T00:00:00+03',
            '2020-02-28T00:00:00+03',
            RESPONSE_P2_1,
        ),
        (
            'p2',
            '2020-02-28T22:00:00+03',
            '2020-03-01T22:00:00+03',
            RESPONSE_P2_2,
        ),
    ],
)
async def test_v1_dashboard_devices_statistics(
        taxi_signal_device_api_admin,
        park_id,
        period_from,
        period_to,
        expected_response,
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

    body = {'period': {'from': period_from, 'to': period_to}}
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


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
        'events': [],
        'vehicles': [],
        'groups': [],
        'drivers': [],
    },
)
async def test_demo_v1_dashboard_devices_statistics(
        taxi_signal_device_api_admin, mockserver,
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

    body = {
        'period': {
            'from': '2020-02-27T00:00:00+03',
            'to': '2020-02-28T00:00:00+03',
        },
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'no such park'}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'amount': {'all': 3, 'active': 2}}
