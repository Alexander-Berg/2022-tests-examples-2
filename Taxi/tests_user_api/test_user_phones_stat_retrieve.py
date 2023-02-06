import bson
import pytest

ENDPOINT = 'user_phones/stat/retrieve'


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
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post('user_phones/stat/retrieve', json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _retrieve_stats(taxi_user_api, '123e99e1e7e5b1f5397adc5d')
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': ('No such user_phone with id ' '123e99e1e7e5b1f5397adc5d'),
    }


async def test_stat_missing(taxi_user_api):
    response = await _retrieve_stats(taxi_user_api, '539e99e1e7e5b1f5397adc5e')
    assert response.status_code == 200
    assert response.json() == {'stat': {}}


async def test_stat_malformed(taxi_user_api):
    response = await _retrieve_stats(taxi_user_api, '539e99e1e7e5b1f5397adc5f')
    assert response.status_code == 500


async def test_stat_missing_fields(taxi_user_api, mongodb):
    response = await _retrieve_stats(taxi_user_api, '539e99e1e7e5b1f5397adc6f')
    stat_data = mongodb.user_phones.find_one(
        {'_id': bson.ObjectId('539e99e1e7e5b1f5397adc6f')},
        {'_id': False, 'stat': True},
    )
    stat_data = stat_data['stat']

    assert response.status_code == 200
    assert response.json() == {'stat': stat_data}


async def test_retrieve_stats(taxi_user_api):
    response = await _retrieve_stats(taxi_user_api, '539e99e1e7e5b1f5397adc5d')
    assert response.status_code == 200
    assert response.json() == {
        'stat': {
            'total': 100,
            'complete': 15,
            'complete_card': 1,
            'complete_google': 5,
            'complete_apple': 6,
            'fake': 1,
            'big_first_discounts': 1,
        },
    }


async def _retrieve_stats(api, phone_id):
    request = {'id': phone_id}

    return await api.post(ENDPOINT, json=request)
