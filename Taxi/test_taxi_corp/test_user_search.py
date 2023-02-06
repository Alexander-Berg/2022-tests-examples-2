import pytest

from taxi_corp.internal import consts


@pytest.mark.parametrize(
    'passport_mock, body, expected_status',
    [
        (
            'client1',
            {'user_phone': '+10001110011', 'client_id': 'client1'},
            200,
        ),
        (
            'client1',
            {'user_phone': '+90001110011', 'client_id': 'client1'},
            200,
        ),
        (
            'client1',
            {'user_phone': '+90001110011', 'client_id': 'client2'},
            403,
        ),
        (
            'client1',
            {'user_phone': '+90001110011', 'client_id': 'client1'},
            200,
        ),
        (
            'client2',
            {'user_phone': '+90001110011', 'client_id': 'client5'},
            404,
        ),
        ('client1', {}, 500),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+10', '+90'],
            'matches': ['^10', '^90'],
        },
    ],
)
async def test_user_search_status(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        body,
        expected_status,
        pd_patch,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.post(
        '/1.0/search/users', json=body,
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    'body, expected_result',
    [
        (
            {'user_phone': '+10001110011', 'client_id': 'client1'},
            {
                'users': [
                    {
                        '_id': 'user1_of_client1',
                        'fullname': 'Имя 1',
                        'phone': '+10001110011',
                        'email': 'test1@yandex-team.ru',
                        'is_active': True,
                        'role': {
                            'name': 'role.others_name',
                            'limit': 550,
                            'period': 'month',
                            'geo_restrictions': [
                                {
                                    'source': 'geo_id_1',
                                    'destination': 'geo_id_2',
                                },
                            ],
                            'classes': ['start', 'econom', 'business'],
                            'no_specific_limit': False,
                            'orders': {
                                'limit': consts.INF,
                                'no_specific_limit': True,
                            },
                        },
                        'nickname': '',
                        'cost_center': '',
                        'services': {
                            'drive': {
                                'is_active': False,
                                'group_id': None,
                                'soft_limit': None,
                                'hard_limit': None,
                            },
                            'eats2': {'is_active': False},
                        },
                        'service_spendings': {
                            'eats2': {'spent': '0'},
                            'taxi': {'spent': '0'},
                        },
                        'spent': 0,
                    },
                ],
                'total': 1,
            },
        ),
        (
            {'user_phone': '+20001110011', 'client_id': 'client1'},
            {
                'users': [
                    {
                        '_id': 'user2_of_client1',
                        'fullname': 'Имя 2',
                        'phone': '+20001110011',
                        'email': 'test2@yandex-team.ru',
                        'is_active': True,
                        'role': {
                            'name': 'role.others_name',
                            'period': 'month',
                            'limit': 550,
                            'geo_restrictions': [
                                {
                                    'source': 'geo_id_1',
                                    'destination': 'geo_id_2',
                                },
                            ],
                            'classes': ['start', 'econom', 'business'],
                            'no_specific_limit': False,
                            'orders': {
                                'limit': consts.INF,
                                'no_specific_limit': True,
                            },
                        },
                        'nickname': '',
                        'cost_center': '',
                        'services': {
                            'drive': {
                                'is_active': False,
                                'group_id': None,
                                'soft_limit': None,
                                'hard_limit': None,
                            },
                            'eats2': {'is_active': False},
                        },
                        'service_spendings': {
                            'eats2': {'spent': '0'},
                            'taxi': {'spent': '0'},
                        },
                        'spent': 0,
                    },
                ],
                'total': 1,
            },
        ),
        (
            {'user_phone': '+20001110011', 'client_id': 'client2'},
            {'users': [], 'total': 0},
        ),
        (
            {'user_phone': '+30001110011', 'client_id': 'client2'},
            {
                'users': [
                    {
                        '_id': 'user1_of_client2',
                        'fullname': 'Имя 3',
                        'phone': '+30001110011',
                        'email': 'test3@yandex-team.ru',
                        'is_active': True,
                        'role': {
                            'name': 'role.others_name',
                            'period': 'month',
                            'limit': 550,
                            'classes': ['start', 'econom'],
                            'no_specific_limit': False,
                            'orders': {
                                'limit': consts.INF,
                                'no_specific_limit': True,
                            },
                        },
                        'nickname': '',
                        'cost_center': '',
                        'services': {
                            'drive': {
                                'is_active': False,
                                'group_id': None,
                                'soft_limit': None,
                                'hard_limit': None,
                            },
                            'eats2': {'is_active': False},
                        },
                        'service_spendings': {
                            'eats2': {'spent': '0'},
                            'taxi': {'spent': '0'},
                        },
                        'spent': 0,
                    },
                ],
                'total': 1,
            },
        ),
        (
            {'user_phone': '+10001110012', 'client_id': 'client3'},
            {
                'users': [
                    {
                        '_id': 'user1_of_client3',
                        'fullname': 'Имя 4',
                        'phone': '+10001110012',
                        'email': 'test3@yandex-team.ru',
                        'is_active': True,
                        'role': {
                            'name': 'role.others_name',
                            'period': 'month',
                            'limit': consts.INF,
                            'classes': ['start'],
                            'no_specific_limit': True,
                            'orders': {
                                'limit': consts.INF,
                                'no_specific_limit': True,
                            },
                        },
                        'nickname': '',
                        'cost_center': '',
                        'services': {
                            'drive': {
                                'is_active': False,
                                'group_id': None,
                                'soft_limit': None,
                                'hard_limit': None,
                            },
                            'eats2': {'is_active': False},
                        },
                        'service_spendings': {
                            'eats2': {'spent': '0'},
                            'taxi': {'spent': '0'},
                        },
                        'spent': 0,
                    },
                ],
                'total': 1,
            },
        ),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+10', '+20', '+30'],
            'matches': ['^10', '^20', '^30'],
        },
    ],
    CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'RUB'}},
    ALLOW_CORP_BILLING_REQUESTS=True,
)
@pytest.mark.translations(
    corp={'role.others_name': {'ru': 'role.others_name'}},
)
async def test_user_search_result(
        taxi_corp_auth_client, patch, body, expected_result, pd_patch,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch(
        (
            'taxi_corp.clients.corp_billing.CorpBillingClient'
            '.v2_find_employees_spendings'
        ),
    )
    async def _find_employees_spendings(*args, **kwargs):
        return {}

    response = await taxi_corp_auth_client.post('/1.0/search/users', json=body)
    response_json = await response.json()
    for user in response_json['users']:
        if user.get('service_spendings', {}).get('drive'):
            user['service_spendings'].pop('drive')
    assert response_json == expected_result


@pytest.mark.parametrize(
    'body, expected_ids',
    [
        (
            {
                'ids': ['user1_of_client1', 'user2_of_client1'],
                'client_id': 'client1',
            },
            ['user1_of_client1', 'user2_of_client1'],
        ),
        (
            {
                'ids': ['user1_of_client1', 'user2_of_client1'],
                'client_id': 'client1',
                'limit': 1,
            },
            ['user1_of_client1'],
        ),
        (
            {
                'ids': ['user1_of_client1', 'user2_of_client1'],
                'client_id': 'client1',
                'offset': 1,
                'limit': 1,
            },
            ['user2_of_client1'],
        ),
    ],
)
async def test_user_search_by_ids(
        taxi_corp_auth_client, patch, body, expected_ids, pd_patch,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch(
        (
            'taxi_corp.clients.corp_billing.CorpBillingClient'
            '.v2_find_employees_spendings'
        ),
    )
    async def _find_employees_spendings(*args, **kwargs):
        return {}

    response = await taxi_corp_auth_client.post('/1.0/search/users', json=body)
    response_json = await response.json()

    result_ids = [u['_id'] for u in response_json['users']]
    assert result_ids == expected_ids
    assert response_json['total'] == len(body['ids'])
