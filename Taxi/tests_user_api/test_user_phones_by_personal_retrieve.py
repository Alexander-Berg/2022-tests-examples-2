import pytest

ENDPOINT = 'user_phones/by_personal/retrieve'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'type': 'foo'}, 'Field \'personal_phone_id\' is missing'),
        (
            {'personal_phone_id': 123, 'type': 'foo'},
            (
                'Field \'personal_phone_id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'personal_phone_id': '557f191e810c19729de860ea'},
            'Field \'type\' is missing',
        ),
        (
            {'personal_phone_id': '557f191e810c19729de860ea', 'type': 123},
            (
                'Field \'type\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {
                'personal_phone_id': '557f191e810c19729de860ea',
                'type': 'foo',
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
    response = await _get_user_phone_by_personal(
        taxi_user_api, '+71112223344', 'unknown',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No such user_phone by personal_id',
    }


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize('primary_replica', [None, False, True])
@pytest.mark.parametrize(
    'personal_phone_id, type_, response_name',
    [
        ('557f191e810c19729de860ea', 'yandex', 'yandex_response.json'),
        ('557f191e810c19729de860eb', 'yandex', 'default_type_response.json'),
        ('557f191e810c19729de860ea', 'deleted:12345', 'deleted_response.json'),
    ],
)
async def test_ok(
        taxi_user_api,
        load_json,
        personal_phone_id,
        type_,
        response_name,
        primary_replica,
):
    response = await _get_user_phone_by_personal(
        taxi_user_api,
        personal_phone_id,
        type_,
        primary_replica=primary_replica,
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_name)


async def _get_user_phone_by_personal(
        api, personal_phone_id, type_, primary_replica=None,
):
    body = {'personal_phone_id': personal_phone_id, 'type': type_}

    if primary_replica:
        body['primary_replica'] = primary_replica

    return await api.post(ENDPOINT, json=body)
