import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/dashboard/events/statistics'

RESPONSE1 = {
    'critical': {'amount': 0},
    'non_critical': {'amount': 0},
    'details': [
        {'amount': 0, 'event_type': 'tired', 'is_critical': True},
        {'amount': 0, 'event_type': 'eyeclosed', 'is_critical': True},
        {'amount': 0, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 0, 'event_type': 'seatbelt', 'is_critical': True},
    ],
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 0, 'event_type': 'trash_frames'},
    ],
}

RESPONSE2 = {
    'critical': {'amount': 0},
    'details': [
        {'amount': 0, 'event_type': 'tired', 'is_critical': True},
        {'amount': 0, 'event_type': 'eyeclosed', 'is_critical': True},
        {'amount': 0, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 0, 'event_type': 'seatbelt', 'is_critical': True},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
    ],
    'non_critical': {'amount': 1},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 0, 'event_type': 'trash_frames'},
    ],
}

RESPONSE3 = {
    'critical': {'amount': 1},
    'details': [
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 0, 'event_type': 'tired', 'is_critical': True},
        {'amount': 0, 'event_type': 'eyeclosed', 'is_critical': True},
        {'amount': 0, 'event_type': 'seatbelt', 'is_critical': True},
        {'amount': 2, 'event_type': 'sleep', 'is_critical': False},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': False},
        {'amount': 1, 'event_type': 'trash_frames', 'is_critical': False},
    ],
    'non_critical': {'amount': 5, 'diff': 400.0},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'trash_frames'},
    ],
}

RESPONSE4_WITH_WHITELIST = {
    'critical': {'amount': 1},
    'details': [
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 0, 'event_type': 'tired', 'is_critical': True},
        {'amount': 0, 'event_type': 'eyeclosed', 'is_critical': True},
        {'amount': 0, 'event_type': 'seatbelt', 'is_critical': True},
        {'amount': 2, 'event_type': 'sleep', 'is_critical': False},
    ],
    'non_critical': {'amount': 2},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'trash_frames'},
    ],
}

RESPONSE5_WITH_CRITICAL_EVENTS = {
    'critical': {'amount': 3},
    'details': [
        {'amount': 2, 'event_type': 'sleep', 'is_critical': True},
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
        {'amount': 1, 'event_type': 'trash_frames', 'is_critical': False},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': False},
    ],
    'non_critical': {'amount': 3, 'diff': 200.0},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'trash_frames'},
    ],
}

RESPONSE6_WITH_BOTH = {
    'critical': {'amount': 3},
    'details': [
        {'amount': 2, 'event_type': 'sleep', 'is_critical': True},
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
    ],
    'non_critical': {'amount': 0},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'trash_frames'},
    ],
}

RESPONSE7_EMPTY_ERRORS = {
    'critical': {'amount': 0, 'diff': -100.0},
    'details': [
        {'amount': 0, 'event_type': 'tired', 'is_critical': True},
        {'amount': 0, 'event_type': 'eyeclosed', 'is_critical': True},
        {'amount': 0, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 0, 'event_type': 'seatbelt', 'is_critical': True},
    ],
    'non_critical': {'amount': 0, 'diff': -100.0},
    'device_errors': [],
}

RESPONSE8_WITH_DEVICE_ERRORS_NON_CRITICAL = {
    'critical': {'amount': 1},
    'details': [
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 0, 'event_type': 'tired', 'is_critical': True},
        {'amount': 0, 'event_type': 'eyeclosed', 'is_critical': True},
        {'amount': 0, 'event_type': 'seatbelt', 'is_critical': True},
        {'amount': 2, 'event_type': 'sleep', 'is_critical': False},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': False},
    ],
    'non_critical': {'amount': 4, 'diff': 300.0},
    'device_errors': [{'amount': 0, 'event_type': 'bad_camera_pose'}],
}

RESPONSE9_WITH_DEVICE_ERRORS_CRITICAL = {
    'critical': {'amount': 4},
    'details': [
        {'amount': 2, 'event_type': 'sleep', 'is_critical': True},
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': True},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
    ],
    'non_critical': {'amount': 1, 'diff': 0.0},
    'device_errors': [{'amount': 0, 'event_type': 'bad_camera_pose'}],
}

RESPONSE10_WITH_TWO_DEVICE_ERRORS = {
    'critical': {'amount': 4},
    'details': [
        {'amount': 2, 'event_type': 'sleep', 'is_critical': True},
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': True},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
        {
            'amount': 1,
            'event_type': 'bad_camera_pose1337',
            'is_critical': False,
        },
    ],
    'non_critical': {'amount': 2, 'diff': 100.0},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'bad_camera_pose1337'},
    ],
}

RESPONSE11_WITH_THREE_DEVICE_ERRORS = {
    'critical': {'amount': 4},
    'details': [
        {'amount': 2, 'event_type': 'sleep', 'is_critical': True},
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': True},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
        {'amount': 1, 'event_type': 'trash_frames', 'is_critical': False},
        {
            'amount': 1,
            'event_type': 'bad_camera_pose1337',
            'is_critical': False,
        },
    ],
    'non_critical': {'amount': 3, 'diff': 200.0},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'bad_camera_pose1337'},
        {'amount': 1, 'event_type': 'trash_frames'},
    ],
}

RESPONSE12_WHERE_DEVICE_ERRORS_IS_NONE = {
    'critical': {'amount': 4},
    'details': [
        {'amount': 2, 'event_type': 'sleep', 'is_critical': True},
        {'amount': 1, 'event_type': 'distraction', 'is_critical': True},
        {'amount': 1, 'event_type': 'bad_camera_pose', 'is_critical': True},
        {'amount': 1, 'event_type': 'driver_lost', 'is_critical': False},
        {'amount': 1, 'event_type': 'trash_frames', 'is_critical': False},
        {
            'amount': 1,
            'event_type': 'bad_camera_pose1337',
            'is_critical': False,
        },
    ],
    'non_critical': {'amount': 3, 'diff': 200.0},
    'device_errors': [
        {'amount': 0, 'event_type': 'bad_camera_pose'},
        {'amount': 1, 'event_type': 'trash_frames'},
    ],
}

NO_CONFIGS_TEMPLATE = (None, None, None)
DEFAULT_PARK_ID_AND_PERIOD = (
    'p1',
    '2020-02-27T00:00:00+03:00',
    '2020-02-28T00:00:00+03:00',
)

BIG_WHITELIST_CONFIG = pytest.mark.config(
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
        {
            'event_type': 'driver_lost',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'trash_frames',
            'is_critical': False,
            'is_violation': True,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'bad_camera_pose',
            'is_critical': False,
            'is_violation': True,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'bad_camera_pose1337',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'some_other_event_type',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'another_unreal_event_type',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)


@pytest.mark.pgsql(
    'signal_device_api_meta_db',
    files=['pg_signal_device_api_meta_db.sql', 'error_states.sql'],
)
@pytest.mark.config(
    TVM_ENABLED=True,
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
        {
            'event_type': 'driver_lost',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'trash_frames',
            'is_critical': False,
            'is_violation': True,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'bad_camera_pose',
            'is_critical': False,
            'is_violation': True,
            'fixation_config_path': 'some_path',
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, whitelist, critical_types, '
    'device_errors, check_order_ignored_slices, expected_response',
    [
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-26T00:00:00+03:00',
            *NO_CONFIGS_TEMPLATE,
            None,
            RESPONSE1,
        ),
        (
            'p1',
            '2020-02-26T00:00:00+03:00',
            '2020-02-26T23:59:59+03:00',
            *NO_CONFIGS_TEMPLATE,
            None,
            RESPONSE2,
        ),
        (
            *DEFAULT_PARK_ID_AND_PERIOD,
            *NO_CONFIGS_TEMPLATE,
            [slice(1, 4), slice(5, 8)],
            RESPONSE3,
        ),
        (
            *DEFAULT_PARK_ID_AND_PERIOD,
            ['sleep', 'distraction'],
            None,
            None,
            [slice(1, 4)],
            RESPONSE4_WITH_WHITELIST,
        ),
        (
            *DEFAULT_PARK_ID_AND_PERIOD,
            None,
            ['sleep', 'distraction'],
            None,
            None,
            RESPONSE5_WITH_CRITICAL_EVENTS,
        ),
        (
            *DEFAULT_PARK_ID_AND_PERIOD,
            ['sleep', 'distraction'],
            ['sleep', 'distraction'],
            None,
            [],
            RESPONSE6_WITH_BOTH,
        ),
        (
            'p1',
            '2020-02-28T00:00:00+03:00',
            '2020-02-29T00:00:00+03:00',
            None,
            None,
            [],
            None,
            RESPONSE7_EMPTY_ERRORS,
        ),
        pytest.param(
            *DEFAULT_PARK_ID_AND_PERIOD,
            ['sleep', 'distraction', 'driver_lost', 'bad_camera_pose'],
            None,
            ['bad_camera_pose'],
            [slice(1, 4), slice(5, 7)],
            RESPONSE8_WITH_DEVICE_ERRORS_NON_CRITICAL,
            marks=BIG_WHITELIST_CONFIG,
        ),
        pytest.param(
            *DEFAULT_PARK_ID_AND_PERIOD,
            ['sleep', 'distraction', 'driver_lost', 'bad_camera_pose'],
            ['sleep', 'distraction', 'bad_camera_pose'],
            ['bad_camera_pose'],
            [slice(1, 3)],
            RESPONSE9_WITH_DEVICE_ERRORS_CRITICAL,
            marks=BIG_WHITELIST_CONFIG,
        ),
        pytest.param(
            *DEFAULT_PARK_ID_AND_PERIOD,
            [
                'sleep',
                'distraction',
                'driver_lost',
                'bad_camera_pose',
                'bad_camera_pose1337',
            ],
            ['sleep', 'distraction', 'bad_camera_pose'],
            ['bad_camera_pose', 'bad_camera_pose1337'],
            [slice(1, 3), slice(3, 5)],
            RESPONSE10_WITH_TWO_DEVICE_ERRORS,
            marks=BIG_WHITELIST_CONFIG,
        ),
        pytest.param(
            *DEFAULT_PARK_ID_AND_PERIOD,
            [
                'sleep',
                'distraction',
                'driver_lost',
                'trash_frames',
                'bad_camera_pose',
                'bad_camera_pose1337',
            ],
            ['sleep', 'distraction', 'bad_camera_pose'],
            ['bad_camera_pose', 'bad_camera_pose1337', 'trash_frames'],
            None,
            RESPONSE11_WITH_THREE_DEVICE_ERRORS,
            marks=BIG_WHITELIST_CONFIG,
        ),
        pytest.param(
            *DEFAULT_PARK_ID_AND_PERIOD,
            [
                'sleep',
                'distraction',
                'driver_lost',
                'trash_frames',
                'bad_camera_pose',
                'bad_camera_pose1337',
            ],
            ['sleep', 'distraction', 'bad_camera_pose'],
            None,
            None,
            RESPONSE12_WHERE_DEVICE_ERRORS_IS_NONE,
            id='device_errors is none',
            marks=BIG_WHITELIST_CONFIG,
        ),
    ],
)
async def test_v1_dashboard_events_statistics(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        period_from,
        period_to,
        whitelist,
        critical_types,
        device_errors,
        check_order_ignored_slices,
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
    if whitelist is not None:
        body['whitelist'] = whitelist
    if device_errors is not None:
        body['device_errors'] = device_errors
    if critical_types is not None:
        utils.add_park_critical_types_in_db(
            pgsql, park_id=park_id, critical_types=critical_types,
        )

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['critical'] == expected_response['critical']
    assert response_json['non_critical'] == expected_response['non_critical']

    if check_order_ignored_slices is not None:
        assert utils.lists_are_equal_ignore_order_in_slices(
            response_json['details'],
            expected_response['details'],
            check_order_ignored_slices,
            lambda x: x['event_type'],
        )
    else:
        assert utils.unordered_lists_are_equal(
            response_json['details'], expected_response['details'],
        )

    assert utils.unordered_lists_are_equal(
        response_json['device_errors'], expected_response['device_errors'],
    )


@pytest.mark.config(TVM_ENABLED=True)
async def test_v1_dashboard_events_statistics_wrong_period(
        taxi_signal_device_api_admin, mockserver,
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

    body = {
        'period': {
            'from': '2020-02-26T00:00:00+03:00',
            'to': '2020-02-26T00:00:00+03:00',
        },
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'p1'}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': 'period.from must be lower than period.to',
    }


DETAILS = [
    {'event_type': 'seatbelt', 'amount': 1, 'is_critical': True},
    {'event_type': 'tired', 'amount': 1, 'is_critical': True},
    {'event_type': 'sleep', 'amount': 1, 'is_critical': False},
    {'event_type': 'ushel v edu', 'amount': 1, 'is_critical': False},
    {'event_type': 'brosil signalq', 'amount': 1, 'is_critical': False},
    {'event_type': 'kak teper zhit', 'amount': 1, 'is_critical': False},
    {'event_type': 'third eye', 'amount': 1, 'is_critical': False},
]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': [],
        'events': web_common.DEMO_EVENTS,
        'vehicles': [],
        'groups': [],
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(  # noqa: E501 line too long
        ['tired', 'seatbelt'],
    ),
)
async def test_demo_v1_dashboard_events_statistics(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['taxi'],
                },
            ],
        }

    body = {
        'period': {
            'from': '2020-02-20T00:00:00+03:00',
            'to': '2020-02-27T00:00:00+03:00',
        },
    }
    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'p1'}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert len(DETAILS) == len(response_json['details'])
    for detail in response_json['details']:
        assert detail in DETAILS, detail
    del response_json['details']
    assert response_json == {
        'critical': {'amount': 2, 'diff': 0},
        'non_critical': {'amount': 5, 'diff': 0},
        'device_errors': [
            {'event_type': 'bad_camera_pose', 'amount': 5},
            {'event_type': 'trash_frames', 'amount': 0},
        ],
    }
