import pytest

from testsuite.utils import ordered_object


ENDPOINT = 'user_phones/staff/retrieve_bulk'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'foo': 'bar'}, 'Field \'group\' is missing'),
        (
            {'group': 123},
            (
                'Field \'group\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        ({'group': 'foobarbaz'}, None),
    ],
    ids=['missing group', 'int group', 'bad group'],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    if message:
        assert response.json()['code'] == '400'


@pytest.mark.parametrize('group', ['yandex', 'taxi'])
async def test_retrieve_bulk(taxi_user_api, load_json, group):
    response_name = 'response_{}.json'.format(group)

    response = await _retrieve_staff_phones(taxi_user_api, group)
    assert response.status_code == 200

    ordered_object.assert_eq(
        response.json(), load_json(response_name), ['items'],
    )


async def _retrieve_staff_phones(api, group):
    body = {'group': group}

    return await api.post(ENDPOINT, json=body)
