import pytest


ENDPOINT = 'user_phones/get'


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
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _get_phone(taxi_user_api, '123459e1e7e5b1f539abcdef')
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone with id 123459e1e7e5b1f539abcdef',
    }


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'id_, response_name',
    [
        ('539e99e1e7e5b1f5397adc5d', 'void_object_response.json'),
        ('539e99e1e7e5b1f5398adc5a', 'partial_object_response.json'),
        ('539e99e1e7e5b1f5398adc5b', 'filled_object_response.json'),
    ],
    ids=['void object', 'partial object', 'filled object'],
)
async def test_get_phone(taxi_user_api, id_, response_name, load_json):
    response = await _get_phone(taxi_user_api, id_)
    assert response.status_code == 200

    assert response.json() == load_json(response_name)


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize('primary_replica', [None, False, True])
async def test_get_phone_with_read_preference(
        taxi_user_api, load_json, primary_replica,
):
    response = await _get_phone(
        taxi_user_api,
        '539e99e1e7e5b1f5398adc5b',
        primary_replica=primary_replica,
    )
    assert response.status_code == 200

    assert response.json() == load_json('filled_object_response.json')


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'phone_id, response_name',
    [
        ('539e99e1e7e5b1f5397adc5d', 'arbitary_type_response.json'),
        ('539e99e1e7e5b1f5397adc5e', 'arbitary_payment_type_response.json'),
    ],
    ids=['arbitary type', 'arbitary payment method type'],
)
@pytest.mark.filldb(user_phones='arbitary_data')
async def test_get_phone_with_arbitary_data(
        taxi_user_api, load_json, phone_id, response_name,
):
    response = await _get_phone(taxi_user_api, phone_id)

    assert response.status_code == 200
    assert response.json() == load_json(response_name)


async def _get_phone(api, phone_id, primary_replica=None):
    request = {'id': phone_id}

    if primary_replica:
        request['primary_replica'] = primary_replica

    return await api.post(ENDPOINT, json=request)
