import datetime

import pytest


NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)


CORP_USER_PHONES_SUPPORTED_79 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]
CORP_USER_PHONES_SUPPORTED_712 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+712', '+79'],
        'matches': ['^712', '^79'],
    },
]


@pytest.mark.parametrize(
    ['passport_mock', 'client', 'user_id'],
    [
        # active user
        ('client1', 'client1', 'user1'),
        # inactive user with department_id
        ('client1', 'client1', 'user3'),
        # check access for department manager
        ('manager1', 'client1', 'user3'),
        # check drive/deactivate call
        ('client2', 'client2', 'userServicesActive'),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(
    COST_CENTERS_VALUES_MAX_COUNT=2,
    ALLOW_CORP_BILLING_REQUESTS=True,
    IGNORE_CORP_BILLING_ERRORS=False,
)
@pytest.mark.now(NOW.isoformat())
async def test_delete_user(
        taxi_corp_real_auth_client,
        pd_patch,
        drive_patch,
        db,
        patch,
        passport_mock,
        client,
        user_id,
):
    @patch('taxi.clients.drive.DriveClient.descriptions')
    async def _descriptions(*args, **kwargs):
        return {
            'accounts': [
                {
                    'name': 'example',
                    'soft_limit': 0,
                    'hard_limit': 0,
                    'meta': {'parent_id': 123},
                },
            ],
        }

    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/{}/user/{}'.format(client, user_id),
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    db_item = await db.corp_users.find_one({'_id': user_id})
    assert db_item['is_deleted'] is True
    assert db_item['is_active'] is False
    assert 'deleted' in db_item

    db_history_item = await db.corp_history.find_one({'e._id': user_id})
    assert 'deleted' in db_history_item['e']


@pytest.mark.parametrize(
    'passport_mock, user_id, expected_status',
    [
        ('client2', 'user1', 403),
        ('client1', 'user4', 403),
        ('client2_manager1', 'user1', 403),
        ('client2', 'user2', 403),  # feature off
        ('client1', 'userX', 410),  # already deleted, but active user
    ],
    indirect=['passport_mock'],
)
async def test_delete_user_fail(
        taxi_corp_real_auth_client,
        pd_patch,
        db,
        passport_mock,
        user_id,
        expected_status,
):

    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/client1/user/{}'.format(user_id),
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
