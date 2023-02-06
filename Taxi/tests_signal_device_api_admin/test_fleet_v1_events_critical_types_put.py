import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/events/critical/types'

EXPECTED_DB_ROWS1 = [('p1', ['driver_lost', 'seatbelt', 'tired'])]
EXPECTED_DB_ROWS2 = [
    ('p1', ['sleep', 'distraction']),
    ('p2', ['driver_lost', 'seatbelt', 'tired']),
]


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, expected_db_rows',
    [('p1', EXPECTED_DB_ROWS1), ('p2', EXPECTED_DB_ROWS2)],
)
async def test_v1_events_critical_types_put(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        expected_db_rows,
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

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    body = {'critical_types': ['driver_lost', 'seatbelt', 'tired']}
    response = await taxi_signal_device_api_admin.put(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT park_id, critical_event_types '
        'FROM signal_device_api.park_critical_event_types;',
    )
    db_rows = list(db)
    assert len(db_rows) == len(expected_db_rows)
    assert utils.unordered_lists_are_equal(db_rows, expected_db_rows)
