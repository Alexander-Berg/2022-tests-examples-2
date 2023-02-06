import datetime

import pytest


NOW = datetime.datetime(year=2022, month=6, day=27)


@pytest.mark.parametrize(
    ['limit_id', 'status_code', 'expected_response'],
    [
        pytest.param('limit1', 200, {}, id='assigned only for deleted users'),
        pytest.param(
            'not_existed_limit',
            404,
            {'code': 'NOT_FOUND', 'message': 'Limit not found'},
            id='404',
        ),
        pytest.param(
            'default_limit',
            400,
            {
                'code': 'DEFAULT_LIMIT_CANNOT_BE_DELETED',
                'message': 'Default limit cannot be deleted',
            },
            id='default limit, 400',
        ),
        pytest.param(
            'limit3_2_with_users',
            400,
            {'code': 'LIMIT_HAS_USERS', 'message': 'Limit has users'},
            id='limit has users',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_delete_limit(
        web_app_client, db, limit_id, status_code, expected_response,
):
    response = await web_app_client.post(
        '/v2/limits/delete',
        params={'limit_id': limit_id},
        headers={
            'History-Login': 'login1',
            'History-Uid': 'uid1',
            'History-Method': 'DELETE',
            'History-User-IP': 'ip',
            'History-Locale': 'ru',
        },
    )
    response_data = await response.json()
    assert response.status == status_code, response_data

    assert response_data == expected_response

    if response.status == 200:
        deleted_limit = await db.corp_limits.find_one({'_id': limit_id})
        assert deleted_limit['is_deleted']

        history_record = await db.corp_history.find_one(
            {'c': 'corp_limits', 'e._id': limit_id},
            projection={'_id': False, 'e.created': False, 'e.updated': False},
        )
        assert history_record == {
            'a': 'DELETE',
            'c': 'corp_limits',
            'cl': 'client1',
            'ip': 'ip',
            'p': 'login1',
            'p_uid': 'uid1',
            'd': datetime.datetime(2022, 6, 27, 0, 0),
            'e': {
                '_id': 'limit1',
                'categories': ['econom'],
                'client_id': 'client1',
                'counters': {'users': 0},
                'department_id': None,
                'geo_restrictions': [
                    {
                        'destination': 'destination_restriction_id',
                        'source': 'source_restriction_1',
                    },
                ],
                'is_default': False,
                'limits': {
                    'orders_amount': {'period': 'day', 'value': 12},
                    'orders_cost': {'period': 'month', 'value': '1000'},
                },
                'service': 'taxi',
                'time_restrictions': [
                    {
                        'days': ['mo', 'tu', 'we', 'th', 'fr'],
                        'end_time': '18:40:00',
                        'start_time': '10:30:00',
                        'type': 'weekly_date',
                    },
                ],
                'title': 'limit',
            },
        }
