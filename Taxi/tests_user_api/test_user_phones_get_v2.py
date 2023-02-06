import pytest


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'requested_id, expected_response',
    [
        (
            '539e99e1e7e5b1f5397adc5d',
            {
                'id': '539e99e1e7e5b1f5397adc5d',
                'type': 'yandex',
                'personal_phone_id': '557f191e810c19729de860ea',
                'created': '2019-02-01T13:00:00+0000',
                'updated': '2019-02-01T13:00:00+0000',
                'phone_hash': '123',
                'phone_salt': '132',
                'loyal': True,
                'yandex_staff': True,
                'taxi_staff': True,
                'bound_uid': 'uid',
                'last_order_city_id': 'msk',
                'last_order_nearest_zone': 'msk',
                'last_payment_method': {
                    'id': 'payment-id',
                    'type': 'payment-type',
                },
                'loyalty_processed': ['processed-1', 'processed-2'],
                'antifraud': {
                    'group': 1,
                    'version': 2,
                    'paid_orders': ['order-1', 'order-2'],
                },
                'stat': {
                    'total': 30,
                    'complete': 20,
                    'complete_card': 10,
                    'complete_google': 0,
                    'complete_apple': 0,
                    'fake': 0,
                    'big_first_discounts': 0,
                },
            },
        ),
        (
            '539e99e1e7e5b1f5398adc5a',
            {
                'id': '539e99e1e7e5b1f5398adc5a',
                'taxi_outstaff': True,
                'yandex_staff': True,
            },
        ),
    ],
)
async def test_user_phones_get(taxi_user_api, requested_id, expected_response):
    response = await taxi_user_api.post(
        '/v2/user_phones/get', json={'id': requested_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'requested_fields, expected_response',
    [
        ([], {'id': '539e99e1e7e5b1f5397adc5d'}),
        (['qwe'], {'id': '539e99e1e7e5b1f5397adc5d'}),
        (['id'], {'id': '539e99e1e7e5b1f5397adc5d'}),
        (
            ['personal_phone_id', 'qwe'],
            {
                'id': '539e99e1e7e5b1f5397adc5d',
                'personal_phone_id': '557f191e810c19729de860ea',
            },
        ),
    ],
)
async def test_user_phones_get_fields(
        taxi_user_api, requested_fields, expected_response,
):
    response = await taxi_user_api.post(
        '/v2/user_phones/get',
        json={'id': '539e99e1e7e5b1f5397adc5d', 'fields': requested_fields},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize('primary_replica', [None, False, True])
async def test_user_phones_get_replica(taxi_user_api, primary_replica):
    request = {'id': '539e99e1e7e5b1f5397adc5d'}
    if primary_replica is not None:
        request['primary_replica'] = primary_replica

    response = await taxi_user_api.post('/v2/user_phones/get', json=request)
    assert response.status_code == 200
    assert response.json()['id'] == '539e99e1e7e5b1f5397adc5d'


async def test_not_found(taxi_user_api):
    response = await taxi_user_api.post(
        '/v2/user_phones/get', json={'id': '123459e1e7e5b1f539abcdef'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No user_phone with id 123459e1e7e5b1f539abcdef',
    }


@pytest.mark.parametrize(
    'request_body, error_message',
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
        (
            {
                'id': '123459e1e7e5b1f539abcdef',
                'primary_replica': 'not_a_bool',
            },
            (
                'Field \'primary_replica\' is of a wrong type. '
                'Expected: booleanValue, actual: stringValue'
            ),
        ),
    ],
)
async def test_bad_request(taxi_user_api, request_body, error_message):
    response = await taxi_user_api.post(
        '/v2/user_phones/get', json=request_body,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
