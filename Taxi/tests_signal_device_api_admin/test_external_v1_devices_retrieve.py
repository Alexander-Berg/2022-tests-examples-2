import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'external/signal-device-api-admin/v1/devices/retrieve'

GNSS = {
    'lat': 53.3242,
    'lon': 34.9885,
    'accuracy_m': 3.0,
    'speed_kmph': 10.0,
    'direction_deg': 100.0,
}

RESPONSE = {
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
        {
            'device_id': 'd7',
            'device_serial_number': 'AB7',
            'status': {
                'status_at': '2020-03-01T01:00:00+00:00',
                'status': 'offline',
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
async def test_devices_retrieve(taxi_signal_device_api_admin):
    serial_numbers = ['AB1', 'AB7', 'AB1337', 'AB3']
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'serial_numbers': serial_numbers},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE
