import pytest


ENDPOINT = 'user_phones/staff/save_affilation'


@pytest.mark.parametrize(
    'body, message',
    [
        ({'state': 'give', 'group': 'yandex'}, 'Field \'phones\' is missing'),
        (
            {'phones': 42, 'state': 'give', 'group': 'yandex'},
            (
                'Field \'phones\' is of a wrong type. '
                'Expected: arrayValue, actual: intValue'
            ),
        ),
        ({'phones': [], 'group': 'yandex', 'state': 'give'}, None),
        (
            {'phones': ['+79991112233'], 'state': 'give'},
            'Field \'group\' is missing',
        ),
        (
            {'phones': ['+79991112233'], 'state': 'give', 'group': {}},
            (
                'Field \'group\' is of a wrong type. '
                'Expected: stringValue, actual: objectValue'
            ),
        ),
        (
            {
                'phones': ['+79991112233'],
                'state': 'give',
                'group': 'foobarbaz',
            },
            None,
        ),
        (
            {'phones': ['+79991112233'], 'group': 'taxi'},
            'Field \'state\' is missing',
        ),
        (
            {'phones': ['+79991112233'], 'state': [], 'group': 'taxi'},
            (
                'Field \'state\' is of a wrong type. '
                'Expected: stringValue, actual: arrayValue'
            ),
        ),
        (
            {
                'phones': ['+79991112233'],
                'state': 'foobarbaz',
                'group': 'taxi',
            },
            None,
        ),
    ],
    ids=[
        'missing phones',
        'int phones',
        'empty phones',
        'missing group',
        'obj group',
        'bad group',
        'missing state',
        'array state',
        'bad state',
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post(ENDPOINT, json=body)
    assert response.status_code == 400
    if message:
        assert response.json()['code'] == '400'


@pytest.mark.parametrize('state', ['give', 'revoke'])
@pytest.mark.parametrize('group', ['yandex', 'taxi'])
async def test_save_affilation(taxi_user_api, mongodb, group, state):
    phones = ['+71112223344', '+71112223345', '+71112223346']

    response = await _save_affilation(taxi_user_api, phones, group, state)

    assert response.status_code == 200
    assert response.json() == {}

    staff_field = '{}_staff'.format(group)

    affilations = mongodb.user_phones.find(
        {'phone': {'$in': phones}}, [staff_field],
    )

    for affilation in affilations:
        if state == 'give':
            assert affilation[staff_field] is True
        elif state == 'revoke':
            assert staff_field not in affilation


async def _save_affilation(api, phones, group, state):
    body = {'phones': phones, 'group': group, 'state': state}

    return await api.post(ENDPOINT, json=body)
