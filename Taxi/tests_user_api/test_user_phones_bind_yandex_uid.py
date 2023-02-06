import bson
import pytest


ENDPOINT = 'user_phones/bind_yandex_uid'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'yandex_uid': '999999999'}, 'Field \'phone_id\' is missing'),
        (
            {'phone_id': '539e99e1e7e5b1f5397adc5d'},
            'Field \'yandex_uid\' is missing',
        ),
        (
            {'phone_id': 'foobar', 'yandex_uid': '999999999'},
            'Invalid oid foobar',
        ),
        (
            {'phone_id': 123, 'yandex_uid': '999999999'},
            (
                'Field \'phone_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'phone_id': '539e99e1e7e5b1f5397adc5d', 'yandex_uid': 999999999},
            (
                'Field \'yandex_uid\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
    ],
    ids=[
        'missing phone_id',
        'missing yandex_uid',
        'malformed phone_id',
        'numeric phone_id',
        'numeric yandex_uid',
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _bind_yandex_uid(
        taxi_user_api, '123459e1e7e5b1f539abcdef', '999999999',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone with id 123459e1e7e5b1f539abcdef',
    }


async def test_bound(taxi_user_api, mongodb):
    phone_id = '539e99e1e7e5b1f5397adc5d'
    yandex_uid = '999999999'

    assert 'bound_uid' not in mongodb.user_phones.find_one(
        {'_id': bson.ObjectId(phone_id)}, ['bound_uid'],
    )

    response = await _bind_yandex_uid(taxi_user_api, phone_id, yandex_uid)
    assert response.status_code == 200
    assert response.json() == {}

    assert (
        mongodb.user_phones.find_one(
            {'_id': bson.ObjectId(phone_id)}, ['bound_uid'],
        )['bound_uid']
        == yandex_uid
    )


@pytest.mark.parametrize(
    'yandex_uid, status, body',
    [
        (
            '999999999',
            409,
            {
                'code': 'ALREADY_BOUND',
                'message': 'User\'s phone already bound',
            },
        ),
        ('123456789', 200, {}),
    ],
)
async def test_conflict(taxi_user_api, yandex_uid, status, body):
    response = await _bind_yandex_uid(
        taxi_user_api, '539e99e1e7e5b1f5398adc5a', yandex_uid,
    )
    assert response.status_code == status
    assert response.json() == body


async def test_bind_race(taxi_user_api, mongodb, testpoint):
    @testpoint('testpoint:before_bind')
    def bind(phone_id):
        mongodb.user_phones.update(
            {'_id': bson.ObjectId(phone_id)},
            {
                '$set': {'bound_uid': '123456789'},
                '$currentDate': {'updated': True},
            },
        )

    response = await _bind_yandex_uid(
        taxi_user_api, '539e99e1e7e5b1f5397adc5d', '999999999',
    )
    assert bind.times_called == 1
    assert response.status_code == 409
    assert response.json() == {
        'code': 'ALREADY_BOUND',
        'message': 'User\'s phone already bound',
    }


async def _bind_yandex_uid(api, phone_id, yandex_uid):
    request = {'phone_id': phone_id, 'yandex_uid': yandex_uid}

    return await api.post(ENDPOINT, json=request)
