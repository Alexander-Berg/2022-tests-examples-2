import pytest

from testsuite.utils import ordered_object

ENDPOINT = 'user_phones/by_personal/retrieve_bulk'


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
                'items': [
                    {
                        'personal_phone_id': '539e99e1e7e5b1f5397adc53',
                        'type': 'foo',
                    },
                ],
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


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize('primary_replica', [None, False, True])
@pytest.mark.parametrize(
    'items, response_name',
    [
        (
            [{'personal_phone_id': '557f191e810c19729de860ea'}],
            'any_type_response.json',
        ),
        (
            [
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'yandex',
                },
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'partner',
                },
                {
                    'personal_phone_id': '557f191e810c19729de860eb',
                    'type': 'yandex',
                },
            ],
            'all_found_response.json',
        ),
        (
            [
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'yandex',
                },
                # duplicate existing phone
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'yandex',
                },
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'unknown',
                },
            ],
            'some_found_response.json',
        ),
        (
            [
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'yandex',
                },
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'unknown',
                },
                # duplicate nonexisting phone
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'unknown',
                },
            ],
            'some_found_response.json',
        ),
        (
            [
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'yandex',
                },
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'unknown',
                },
            ],
            'some_found_response.json',
        ),
        (
            [
                {
                    'personal_phone_id': '557f191e810c19729de860ea',
                    'type': 'unknown',
                },
                {
                    'personal_phone_id': '557f191e810c19729de860eb',
                    'type': 'unknown',
                },
            ],
            'none_found_response.json',
        ),
        ([], 'none_found_response.json'),
    ],
)
async def test_ok(
        taxi_user_api, load_json, items, response_name, primary_replica,
):
    response = await _get_user_phones_by_personal(
        taxi_user_api, items, primary_replica=primary_replica,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), load_json(response_name), ['items'],
    )


async def _get_user_phones_by_personal(api, items, primary_replica=None):
    body = {'items': items}

    if primary_replica:
        body['primary_replica'] = primary_replica

    return await api.post(ENDPOINT, json=body)
