import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'internal/signal-device-api-admin/v1/driver/events'

GNSS_1 = {
    'lat': 54.99250000,
    'lon': 73.36861111,
    'speed_kmph': 34.437895,
    'accuracy_m': 0.61340,
    'direction_deg': 245.895,
}

EVENT_1 = {
    'park_id': 'p1',
    'id': '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_at': '2020-02-27T12:00:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_1,
    'vehicle': {'plate_number': 'K444AB55', 'id': 'c1'},
    'is_critical': True,
    'comments_info': {
        'comments_count': 1,
        'last_comment': {
            'id': '1',
            'text': 'cute',
            'created_at': '2020-08-08T15:00:00+00:00',
        },
    },
}

EVENT_2 = {
    'park_id': 'p1',
    'id': '3233d7ec-30f6-43cf-94a8-11dbv8ae404c',
    'event_at': '2020-02-27T12:00:00+00:00',
    'type': 'event',
    'gnss': GNSS_1,
    'is_critical': False,
    'comments_info': {
        'comments_count': 2,
        'last_comment': {
            'id': '3',
            'text': 'nice',
            'created_at': '2020-08-11T15:00:00+00:00',
        },
    },
}

EVENT_3 = {
    'park_id': 'p1',
    'id': '1233d7ec-30f6-43cf-94a8-11dbv8ae404c',
    'event_at': '2020-02-27T12:10:00+00:00',
    'type': 'seatbelt',
    'gnss': GNSS_1,
    'vehicle': {'plate_number': 'K123KK777', 'id': 'c2'},
    'is_critical': True,
    'comments_info': {'comments_count': 0},
}

EVENT_4 = {
    'park_id': 'p1',
    'id': '44b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_at': '2020-02-27T12:12:00+00:00',
    'type': 'event',
    'gnss': GNSS_1,
    'vehicle': {'plate_number': 'K444AB55', 'id': 'c1'},
    'is_critical': False,
    'comments_info': {'comments_count': 0},
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.config(SIGNALQ_DRIVERS_EVENTS_LIMIT=100)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'seatbelt',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'sleep',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, driver_profile_id, period_from, ' 'period_to, expected_events',
    [
        pytest.param(
            'p1',
            'd1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            [EVENT_4, EVENT_3, EVENT_1],
            marks=pytest.mark.config(
                SIGNALQ_DRIVERS_EVENTS_WHITELIST=[
                    'sleep',
                    'event',
                    'seatbelt',
                ],
            ),
            id='all in the whitelist',
        ),
        pytest.param(
            'p1',
            'd1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            [EVENT_4, EVENT_1],
            marks=pytest.mark.config(
                SIGNALQ_DRIVERS_EVENTS_WHITELIST=['sleep', 'event'],
            ),
            id='seatbelt is not in the whitelist',
        ),
        pytest.param(
            'p1',
            'd1',
            '2020-02-27T12:05:00+00:00',
            '2020-02-27T12:11:00+00:00',
            [EVENT_3],
            marks=pytest.mark.config(
                SIGNALQ_DRIVERS_EVENTS_WHITELIST=[
                    'sleep',
                    'event',
                    'seatbelt',
                ],
            ),
            id='period constraints',
        ),
        pytest.param(
            'p1',
            'd2',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            [EVENT_2],
            marks=pytest.mark.config(
                SIGNALQ_DRIVERS_EVENTS_WHITELIST=['event'],
            ),
            id='driver 2',
        ),
    ],
)
async def test_internal_driver_events(
        taxi_signal_device_api_admin,
        park_id,
        driver_profile_id,
        period_from,
        period_to,
        expected_events,
):
    query = {'period': {'from': period_from, 'to': period_to}}
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=query,
        headers=headers,
        params={'driver_profile_id': driver_profile_id},
    )
    assert response.status_code == 200, response.text
    assert response.json()['events'] == expected_events


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.config(SIGNALQ_DRIVERS_EVENTS_LIMIT=2)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'seatbelt',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'sleep',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
    SIGNALQ_DRIVERS_EVENTS_WHITELIST=['sleep', 'event', 'seatbelt'],
)
@pytest.mark.parametrize(
    'park_id, driver_profile_id, period_from, '
    'period_to, expected_events1, expected_events2',
    [
        (
            'p1',
            'd1',
            '2019-02-27T11:00:00+00:00',
            '2020-02-27T12:20:00+00:00',
            [EVENT_4, EVENT_3],
            [EVENT_1],
        ),
    ],
)
async def test_internal_driver_events_with_cursor(
        taxi_signal_device_api_admin,
        park_id,
        driver_profile_id,
        period_from,
        period_to,
        expected_events1,
        expected_events2,
):
    query = {'period': {'from': period_from, 'to': period_to}}
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=query,
        headers=headers,
        params={'driver_profile_id': driver_profile_id},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    last_event = expected_events1[-1]
    cursor = utils.get_encoded_events_cursor(
        last_event['event_at'], last_event['id'],
    )
    assert utils.decode_cursor_from_resp_json(
        response_json,
    ) == utils.decode_cursor_from_event(last_event)
    assert response.json() == {'events': expected_events1, 'cursor': cursor}

    query['cursor'] = cursor
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=query,
        headers=headers,
        params={'driver_profile_id': driver_profile_id},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'events': expected_events2}
