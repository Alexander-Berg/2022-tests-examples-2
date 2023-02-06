import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'sync/v1/parks/users'

HEADERS = {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET}


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'admin': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
async def test_delete_user_success(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        redis_store,
        blackbox_service,
):
    response = await taxi_dispatcher_access_control.delete(
        ENDPOINT,
        params={'park_id': 'park_valid1', 'user_id': 'admin'},
        headers=HEADERS,
    )

    assert response.status_code == 200, response.text

    assert redis_store.hget('User:Items:park_valid1', 'admin') is None


BAD_PARAMS = [
    (
        'park_invalid',
        'user_valid1',
        404,
        {'code': 'park_not_found', 'message': 'Park not found'},
    ),
    (
        'park_valid1',
        'user_invalid',
        404,
        {'code': 'user_not_found', 'message': 'User not found'},
    ),
]


@pytest.mark.parametrize('park_id, user_id, code, message', BAD_PARAMS)
async def test_modify_user_fail(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        redis_store,
        park_id,
        user_id,
        code,
        message,
):
    response = await taxi_dispatcher_access_control.delete(
        ENDPOINT,
        params={'park_id': park_id, 'user_id': user_id},
        headers=HEADERS,
    )
    assert response.status_code == code, response.text
    assert response.json() == message
