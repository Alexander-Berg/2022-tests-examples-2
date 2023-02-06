import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/events/critical/types'

RESPONSE1 = {'critical_types': ['distraction', 'sleep']}
RESPONSE2 = {
    'critical_types': ['tired', 'eyeclosed', 'distraction', 'seatbelt'],
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'seatbelt',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'eyeclosed',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'tired',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'sleep',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'distraction',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, expected_response', [('p1', RESPONSE1), ('p2', RESPONSE2)],
)
async def test_v1_events_critical_types_get(
        taxi_signal_device_api_admin, park_id, expected_response, mockserver,
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
    response = await taxi_signal_device_api_admin.get(
        ENDPOINT, headers=headers,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert utils.unordered_lists_are_equal(
        response_json['critical_types'], expected_response['critical_types'],
    )
