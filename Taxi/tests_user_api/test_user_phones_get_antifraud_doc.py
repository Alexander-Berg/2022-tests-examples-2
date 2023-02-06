import bson
import pytest


@pytest.mark.parametrize(
    'body, message',
    [
        ({'foo': 'bar'}, 'Field \'id\' is missing'),
        (
            {'id': 123},
            (
                'Field \'id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        ({'id': 'strval'}, 'Invalid oid strval'),
    ],
    ids=['missing_id', 'int_id', 'string_id'],
)
async def test_antifraud_doc_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(
        'user_phones/get_antifraud_doc', json=body,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_antifraud_doc_not_found(taxi_user_api):
    response = await _get_antifraud_doc(
        taxi_user_api, '123e99e1e7e5b1f5397adc5d',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': ('No such user_phone with id ' '123e99e1e7e5b1f5397adc5d'),
    }


async def test_antifraud_doc_missing(taxi_user_api):
    response = await _get_antifraud_doc(
        taxi_user_api, '539e99e1e7e5b1f5397adc5e',
    )
    assert response.status_code == 200
    assert response.json() == {'antifraud': {}}


async def test_antifraud_doc_malformed(taxi_user_api):
    response = await _get_antifraud_doc(
        taxi_user_api, '539e99e1e7e5b1f5397adc5f',
    )
    assert response.status_code == 500


async def test_antifraud_doc_missing_fields(taxi_user_api, mongodb):
    response = await _get_antifraud_doc(
        taxi_user_api, '539e99e1e7e5b1f5397adc6f',
    )
    antifraud_data = mongodb.user_phones.find_one(
        {'_id': bson.ObjectId('539e99e1e7e5b1f5397adc6f')},
        {'_id': False, 'antifraud': True},
    )

    assert response.status_code == 200
    assert response.json() == antifraud_data


async def test_antifraud_doc(taxi_user_api):
    response = await _get_antifraud_doc(
        taxi_user_api, '539e99e1e7e5b1f5397adc5d',
    )
    assert response.status_code == 200
    assert response.json() == {
        'antifraud': {
            'version': 1,
            'group': 2,
            'paid_orders': ['1234567890abcdef'],
        },
    }


async def _get_antifraud_doc(api, user_phone_id):
    request = {'id': user_phone_id}

    return await api.post('user_phones/get_antifraud_doc', json=request)
