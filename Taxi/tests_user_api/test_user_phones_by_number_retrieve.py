import pytest

ENDPOINT = 'user_phones/by_number/retrieve'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'type': 'foo'}, 'Field \'phone\' is missing'),
        (
            {'phone': 123, 'type': 'foo'},
            (
                'Field \'phone\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        ({'phone': '+71112223344'}, 'Field \'type\' is missing'),
        (
            {'phone': '+71112223344', 'type': 123},
            (
                'Field \'type\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {
                'phone': '+71112223344',
                'type': 'foo',
                'primary_replica': 'not_a_bool',
            },
            (
                'Field \'primary_replica\' is of a wrong type. '
                'Expected: booleanValue, actual: stringValue'
            ),
        ),
    ],
    ids=[
        'missing phone',
        'numeric phone',
        'missing type',
        'numeric type',
        'bad primary_replica',
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_not_found(taxi_user_api):
    response = await _get_user_phone_by_number(
        taxi_user_api, '+71112223344', 'unknown',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone by phone and type',
    }


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize('primary_replica', [None, False, True])
@pytest.mark.parametrize(
    'phone, type_, response_name',
    [
        ('+71112223344', 'yandex', 'yandex_response.json'),
        ('+71112223345', 'yandex', 'default_type_response.json'),
        ('+71112223344', 'deleted:12345', 'deleted_response.json'),
    ],
    ids=['regular', 'default type', 'deleted'],
)
async def test_ok(
        taxi_user_api, load_json, phone, type_, response_name, primary_replica,
):
    response = await _get_user_phone_by_number(
        taxi_user_api, phone, type_, primary_replica=primary_replica,
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_name)


async def _get_user_phone_by_number(api, phone, type_, primary_replica=None):
    body = {'phone': phone, 'type': type_}

    if primary_replica:
        body['primary_replica'] = primary_replica

    return await api.post(ENDPOINT, json=body)
