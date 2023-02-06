from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/events/whitelist'


async def test_events_whitelist(taxi_signal_device_api_admin):
    response = await taxi_signal_device_api_admin.get(
        ENDPOINT, headers={**web_common.PARTNER_HEADERS_1},
    )
    assert response.status_code == 200, response.text
    assert set(response.json()['whitelist']) == set(
        ['sleep', 'distraction', 'driver_lost'],
    )
