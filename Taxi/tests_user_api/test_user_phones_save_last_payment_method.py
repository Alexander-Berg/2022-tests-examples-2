import bson
import pytest

ENDPOINT = 'user_phones/save_last_payment_method'


@pytest.mark.parametrize(
    'body, message',
    [
        (
            {'foo': 'bar', 'payment_method_type': 'cash'},
            'Field \'phone_id\' is missing',
        ),
        (
            {'phone_id': 123, 'payment_method_type': 'cash'},
            (
                'Field \'phone_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'phone_id': '123', 'payment_method_type': 'cash'},
            'Invalid oid 123',
        ),
        (
            {'phone_id': '123459e1e7e5b1f539abcdef'},
            'Field \'payment_method_type\' is missing',
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'payment_method_type': 123,
            },
            (
                'Field \'payment_method_type\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'payment_method_type': 'card',
                'payment_method_id': 123,
            },
            (
                'Field \'payment_method_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
    ],
    ids=[
        'missing phone_id',
        'numeric phone_id',
        'malformed phone_id',
        'missing payment_method_type',
        'numeric payment_method_type',
        'numeric id',
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _save_last_payment_method(
        taxi_user_api, '123459e1e7e5b1f539abcdef', 'cash',
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone with id 123459e1e7e5b1f539abcdef',
    }


@pytest.mark.parametrize(
    'phone_id', ['539e99e1e7e5b1f5397adc5d', '539e99e1e7e5b1f5397adc5e'],
)
@pytest.mark.parametrize(
    'payment_method_type, payment_method_id',
    [('cash', None), ('card', 'card-xxxxxxxxxxxxxa51c1e12a713')],
)
async def test_ok(
        taxi_user_api,
        mongodb,
        phone_id,
        payment_method_type,
        payment_method_id,
):
    initial_updated = mongodb.user_phones.find_one(
        {'_id': bson.ObjectId(phone_id)}, ['updated'],
    )['updated']

    response = await _save_last_payment_method(
        taxi_user_api, phone_id, payment_method_type, payment_method_id,
    )
    assert response.status_code == 200
    assert response.json() == {}

    user_phone = mongodb.user_phones.find_one(
        {'_id': bson.ObjectId(phone_id)}, ['updated', 'last_payment_method'],
    )
    assert user_phone['updated'] != initial_updated
    last_payment_method = user_phone['last_payment_method']
    assert last_payment_method['type'] == payment_method_type

    if payment_method_id:
        assert last_payment_method['id'] == payment_method_id
    else:
        assert 'id' not in last_payment_method


async def _save_last_payment_method(
        api, phone_id, payment_method_type, payment_method_id=None,
):
    request = {
        'phone_id': phone_id,
        'payment_method_type': payment_method_type,
    }

    if payment_method_id:
        request['payment_method_id'] = payment_method_id

    return await api.post(ENDPOINT, json=request)
