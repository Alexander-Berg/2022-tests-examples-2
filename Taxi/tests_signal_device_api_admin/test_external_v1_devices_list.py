import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'external/signal-device-api-admin/v1/devices/list'

GNSS = {
    'lat': 53.3242,
    'lon': 34.9885,
    'accuracy_m': 3.0,
    'speed_kmph': 10.0,
    'direction_deg': 100.0,
}

RESPONSE1 = {
    'cursor': utils.get_encoded_external_devices_list_cursor('d1'),
    'devices': [
        {
            'device_id': 'd1',
            'device_serial_number': 'AB1',
            'status': {
                'status_at': '2020-03-02T01:00:00+00:00',
                'status': 'faced_away',
                'gnss': GNSS,
            },
        },
    ],
}

RESPONSE2 = {
    'cursor': utils.get_encoded_external_devices_list_cursor('d5'),
    'devices': [
        {
            'device_id': 'd2',
            'device_serial_number': 'AB2',
            'status': {
                'status_at': '2020-03-02T01:00:00+00:00',
                'status': 'closed',
                'gnss': GNSS,
            },
        },
        {
            'device_id': 'd5',
            'device_serial_number': 'AB5',
            'status': {
                'status_at': '2020-03-02T00:56:00+00:00',
                'status': 'turned_off',
                'gnss': GNSS,
            },
        },
    ],
}

RESPONSE3 = {
    'devices': [
        {
            'device_id': 'd6',
            'device_serial_number': 'AB6',
            'status': {
                'status_at': '2020-03-02T01:00:00+00:00',
                'status': 'offline',
            },
        },
        {
            'device_id': 'd7',
            'device_serial_number': 'AB7',
            'status': {
                'status_at': '2020-03-01T01:00:00+00:00',
                'status': 'offline',
                'gnss': GNSS,
            },
        },
        {
            'device_id': 'd8',
            'device_serial_number': 'AB8',
            'status': {
                'status_at': '2020-03-02T01:00:00+00:00',
                'status': 'turned_on',
                'gnss': GNSS,
            },
        },
    ],
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['statuses.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_STATUS_HISTORY_SETTINGS_V4={
        'pg_statuses_limit': 1500,
        'intervals_limit': 20,
        'supposed_statuses_interval_minutes': 1,
        'big_gap_length_minutes': 5,
        'default_request_period_hours': 168,
        'is_obsolete_response': False,
        'driver_statuses_interval_hours': 24,
    },
)
@pytest.mark.now('2020-03-02T01:00:00+00:00')
async def test_devices_list_pagination(taxi_signal_device_api_admin):
    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 1},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == RESPONSE1

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 2, 'cursor': response1.json()['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response2.text
    assert response2.json() == RESPONSE2

    response3 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 69, 'cursor': response2.json()['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response3.status_code == 200, response2.text
    assert response3.json() == RESPONSE3
