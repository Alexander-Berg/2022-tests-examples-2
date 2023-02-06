import pytest


@pytest.mark.now('2019-02-01T13:00:00+00:00')
async def test_get_authinfo(taxi_user_api):
    response = await taxi_user_api.post(
        'users/get_authinfo', json={'id': '6e409dba84794165a34ac72ae27829ac'},
    )
    assert response.status_code == 200
    _check_response(
        response.json(),
        [
            'confirmation_attempts',
            'confirmation_code',
            'confirmation_created',
            'phone_id',
            'authorized',
        ],
    )


async def test_not_found(taxi_user_api):
    index = 'incorrect_input'
    response = await taxi_user_api.post(
        'users/get_authinfo', json={'id': index},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No user with id ' + index,
    }


async def test_increment_attempts(taxi_user_api, mongodb):
    user_doc = mongodb.users.find_one(
        {'_id': '6e409dba84794165a34ac72ae27829ac'},
    )
    assert user_doc['confirmation']['attempts'] == 2

    response = await taxi_user_api.post(
        'users/increment_attempts',
        json={'id': '6e409dba84794165a34ac72ae27829ac'},
    )
    assert response.status_code == 200
    user_doc = mongodb.users.find_one(
        {'_id': '6e409dba84794165a34ac72ae27829ac'},
    )
    assert user_doc['confirmation']['attempts'] == 3


async def test_set_confirmation_code(taxi_user_api, mongodb):
    user_doc = mongodb.users.find_one(
        {'_id': '8fa869dd9e684cbe945f7a73df621e25'},
    )
    assert user_doc['confirmation']['code'] == '111'

    response = await taxi_user_api.post(
        'users/set_confirmation_code',
        json={
            'id': '8fa869dd9e684cbe945f7a73df621e25',
            'confirmation_code': '123456',
            'phone_id': '56b885ebed2c89a5e04e60ed',
        },
    )
    assert response.status_code == 200
    user_doc = mongodb.users.find_one(
        {'_id': '8fa869dd9e684cbe945f7a73df621e25'},
    )
    assert user_doc['confirmation']['code'] == '123456'


async def test_set_authorized(taxi_user_api, mongodb):
    user_doc = mongodb.users.find_one(
        {'_id': '8fa869dd9e684cbe945f7a73df621e25'},
    )
    assert user_doc['authorized'] is False

    response = await taxi_user_api.post(
        'users/set_authorized',
        json={'id': '8fa869dd9e684cbe945f7a73df621e25', 'authorized': True},
    )
    assert response.status_code == 200
    user_doc = mongodb.users.find_one(
        {'_id': '8fa869dd9e684cbe945f7a73df621e25'},
    )
    assert user_doc['authorized'] is True


def _check_response(response_json, fields):
    expected_response = {
        'id': '6e409dba84794165a34ac72ae27829ac',
        'created': '2019-02-01T13:00:00+0000',
        'updated': '2019-02-01T13:00:00+0000',
        'phone_id': '56b885ebed2c89a5e04e60ed',
        'authorized': True,
        'confirmation_code': '123456',
        'confirmation_attempts': 2,
        'confirmation_created': '2019-02-01T13:00:00+0000',
    }
    if not fields:
        assert response_json == expected_response
    else:
        assert len(response_json) == len(fields)
        for field in fields:
            assert response_json[field] == expected_response[field]
