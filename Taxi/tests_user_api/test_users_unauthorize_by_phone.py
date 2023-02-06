import bson
import pytest


@pytest.mark.parametrize('request_body', [{}, {'phone_id': 'invalid-iod'}])
async def test_invalid_input(taxi_user_api, request_body):
    response = await taxi_user_api.post(
        'users/unauthorize-by-phone', json=request_body,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_phone_id, updated_users_count',
    [
        ('000000000000000000000001', 2),
        ('000000000000000000000002', 1),
        ('000000000000000000000003', 0),
    ],
)
async def test_unauthorize(
        taxi_user_api,
        mongodb,
        testpoint,
        request_phone_id,
        updated_users_count,
):
    @testpoint('updated-users-count')
    def check_updated_users_count(count):
        assert count == updated_users_count

    response = await taxi_user_api.post(
        'users/unauthorize-by-phone', json={'phone_id': request_phone_id},
    )
    assert response.status_code == 200
    assert check_updated_users_count.times_called == 1

    cursor = mongodb.users.find({'phone_id': bson.ObjectId(request_phone_id)})
    for doc in cursor:
        assert 'authorized' not in doc
