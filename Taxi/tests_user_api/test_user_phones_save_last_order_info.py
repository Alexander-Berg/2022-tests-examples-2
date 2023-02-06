import bson
import pytest


ENDPOINT = 'user_phones/save_last_order_info'


@pytest.mark.parametrize(
    'body, message',
    [
        (
            {'city_id': 'bar', 'nearest_zone': 'foo'},
            'Field \'phone_id\' is missing',
        ),
        (
            {'phone_id': 123, 'city_id': 'bar', 'nearest_zone': 'foo'},
            (
                'Field \'phone_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'phone_id': '123', 'city_id': 'bar', 'nearest_zone': 'foo'},
            'Invalid oid 123',
        ),
        (
            {'phone_id': '123459e1e7e5b1f539abcdef', 'nearest_zone': 'foo'},
            'Field \'city_id\' is missing',
        ),
        (
            {'phone_id': '123459e1e7e5b1f539abcdef', 'city_id': 123},
            (
                'Field \'city_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'phone_id': '123459e1e7e5b1f539abcdef', 'city_id': 'foo'},
            'Field \'nearest_zone\' is missing',
        ),
        (
            {
                'phone_id': '123459e1e7e5b1f539abcdef',
                'city_id': 'foo',
                'nearest_zone': 123,
            },
            (
                'Field \'nearest_zone\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
    ],
    ids=[
        'no phone_id',
        'int phone_id',
        'bad phone_id',
        'no city_id',
        'int city_id',
        'no nearest_zone',
        'int nearest_zone',
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _save_last_order_info(
        taxi_user_api, '123459e1e7e5b1f539abcdef', 'foo', 'bar',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone with id 123459e1e7e5b1f539abcdef',
    }


async def test_save_last_order_info(taxi_user_api, mongodb):
    phone_id = '539e99e1e7e5b1f5397adc5d'

    def _get_doc():
        return mongodb.user_phones.find_one(
            bson.ObjectId(phone_id),
            ['last_order_city_id', 'last_order_nearest_zone', 'updated'],
        )

    before = _get_doc()
    response = await _save_last_order_info(
        taxi_user_api, phone_id, 'foo', 'bar',
    )
    assert response.status_code == 200
    assert response.json() == {}

    after = _get_doc()
    assert 'last_order_city_id' not in before
    assert 'last_order_nearest_zone' not in before
    assert after['last_order_city_id'] == 'foo'
    assert after['last_order_nearest_zone'] == 'bar'
    assert after['updated'] > before['updated']


async def _save_last_order_info(api, phone_id, city_id, nearest_zone):
    return await api.post(
        ENDPOINT,
        json={
            'phone_id': phone_id,
            'city_id': city_id,
            'nearest_zone': nearest_zone,
        },
    )
