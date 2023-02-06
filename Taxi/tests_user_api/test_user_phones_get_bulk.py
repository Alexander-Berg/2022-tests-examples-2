import pytest

from testsuite.utils import ordered_object


ENDPOINT = 'user_phones/get_bulk'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'foo': 'bar'}, 'Field \'ids\' is missing'),
        (
            {'ids': '1234567890abcdef'},
            (
                'Field \'ids\' is of a wrong type. '
                'Expected: arrayValue, actual: stringValue'
            ),
        ),
        ({'ids': ['strval']}, 'Invalid oid strval'),
        (
            {
                'ids': ['123459e1e7e5b1f539abcdef'],
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
    'ids, response_name',
    [
        (['123459e1e7e5b1f539abcdef'], 'no_found.json'),
        ([], 'no_found.json'),
        (
            [
                '539e99e1e7e5b1f5397adc5d',
                '539e99e1e7e5b1f5398adc5a',
                '539e99e1e7e5b1f5398adc5b',
            ],
            'all_found.json',
        ),
        (
            [
                '539e99e1e7e5b1f5397adc5d',
                '123459e1e7e5b1f539abcdef',
                '539e99e1e7e5b1f5398adc5b',
            ],
            'some_found.json',
        ),
        (['539e99e1e7e5b1f5397adc5e'], 'arbitary_type.json'),
    ],
)
async def test_get_phones(
        taxi_user_api, ids, response_name, primary_replica, load_json,
):
    response = await _get_phones_bulk(
        taxi_user_api, ids, primary_replica=primary_replica,
    )
    assert response.status_code == 200

    ordered_object.assert_eq(
        response.json(), load_json(response_name), 'items',
    )


async def _get_phones_bulk(api, phone_ids, primary_replica=None):
    request = {'ids': phone_ids}

    if primary_replica:
        request['primary_replica'] = primary_replica

    return await api.post(ENDPOINT, json=request)
