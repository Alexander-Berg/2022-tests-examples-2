import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/events/seen'

EVENT_IDS = [
    '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    '44b3d7ec-30f6-43cf-94a8-911bc8fe404c',
]


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_ok_seen(taxi_signal_device_api_admin, pgsql, mockserver):
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
        json={'event_ids': EVENT_IDS, 'park_id': 'p1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT public_event_id, is_seen FROM signal_device_api.events')
    for row in db:
        if row[0] in EVENT_IDS:
            assert row[1]
        else:
            assert not row[1]
