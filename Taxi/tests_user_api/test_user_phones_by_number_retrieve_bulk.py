import pytest

from testsuite.utils import ordered_object

ENDPOINT = 'user_phones/by_number/retrieve_bulk'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'foo': 'bar'}, 'Field \'items\' is missing'),
        (
            {'items': 'foo'},
            (
                'Field \'items\' is of a wrong type. '
                'Expected: arrayValue, actual: stringValue'
            ),
        ),
        (
            {
                'items': [{'phone': '+71112223344', 'type': 'foo'}],
                'primary_replica': 'not_a_bool',
            },
            (
                'Field \'primary_replica\' is of a wrong type. '
                'Expected: booleanValue, actual: stringValue'
            ),
        ),
    ],
    ids=['missing items', 'str items', 'bad primary_replica'],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize('primary_replica', [None, False, True])
@pytest.mark.parametrize(
    'items, response_name',
    [
        ([{'phone': '+71112223344'}], 'any_type_response.json'),
        (
            [
                {'phone': '+71112223344', 'type': 'yandex'},
                {'phone': '+71112223344', 'type': 'partner'},
                {'phone': '+71112223345', 'type': 'yandex'},
            ],
            'all_found_response.json',
        ),
        (
            [
                {'phone': '+71112223344', 'type': 'yandex'},
                {'phone': '+71112223344', 'type': 'unknown'},
            ],
            'some_found_response.json',
        ),
        (
            [
                {'phone': '+71112223344', 'type': 'yandex'},
                # duplicate nonexisting phone
                {'phone': '+71112223344', 'type': 'unknown'},
                {'phone': '+71112223344', 'type': 'unknown'},
            ],
            'some_found_response.json',
        ),
        (
            [
                {'phone': '+71112223344', 'type': 'yandex'},
                # duplicate existing phone
                {'phone': '+71112223344', 'type': 'yandex'},
                {'phone': '+71112223344', 'type': 'unknown'},
            ],
            'some_found_response.json',
        ),
        (
            [
                {'phone': '+71112223344', 'type': 'unknown'},
                {'phone': '+71112223345', 'type': 'unknown'},
            ],
            'none_found_response.json',
        ),
        ([], 'none_found_response.json'),
    ],
)
async def test_ok(
        taxi_user_api, load_json, items, response_name, primary_replica,
):
    response = await _get_user_phones_by_numbers(
        taxi_user_api, items, primary_replica=primary_replica,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), load_json(response_name), ['items'],
    )


async def _get_user_phones_by_numbers(api, items, primary_replica=None):
    body = {'items': items}

    if primary_replica:
        body['primary_replica'] = primary_replica

    return await api.post(ENDPOINT, json=body)
