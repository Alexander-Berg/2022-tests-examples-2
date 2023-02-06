import pytest

from tests_signal_device_configs import web_common

ENDPOINT = 'fleet/signal-device-configs/v1/events/fixated'

RESPONSE1 = {'event_types': ['tired', 'distraction']}

RESPONSE2 = {'event_types': ['tired', 'distraction', 'unusual_event_type']}

RESPONSE3 = {'event_types': ['tired', 'smoking', 'seatbelt']}


WHITELIST = [
    {
        'event_type': 'tired',
        'is_critical': True,
        'is_violation': False,
        'fixation_config_path': 'drowsiness.events.tired.enabled',
    },
    {
        'event_type': 'smoking',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'smoking.events.smoking.enabled',
    },
    {
        'event_type': 'seatbelt',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'seatbelt.events.seatbelt.enabled',
    },
    {
        'event_type': 'distraction',
        'is_critical': True,
        'is_violation': False,
        'fixation_config_path': 'distraction.events.distraction.enabled',
    },
    {
        'event_type': 'bad_camera_pose',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'general.events.bad_camera_pose.enabled',
    },
    {
        'event_type': 'something',
        'is_critical': False,
        'is_violation': False,
        'fixation_config_path': 'some.useless',
    },
]

UNUSUAL_EVENT_TYPE_INFO = {
    'event_type': 'unusual_event_type',
    'is_critical': False,
    'is_violation': False,
    'fixation_config_path': 'some.events.enabled',
}


@pytest.mark.pgsql(
    'signal_device_configs', files=['pg_signal_device_configs.sql'],
)
@pytest.mark.config(SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=WHITELIST)
@pytest.mark.parametrize(
    'park_id, expected_response',
    [
        ('p1', RESPONSE1),
        pytest.param(
            'p1',
            RESPONSE2,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=(
                    WHITELIST + [UNUSUAL_EVENT_TYPE_INFO]
                ),
            ),
        ),
        ('p2', RESPONSE3),
    ],
)
async def test_events_fixated_get(
        taxi_signal_device_configs, park_id, expected_response,
):
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_configs.get(ENDPOINT, headers=headers)
    assert response.status_code == 200, response.text
    assert sorted(response.json()['event_types']) == sorted(
        expected_response['event_types'],
    )
