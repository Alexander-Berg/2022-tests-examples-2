from urllib import parse

import pytest


ENDPOINT = '/user_phones/by-natural-id'


@pytest.mark.parametrize(
    'query, message',
    [
        ('?' + parse.urlencode({'id': 'foo'}), 'Missing type in query'),
        ('?' + parse.urlencode({'type': 'user_id'}), 'Missing id in query'),
        (
            '?' + parse.urlencode({'id': 'foo', 'type': 'bar'}),
            'Failed to parse request',
        ),
    ],
    ids=['no type', 'no id', 'bad type'],
)
async def test_bad_request(taxi_user_api, query, message):
    response = await taxi_user_api.get(ENDPOINT + query)
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': message}


@pytest.mark.parametrize(
    'query_id, query_type',
    [
        ('539e99e1e7e5b1f5397affff', 'user_id'),
        ('539e99e1e7e5b1f5397aaaab', 'user_id'),
        ('539e99e1e7e5b1f5397aaaac', 'user_id'),
    ],
)
async def test_not_found(taxi_user_api, query_id, query_type):
    response = await taxi_user_api.get(_make_url(query_id, query_type))
    assert response.status_code == 404


@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_ok_user_id(taxi_user_api):
    response = await taxi_user_api.get(
        _make_url('539e99e1e7e5b1f5397aaaaa', 'user_id'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': '539e99e1e7e5b1f5397adc5d',
        'phone': '+79991234567',
        'type': 'yandex',
        'phone_hash': '123',
        'phone_salt': '132',
        'personal_phone_id': '557f191e810c19729de860ea',
        'created': '2019-02-01T13:00:00+0000',
        'updated': '2019-02-01T13:00:00+0000',
        'is_loyal': False,
        'is_taxi_staff': False,
        'is_yandex_staff': False,
        'stat': {
            'big_first_discounts': 0,
            'complete': 0,
            'complete_apple': 0,
            'complete_card': 0,
            'complete_google': 0,
            'fake': 0,
            'total': 0,
        },
    }


def _make_url(query_id, query_type):
    return (
        ENDPOINT + '?' + parse.urlencode({'id': query_id, 'type': query_type})
    )
