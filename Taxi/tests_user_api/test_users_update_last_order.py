import datetime

import pytest


async def test_update_last_order_no_user(taxi_user_api):
    response = await taxi_user_api.post(
        'users/update-last-order-info',
        json={
            'user_id': 'user-not-found',
            'last_order_created': '2020-12-01T11:00:00.123456+0000',
        },
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_user_id', ['user-with-last-order', 'user-without-last-order'],
)
@pytest.mark.now('2020-12-01T12:00:00+00:00')
async def test_update_last_order(taxi_user_api, mongodb, request_user_id):
    expected_last_order = datetime.datetime(2020, 12, 1, 11, 0, 0, 123000)

    old_doc = mongodb.users.find_one({'_id': request_user_id})
    assert old_doc.get('last_order_created') != expected_last_order

    response = await taxi_user_api.post(
        'users/update-last-order-info',
        json={
            'user_id': request_user_id,
            'last_order_created': '2020-12-01T11:00:00.123456+0000',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    new_doc = mongodb.users.find_one({'_id': request_user_id})
    assert new_doc['last_order_created'] == expected_last_order
    assert new_doc['updated'] > old_doc['updated']
