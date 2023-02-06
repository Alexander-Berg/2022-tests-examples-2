import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/driver/status-history/intervals'

DRIVER_PROFILES_LIST_WITH_DRIVER = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': ' Petr ',
                'middle_name': ' D` ',
                'last_name': ' Ivanov ',
                'id': 'd1',
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

FULL_24_HOURS_RESPONSE = {
    'intervals': [
        {
            'work_status': 'offline',
            'start_at': '2020-11-26T09:20:03+00:00',
            'end_at': '2020-11-26T18:00:00+00:00',
        },
        {
            'work_status': 'online',
            'start_at': '2020-11-26T18:00:00+00:00',
            'end_at': '2020-11-27T06:30:00+00:00',
        },
        {
            'work_status': 'on_order',
            'start_at': '2020-11-27T06:30:00+00:00',
            'end_at': '2020-11-27T07:30:00+00:00',
        },
        {
            'work_status': 'busy',
            'start_at': '2020-11-27T07:30:00+00:00',
            'end_at': '2020-11-27T09:20:03+00:00',
        },
    ],
}

EMPTY_CONTRACTOR_STATUS_HISTORY_RESPONSE = {
    'contractors': [{'park_id': 'p1', 'profile_id': 'd1', 'events': []}],
}


@pytest.mark.parametrize(
    'driver_id, body, no_events, expected_code, expected_response',
    [
        ('d1', {}, False, 200, FULL_24_HOURS_RESPONSE),
        (
            'd1',
            {
                'period': {
                    'from': '2020-11-26T09:20:03+00:00',
                    'to': '2020-11-27T09:20:03+00:00',
                },
            },
            True,
            200,
            {
                'intervals': [
                    {
                        'work_status': 'offline',
                        'start_at': '2020-11-26T09:20:03+00:00',
                        'end_at': '2020-11-27T09:20:03+00:00',
                    },
                ],
            },
        ),
        (
            'd1',
            {
                'period': {
                    'from': '2020-11-26T09:20:03+00:00',
                    'to': '2020-11-27T09:20:03+00:00',
                },
                'cursor': utils.get_encoded_dev_stathist_cursor(
                    '2020-11-26T09:20:03+0000',
                ),
            },
            True,
            400,
            None,
        ),
        (
            'd1',
            {
                'period': {
                    'from': '2020-11-26T09:20:03+00:00',
                    'to': '2020-11-27T09:20:03+00:00',
                },
                'cursor': utils.get_encoded_dev_stathist_cursor(
                    '2019-11-26T09:20:03+0000',
                ),
            },
            True,
            400,
            None,
        ),
        (
            'd1',
            {
                'period': {
                    'from': '2021-11-26T09:20:03+00:00',
                    'to': '2020-11-27T09:20:03+00:00',
                },
            },
            True,
            400,
            None,
        ),
        ('d2', {}, False, 404, []),
    ],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_STATUS_HISTORY_SETTINGS_V4={
        'pg_statuses_limit': 1500,
        'intervals_limit': 20,
        'supposed_statuses_interval_minutes': 1,
        'big_gap_length_minutes': 5,
        'default_request_period_hours': 24,
        'is_obsolete_response': False,
        'driver_statuses_interval_hours': 24,
    },
)
@pytest.mark.now('2020-11-27T09:20:03+00:00')
async def test_driver_status_history_intervals(
        taxi_signal_device_api_admin,
        parks,
        driver_id,
        body,
        no_events,
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

    @mockserver.json_handler('/contractor-status-history/events')
    def _get_events(request):
        if no_events:
            return EMPTY_CONTRACTOR_STATUS_HISTORY_RESPONSE
        return {
            'contractors': [
                {
                    'park_id': 'p1',
                    'profile_id': 'd1',
                    'events': [
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-26 18:00:00.0+00',
                            ),
                            'status': 'online',
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-27 06:30:00.0+00',
                            ),
                            'status': 'online',
                            'on_order': True,
                        },
                        {
                            'timestamp': utils.date_str_to_sec(
                                '2020-11-27 07:30:00.0+00',
                            ),
                            'status': 'busy',
                            'on_order': False,
                        },
                    ],
                },
            ],
        }

    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_WITH_DRIVER)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'driver_profile_id': driver_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json=body,
    )
    assert response.status_code == expected_code, response.text
    if response.status_code == 200:
        assert response.json() == expected_response, response.json()


CONTRACTOR_STATUS_HISTORY_RESPONSE2 = {
    'contractors': [
        {
            'park_id': 'p1',
            'profile_id': 'd1',
            'events': [
                {
                    'timestamp': utils.date_str_to_sec(
                        '2020-12-28 11:00:00.0+00',
                    ),
                    'status': 'online',
                },
                {
                    'timestamp': utils.date_str_to_sec(
                        '2020-12-28 17:30:00.0+00',
                    ),
                    'status': 'busy',
                    'on_order': False,
                },
            ],
        },
    ],
}

CONTRACTOR_STATUS_HISTORY_RESPONSE3 = {
    'contractors': [
        {
            'park_id': 'p1',
            'profile_id': 'd1',
            'events': [
                {
                    'timestamp': utils.date_str_to_sec(
                        '2020-12-27 12:30:00.0+00',
                    ),
                    'status': 'online',
                    'on_order': True,
                },
                {
                    'timestamp': utils.date_str_to_sec(
                        '2020-12-27 18:30:00.0+00',
                    ),
                    'status': 'busy',
                    'on_order': False,
                },
            ],
        },
    ],
}

EXPECTED_RESPONSE1 = {
    'intervals': [
        {
            'work_status': 'offline',
            'start_at': '2020-12-29T00:00:00+00:00',
            'end_at': '2020-12-30T00:00:00+00:00',
        },
    ],
    'cursor': utils.get_encoded_dev_stathist_cursor(
        '2020-12-29T00:00:00+0000',
    ),
}

EXPECTED_RESPONSE2 = {
    'intervals': [
        {
            'work_status': 'online',
            'start_at': '2020-12-28T11:00:00+00:00',
            'end_at': '2020-12-28T17:30:00+00:00',
        },
        {
            'work_status': 'busy',
            'start_at': '2020-12-28T17:30:00+00:00',
            'end_at': '2020-12-29T00:00:00+00:00',
        },
    ],
    'cursor': utils.get_encoded_dev_stathist_cursor(
        '2020-12-28T11:00:00+0000',
    ),
}

EXPECTED_RESPONSE3 = {
    'intervals': [
        {
            'work_status': 'on_order',
            'start_at': '2020-12-27T12:30:00+00:00',
            'end_at': '2020-12-27T18:30:00+00:00',
        },
        {
            'work_status': 'busy',
            'start_at': '2020-12-27T18:30:00+00:00',
            'end_at': '2020-12-28T11:00:00+00:00',
        },
    ],
    'cursor': utils.get_encoded_dev_stathist_cursor(
        '2020-12-27T12:30:00+0000',
    ),
}

EXPECTED_RESPONSE4 = {
    'intervals': [
        {
            'work_status': 'offline',
            'start_at': '2020-12-27T00:00:00+00:00',
            'end_at': '2020-12-27T12:30:00+00:00',
        },
    ],
}


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
async def test_driver_status_history_intervals_with_cursor(
        taxi_signal_device_api_admin, parks, mockserver,
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

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        return DRIVER_PROFILES_LIST_WITH_DRIVER

    @mockserver.json_handler('/contractor-status-history/events')
    def _get_events(request, test_number=[0]):  # pylint: disable=W0102
        answers = {
            1: EMPTY_CONTRACTOR_STATUS_HISTORY_RESPONSE,
            2: CONTRACTOR_STATUS_HISTORY_RESPONSE2,
            3: CONTRACTOR_STATUS_HISTORY_RESPONSE3,
            4: EMPTY_CONTRACTOR_STATUS_HISTORY_RESPONSE,
        }
        test_number[0] += 1
        return answers[test_number[0]]

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'driver_profile_id': 'd1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'period': {
                'from': '2020-12-27T00:00:00+00:00',
                'to': '2020-12-30T00:00:00+00:00',
            },
        },
    )
    assert response1.status_code == 200, response1.text
    assert response1.json() == EXPECTED_RESPONSE1, response1.json()

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'driver_profile_id': 'd1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'period': {
                'from': '2020-12-27T00:00:00+00:00',
                'to': '2020-12-30T00:00:00+00:00',
            },
            'cursor': EXPECTED_RESPONSE1['cursor'],
        },
    )
    assert response2.status_code == 200, response2.text
    assert response2.json() == EXPECTED_RESPONSE2, response2.json()

    response3 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'driver_profile_id': 'd1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'period': {
                'from': '2020-12-27T00:00:00+00:00',
                'to': '2020-12-30T00:00:00+00:00',
            },
            'cursor': EXPECTED_RESPONSE2['cursor'],
        },
    )
    assert response3.status_code == 200, response3.text
    assert response3.json() == EXPECTED_RESPONSE3, response3.json()

    response4 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'driver_profile_id': 'd1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'period': {
                'from': '2020-12-27T00:00:00+00:00',
                'to': '2020-12-30T00:00:00+00:00',
            },
            'cursor': EXPECTED_RESPONSE3['cursor'],
        },
    )
    assert response4.status_code == 200, response4.text
    assert response4.json() == EXPECTED_RESPONSE4, response4.json()
