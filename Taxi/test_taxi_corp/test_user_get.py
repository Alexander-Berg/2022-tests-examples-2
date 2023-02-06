import datetime

import bson
import pytest

from taxi_corp.internal import consts

NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)


CORP_USER_PHONES_SUPPORTED_79 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]
CORP_USER_PHONES_SUPPORTED_712 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+712', '+79'],
        'matches': ['^712', '^79'],
    },
]


@pytest.mark.parametrize(
    [
        'passport_mock',
        'client_has_eats2',
        'url_args',
        'expected_items',
        'expected_params',
    ],
    [
        ('client1', True, {}, ['user3', 'user2', 'user1'], None),
        (
            'client1',
            True,
            {'sorting_direction': '-1', 'limit': '1', 'skip': '1'},
            ['user2'],
            {
                'amount': 3,
                'sorting_direction': -1,
                'limit': 1,
                'skip': 1,
                'sorting_field': 'fullname',
            },
        ),
        ('client3', False, {}, [], None),
        ('client1', True, {'search': 'joe'}, ['user3'], None),
        ('client1', True, {'search': 'joe@mail.com'}, ['user3'], None),
        ('client1', True, {'search': 'hoe'}, ['userX'], None),
        (
            'client1',
            True,
            {'search': '+7 (929) 111 - 22 -%2001'},
            ['user1'],
            None,
        ),
        ('client1', True, {'search': '22 - 01'}, ['user1'], None),
        ('client1', True, {'search': 'Moe'}, ['user2'], None),
        ('client1', True, {'search': '   moE '}, ['user2'], None),
        ('client1', True, {'search': 'prince'}, ['user2'], None),
        ('client1', True, {'department_id': 'd1'}, ['user2'], None),
        ('client1', True, {'department_id': 'null'}, ['user1'], None),
        (
            'client1',
            True,
            {'include_roles': 'role1'},
            ['user3', 'user1'],
            None,
        ),
        (
            'client1',
            True,
            {'include_roles': 'custom,role1'},
            ['user3', 'user2', 'user1'],
            None,
        ),
        (
            'client1',
            True,
            {
                'skip': '',
                'limit': '',
                'sorting_direction': '',
                'sorting_field': '',
            },
            ['user3', 'user2', 'user1'],
            None,
        ),
        (
            'client1',
            True,
            {'department_id': 'd1', 'include_subdepartments': 1},
            ['user3', 'user2'],
            None,
        ),
        (
            'client2',
            True,
            {'include_roles': 'custom'},
            ['userWithRolePersonalLimit', 'user_no_specific'],
            None,
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'RUB'}},
    ALLOW_CORP_BILLING_REQUESTS=True,
)
@pytest.mark.settings(USER_API_BATCH_SIZE=2)
async def test_general_get(
        taxi_corp_real_auth_client,
        client_has_eats2,
        patch,
        drive_patch,
        passport_mock,
        url_args,
        expected_items,
        expected_params,
):
    eats_spending_mock = {'spent': '200.0000'}

    @patch(
        (
            'taxi_corp.clients.corp_billing.CorpBillingClient'
            '.v2_find_employees_spendings'
        ),
    )
    async def _find_employees_spendings(*args, **kwargs):
        response = []
        for expected_item in expected_items:
            spending = {'external_ref': expected_item}
            spending.update(eats_spending_mock)
            response.append(spending)
        return response

    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'user_login'}

    @patch('taxi.clients.personal.PersonalApiClient.find')
    async def _find(data_type, request_value, *args, **kwargs):
        emails = {'joe@mail.com': 'joe_email_id'}
        return {'id': emails.get(request_value)}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [
            {'id': bson.ObjectId(phone_id), 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch('taxi.clients.user_api.UserApiClient.create_user_phone')
    async def _create_user_phone(phone, *args, **kwargs):
        def phone_to_hex(phone):
            hex_size = 24
            if phone.startswith('+'):
                phone = phone[1:]
            hex_start = 'A' * (hex_size - len(phone))
            phone_hex = hex_start + phone
            return phone_hex

        identifier = phone_to_hex(phone)

        return {'_id': bson.ObjectId(identifier), 'phone': phone}

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}/user'.format(passport_mock), params=url_args,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    if expected_params:
        response_params = response_json.copy()
        del response_params['items']
        assert response_params == expected_params
    else:
        assert response_json['amount'] == len(expected_items)
        assert response_json['sorting_direction'] == 1
        assert response_json['limit'] == 100
        assert response_json['skip'] == 0
        assert response_json['sorting_field'] == 'fullname'
    response_items = [item['_id'] for item in response_json['items']]
    assert response_items == expected_items

    if expected_items:
        assert _get_user_phone_bulk.calls

    if client_has_eats2:
        assert _find_employees_spendings.calls
        for item in response_json['items']:
            assert item['service_spendings']['eats2'] == {
                'spent': eats_spending_mock['spent'],
            }


@pytest.mark.translations(
    corp={'role.others_name': {'ru': 'role.others_name'}},
)
@pytest.mark.parametrize(
    'passport_mock, url_args, expected_items',
    [
        (
            'client1',
            {'search': 'hoe'},
            [
                {
                    '_id': 'userX',
                    'cost_center': 'hoeCostCenter',
                    'cost_centers_id': 'some_cost_centers_id',
                    'email': 'hoe@mail.com',
                    'fullname': 'Hoe',
                    'is_active': True,
                    'nickname': 'HoeTheCoolest',
                    'phone': '+79291112204',
                    'role': {'role_id': 'role1'},
                    'department_id': 'd1_1',
                    'is_deleted': True,
                    'spent': 0,
                    'link_passport': {
                        'status': 'add',
                        'updated': '2016-02-09T12:35:55+00:00',
                    },
                    'services': {
                        'drive': {
                            'is_active': False,
                            'group_id': None,
                            'soft_limit': None,
                            'hard_limit': None,
                        },
                        'eats2': {
                            'is_active': True,
                            'limits': {
                                'monthly': {
                                    'amount': '5000.00',
                                    'no_specific_limit': False,
                                },
                            },
                        },
                    },
                    'service_spendings': {
                        'eats2': {'spent': '200.0000'},
                        'taxi': {'spent': '0'},
                    },
                },
            ],
        ),
        (
            'client1',
            {'search': '+79291112202'},
            [
                {
                    '_id': 'user2',
                    'department_id': 'd1',
                    'fullname': 'Moe',
                    'nickname': 'Prince',
                    'cost_center': 'MoeCostCenter',
                    'phone': '+79291112202',
                    'role': {
                        'name': 'role.others_name',
                        'limit': 10000,
                        'classes': ['econom'],
                        'no_specific_limit': False,
                        'period': 'day',
                        'orders': {'limit': 1, 'no_specific_limit': False},
                        'geo_restrictions': [
                            {'destination': 'geo_id_2'},
                            {'source': 'geo_id_3'},
                            {
                                'source': 'geo_id_2',
                                'destination': 'geo_id_3',
                                'prohibiting_restriction': True,
                            },
                        ],
                        'restrictions': [
                            {
                                'type': 'range_date',
                                'start_date': '2000-01-01T00:00:00Z',
                                'end_date': '2000-01-02T00:00:00Z',
                            },
                            {
                                'type': 'weekly_date',
                                'start_time': '03:10:10',
                                'end_time': '03:20:10',
                                'days': [],
                            },
                            {
                                'type': 'weekly_date',
                                'start_time': '03:10:10',
                                'end_time': '03:20:10',
                                'days': ['su', 'mo'],
                            },
                        ],
                    },
                    'yandex_login': 'user_login',
                    'email': 'moe@mail.com',
                    'is_active': True,
                    'spent': 0,
                    'link_passport': {'status': 'linked'},
                    'services': {
                        'drive': {
                            'is_active': True,
                            'group_id': 'example',
                            'soft_limit': '100.00',
                            'hard_limit': '100.00',
                        },
                        'eats2': {
                            'is_active': True,
                            'limits': {
                                'monthly': {
                                    'amount': '6000.00',
                                    'no_specific_limit': False,
                                },
                            },
                        },
                    },
                    'service_spendings': {
                        'eats2': {'spent': '200.0000'},
                        'taxi': {'spent': '0'},
                    },
                },
            ],
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'RUB'}},
    ALLOW_CORP_BILLING_REQUESTS=True,
)
@pytest.mark.now(NOW.isoformat())
async def test_general_get_response(
        taxi_corp_real_auth_client,
        patch,
        drive_patch,
        passport_mock,
        url_args,
        expected_items,
):
    eats_spending_mock = {'spent': '200.0000'}

    @patch(
        (
            'taxi_corp.clients.corp_billing.CorpBillingClient'
            '.v2_find_employees_spendings'
        ),
    )
    async def _find_employees_spendings(*args, **kwargs):
        response = []
        for user in expected_items:
            spending = {'external_ref': user['_id']}
            spending.update(eats_spending_mock)
            response.append(spending)
        return response

    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'user_login'}

    @patch('taxi.clients.personal.PersonalApiClient.find')
    async def _find(data_type, request_value, *args, **kwargs):
        emails = {'joe@mail.com': 'joe_email_id'}
        return {'id': emails.get(request_value)}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [
            {'id': bson.ObjectId(phone_id), 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch('taxi.clients.user_api.UserApiClient.create_user_phone')
    async def _create_user_phone(phone, *args, **kwargs):
        def phone_to_hex(phone):
            hex_size = 24
            if phone.startswith('+'):
                phone = phone[1:]
            hex_start = 'A' * (hex_size - len(phone))
            phone_hex = hex_start + phone
            return phone_hex

        identifier = phone_to_hex(phone)

        return {'_id': bson.ObjectId(identifier), 'phone': phone}

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}/user'.format(passport_mock), params=url_args,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['amount'] == len(expected_items)
    assert response_json['sorting_direction'] == 1
    assert response_json['limit'] == 100
    assert response_json['skip'] == 0
    assert response_json['sorting_field'] == 'fullname'
    for item in response_json['items']:
        if item.get('service_spendings', {}).get('drive'):
            item['service_spendings'].pop('drive')
    assert response_json['items'] == expected_items


@pytest.mark.translations(
    corp={'role.others_name': {'ru': 'role.others_name'}},
)
@pytest.mark.parametrize(
    'client_id, user_id, expected_result',
    [
        (
            'client1',
            'user2',
            {
                '_id': 'user2',
                'department_id': 'd1',
                'fullname': 'Moe',
                'nickname': 'Prince',
                'cost_center': 'MoeCostCenter',
                'phone': '+79291112202',
                'role': {
                    'name': 'role.others_name',
                    'limit': 10000,
                    'classes': ['econom'],
                    'no_specific_limit': False,
                    'period': 'day',
                    'orders': {'limit': 1, 'no_specific_limit': False},
                    'geo_restrictions': [
                        {'destination': 'geo_id_2'},
                        {'source': 'geo_id_3'},
                        {
                            'source': 'geo_id_2',
                            'destination': 'geo_id_3',
                            'prohibiting_restriction': True,
                        },
                    ],
                    'restrictions': [
                        {
                            'type': 'range_date',
                            'start_date': '2000-01-01T00:00:00Z',
                            'end_date': '2000-01-02T00:00:00Z',
                        },
                        {
                            'type': 'weekly_date',
                            'start_time': '03:10:10',
                            'end_time': '03:20:10',
                            'days': [],
                        },
                        {
                            'type': 'weekly_date',
                            'start_time': '03:10:10',
                            'end_time': '03:20:10',
                            'days': ['su', 'mo'],
                        },
                    ],
                },
                'yandex_login': 'user_login',
                'email': 'moe@mail.com',
                'is_active': True,
                'spent': 0,
                'link_passport': {'status': 'linked'},
                'services': {
                    'drive': {
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '100.00',
                        'hard_limit': '100.00',
                    },
                    'eats2': {
                        'is_active': True,
                        'limits': {
                            'monthly': {
                                'amount': '6000.00',
                                'no_specific_limit': False,
                            },
                        },
                    },
                },
                'service_spendings': {
                    'eats2': {'spent': '0'},
                    'taxi': {'spent': '0'},
                    'drive': {'spent': '1234.00'},
                },
            },
        ),
        (
            'client1',
            'userX',
            {
                '_id': 'userX',
                'cost_center': 'hoeCostCenter',
                'cost_centers_id': 'some_cost_centers_id',
                'email': 'hoe@mail.com',
                'fullname': 'Hoe',
                'is_active': True,
                'nickname': 'HoeTheCoolest',
                'phone': '+79291112204',
                'role': {'role_id': 'role1'},
                'department_id': 'd1_1',
                'is_deleted': True,
                'spent': 0,
                'link_passport': {
                    'status': 'add',
                    'updated': '2016-02-09T12:35:55+00:00',
                },
                'services': {
                    'drive': {
                        'is_active': False,
                        'group_id': None,
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'eats2': {
                        'is_active': True,
                        'limits': {
                            'monthly': {
                                'amount': '5000.00',
                                'no_specific_limit': False,
                            },
                        },
                    },
                },
                'service_spendings': {
                    'eats2': {'spent': '0'},
                    'taxi': {'spent': '0'},
                    'drive': {'spent': '0'},
                },
            },
        ),
        (
            'client2',
            'user_no_specific',
            {
                '_id': 'user_no_specific',
                'cost_center': '',
                'cost_centers': {
                    'required': False,
                    'format': 'select',
                    'values': ['one', 'two'],
                },
                'email': 'inf@mail.com',
                'fullname': 'Infinite',
                'is_active': True,
                'nickname': '',
                'phone': '+79291112221',
                'role': {
                    'classes': [],
                    'limit': consts.INF,
                    'period': 'month',
                    'name': 'role.others_name',
                    'no_specific_limit': True,
                    'orders': {'limit': consts.INF, 'no_specific_limit': True},
                },
                'spent': 0,
                'services': {
                    'drive': {
                        'is_active': False,
                        'group_id': None,
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'eats2': {
                        'is_active': False,
                        'limits': {
                            'monthly': {
                                'amount': '6000.00',
                                'no_specific_limit': False,
                            },
                        },
                    },
                },
                'service_spendings': {
                    'eats2': {'spent': '0'},
                    'taxi': {'spent': '0'},
                    'drive': {'spent': '0'},
                },
            },
        ),
        (
            'client2',
            'userServicesActive',
            {
                '_id': 'userServicesActive',
                'cost_center': 'hoeCostCenter',
                'department_id': 'd1_1',
                'email': 'hoe@mail.com',
                'fullname': 'Hoe',
                'is_active': True,
                'nickname': 'HoeTheCoolest',
                'phone': '+79291112206',
                'role': {'role_id': 'role1'},
                'yandex_login': 'user_login',
                'spent': 0,
                'link_passport': {'status': 'linked'},
                'services': {
                    'drive': {
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '100.00',
                        'hard_limit': '100.00',
                    },
                    'eats2': {
                        'is_active': False,
                        'limits': {
                            'monthly': {
                                'amount': '5000.00',
                                'no_specific_limit': False,
                            },
                        },
                    },
                },
                'service_spendings': {
                    'eats2': {'spent': '0'},
                    'taxi': {'spent': '0'},
                    'drive': {'spent': '1234.00'},
                },
            },
        ),
        (
            'client2',
            'userWithRolePersonalLimit',
            {
                '_id': 'userWithRolePersonalLimit',
                'cost_center': 'hoeCostCenter',
                'email': 'hoe@mail.com',
                'fullname': 'Hoe',
                'is_active': True,
                'nickname': 'HoeTheCoolest',
                'phone': '+79291112209',
                'role': {
                    'limit': 1000,
                    'classes': ['econom'],
                    'name': 'role.others_name',
                    'period': 'month',
                    'no_specific_limit': False,
                    'orders': {'limit': consts.INF, 'no_specific_limit': True},
                },
                'spent': 0,
                'services': {
                    'drive': {
                        'is_active': False,
                        'group_id': None,
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'eats2': {
                        'is_active': True,
                        'limits': {
                            'monthly': {
                                'amount': '-1.000',
                                'no_specific_limit': True,
                            },
                        },
                    },
                },
                'service_spendings': {
                    'eats2': {'spent': '0'},
                    'taxi': {'spent': '0'},
                    'drive': {'spent': '0'},
                },
            },
        ),
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'RUB'}},
    ALLOW_CORP_BILLING_REQUESTS=True,
)
@pytest.mark.now(NOW.isoformat())
async def test_single_get(
        taxi_corp_auth_client,
        patch,
        drive_patch,
        client_id,
        user_id,
        expected_result,
):
    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'user_login'}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [
            {'id': bson.ObjectId(phone_id), 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch(
        (
            'taxi_corp.clients.corp_billing.CorpBillingClient'
            '.v2_find_employees_spendings'
        ),
    )
    async def _find_employees_spendings(*args, **kwargs):
        return {}

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/user/{}'.format(client_id, user_id),
    )
    assert response.status == 200
    result = await response.json()
    if result.get('service_spendings', {}).get('drive', {}).get('spent'):
        result['service_spendings']['drive']['spent'] = expected_result[
            'service_spendings'
        ]['drive']['spent']
    assert result == expected_result
    assert _get_user_phone_bulk.calls
    assert _find_employees_spendings.calls


@pytest.mark.translations(
    corp={'role.others_name': {'ru': 'role.others_name'}},
)
@pytest.mark.parametrize(
    'client_id, name_of_file_with_result',
    [
        (
            'client_for_test_multi_user_get',
            'test_several_get_expected_result.json',
        ),
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'RUB'}},
    ALLOW_CORP_BILLING_REQUESTS=True,
)
@pytest.mark.now(NOW.isoformat())
async def test_several_get(
        taxi_corp_auth_client,
        patch,
        drive_patch,
        client_id,
        name_of_file_with_result,
        load_json,
):
    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'user_login'}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        return [
            {'id': bson.ObjectId(phone_id), 'phone': hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch(
        (
            'taxi_corp.clients.corp_billing.CorpBillingClient'
            '.v2_find_employees_spendings'
        ),
    )
    async def _find_employees_spendings(*args, **kwargs):
        return {}

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/user'.format(client_id),
    )
    assert response.status == 200
    assert (await response.json()) == load_json(name_of_file_with_result)
    assert _get_user_phone_bulk.calls
    assert _find_employees_spendings.calls


@pytest.mark.parametrize(
    'passport_mock, client_id, user_id, response_code',
    [
        ('client1', '7268e11436264fb39830494f84a5f8cc', 'user2', 404),
        ('client1', 'client1', '86a2cdea4b5c4ecda9db14bcf67be7c7', 404),
        ('client1', 'client1', 'user4', 403),
    ],
    indirect=['passport_mock'],
)
async def test_single_get_fail(
        taxi_corp_real_auth_client,
        passport_mock,
        client_id,
        user_id,
        response_code,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}/user/{}'.format(client_id, user_id),
    )
    assert response.status == response_code
