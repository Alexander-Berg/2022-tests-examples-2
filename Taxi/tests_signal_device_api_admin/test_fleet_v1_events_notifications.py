import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

RESPONSE1 = {'critical_types': ['distraction', 'sleep']}
RESPONSE2 = {
    'critical_types': ['tired', 'eyeclosed', 'distraction', 'seatbelt'],
}


NOTIFICATIONS_NORMAL = {
    'user_notifications_settings': [{'user_id': 'u1'}, {'user_id': 'u2'}],
}


NOTIFICATIONS_DOUBLED_USER = {
    'user_notifications_settings': [
        {'user_id': 'u1'},
        {'user_id': 'u2'},
        {'user_id': 'u2'},
    ],
}

NOTIFICATIONS_BAD_USERS = {
    'user_notifications_settings': [
        {'user_id': 'u1'},
        {'user_id': 'u42'},
        {'user_id': 'u43'},
    ],
}


@pytest.mark.parametrize(
    'expected_request, expected_code, expected_response',
    [
        (NOTIFICATIONS_NORMAL, 200, NOTIFICATIONS_NORMAL),
        (NOTIFICATIONS_DOUBLED_USER, 200, NOTIFICATIONS_NORMAL),
        (
            NOTIFICATIONS_BAD_USERS,
            400,
            {
                'code': '400',
                'message': 'Some user ids were not found',
                'users_not_found': ['u42', 'u43'],
            },
        ),
        (
            {'user_notifications_settings': []},
            200,
            {'user_notifications_settings': []},
        ),
    ],
)
async def test_v1_events_notifications(
        taxi_signal_device_api_admin,
        mockserver,
        pgsql,
        expected_request,
        expected_code,
        expected_response,
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

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    async def _mock_dac(request):
        if 'user_notifications_settings' in expected_response:
            user_ids_expected = [
                user['user_id']
                for user in (expected_response['user_notifications_settings'])
            ]
            assert utils.unordered_lists_are_equal(
                user_ids_expected, request.json['query']['user']['ids'],
            )

        return {
            'users': [
                {
                    'id': 'u1',
                    'park_id': 'p1',
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': False,
                    'is_usage_consent_accepted': False,
                    'email': 'test@yandex.ru',
                },
                {
                    'id': 'u2',
                    'park_id': 'p1',
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': False,
                    'is_usage_consent_accepted': False,
                    'email': 'test@yandex.ru',
                },
            ],
            'limit': 2,
            'offset': 0,
        }

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'p1'}
    response = await taxi_signal_device_api_admin.put(
        '/fleet/signal-device-api-admin/v1/events/notifications',
        headers=headers,
        json=expected_request,
    )

    assert response.status_code == expected_code, response.text
    response_json = response.json()
    if expected_code == 400:
        assert utils.unordered_lists_are_equal(
            response_json['users_not_found'],
            expected_response['users_not_found'],
        )
        return

    # check retry successful
    response = await taxi_signal_device_api_admin.put(
        '/fleet/signal-device-api-admin/v1/events/notifications',
        headers=headers,
        json=expected_request,
    )
    assert response.status_code == expected_code, response.text
    assert response_json == response.json()

    assert utils.unordered_lists_are_equal(
        response_json['user_notifications_settings'],
        expected_response['user_notifications_settings'],
    )

    expected_db_data = [
        (user['user_id'],)
        for user in (expected_response['user_notifications_settings'])
    ]
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute('SELECT user_id FROM signal_device_api.user_notifications')

    assert utils.unordered_lists_are_equal(list(db), expected_db_data)

    get_response = await taxi_signal_device_api_admin.get(
        '/fleet/signal-device-api-admin/v1/events/notifications',
        headers=headers,
    )
    response_json = get_response.json()
    assert utils.unordered_lists_are_equal(
        response_json['user_notifications_settings'],
        expected_response['user_notifications_settings'],
    )
