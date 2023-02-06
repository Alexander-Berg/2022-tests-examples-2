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


@pytest.mark.translations(
    corp={
        'role.others_name': {'ru': 'role.others_name'},
        'sms.create_user': {'ru': 'Привет!'},
    },
)
@pytest.mark.parametrize(
    'post_content, expected_result',
    [
        pytest.param(
            {
                'phone': '+79291112211',
                'role': {'role_id': 'role1'},
                'is_active': True,
                'fullname': 'Full Name',
                'email': 'test@email.com',
                'nickname': 'tester',
                'cost_center': 'TAXI',
                'department_id': 'd1',
            },
            {
                'client_id': 'client1',
                'role': {'role_id': 'role1'},
                'is_active': True,
                'fullname': 'Full Name',
                'email': 'test@email.com',
                'nickname': 'tester',
                'cost_center': 'TAXI',
                'department_id': 'd1',
                'services': {
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'eats2': {'was_sms_sent': False},
                    'drive': {
                        'drive_user_id': None,
                        'group_id': None,
                        'is_active': False,
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'taxi': {'send_activation_sms': True},
                },
            },
            id='full_data',
        ),
        pytest.param(
            {
                'phone': '+79291112211',
                'role': {'role_id': 'role1'},
                'is_active': True,
                'department_id': 'd1',
            },
            {
                'client_id': 'client1',
                'role': {'role_id': 'role1'},
                'is_active': True,
                'fullname': '',
                'email': '',
                'department_id': 'd1',
                'services': {
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'eats2': {'was_sms_sent': False},
                    'drive': {
                        'drive_user_id': None,
                        'group_id': None,
                        'is_active': False,
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'taxi': {'send_activation_sms': True},
                },
            },
            id='minimal_data',
        ),
        pytest.param(
            {
                'phone': '+79291112221',
                'role': {'classes': ['econom', 'unknown-class-name']},
                'is_active': True,
                'nickname': 'Tester',
            },
            {
                'client_id': 'client1',
                'role': {
                    'classes': ['econom'],
                    'limit': consts.INF,
                    'no_specific_limit': True,
                },
                'is_active': True,
                'fullname': '',
                'email': '',
                'nickname': 'Tester',
            },
            id='no_limit',
        ),
        pytest.param(
            {
                'phone': '+79291112221',
                'role': {
                    'limit': 5000,
                    'classes': ['econom', 'unknown-class-name'],
                    'restrictions': [
                        {
                            'type': 'range_date',
                            'start_date': '2000-01-01T00:00:00',
                            'end_date': '2000-01-02T00:00:00',
                        },
                        {
                            'type': 'weekly_date',
                            'start_time': '03:10:10',
                            'end_time': '03:20:10',
                            'days': [],
                        },
                    ],
                },
                'is_active': True,
                'nickname': 'Tester',
            },
            {
                'client_id': 'client1',
                'role': {
                    'limit': 5000,
                    'classes': ['econom'],
                    'restrictions': [
                        {
                            'type': 'range_date',
                            'start_date': '2000-01-01T00:00:00',
                            'end_date': '2000-01-02T00:00:00',
                        },
                        {
                            'type': 'weekly_date',
                            'start_time': '03:10:10',
                            'end_time': '03:20:10',
                            'days': [],
                        },
                    ],
                    'no_specific_limit': False,
                },
                'is_active': True,
                'fullname': '',
                'email': '',
                'nickname': 'Tester',
            },
            id='with restrictions',
        ),
        pytest.param(
            {
                'phone': '+79291112201',
                'role': {'role_id': 'role1'},
                'is_active': False,
                'cost_center': 'TAXI-DEV',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['123'],
                },
                'department_id': 'd1',
            },
            {
                '_id': 'user1',
                'client_id': 'client1',
                'role': {'role_id': 'role1'},
                'is_active': False,
                'cost_center': 'TAXI-DEV',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['123'],
                },
                'fullname': 'Zoe',
                'email': 'zoe@mail.com',
                'nickname': 'ZoeTheCoolest',
                'phone_id': bson.ObjectId('AAAAAAAAAAAAA79291112201'),
                'department_id': 'd1',
            },
            id='update_some_fields',
        ),
        pytest.param(
            {
                'phone': '+79291112201',
                'role': {'role_id': 'role4'},
                'is_active': False,
                'cost_center': 'TAXI-DEV',
            },
            {
                '_id': 'user1',
                'client_id': 'client1',
                'role': {'role_id': 'role4'},
                'is_active': False,
                'cost_center': 'TAXI-DEV',
                'fullname': 'Zoe',
                'email': 'zoe@mail.com',
                'nickname': 'ZoeTheCoolest',
                'phone_id': bson.ObjectId('AAAAAAAAAAAAA79291112201'),
                'personal_phone_id': 'pd_id',
                'department_id': None,
            },
            id='write_cabinet_only_role_within_department',
        ),
    ],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_general_patch(
        taxi_corp_auth_client,
        pd_patch,
        db,
        patch,
        post_content,
        expected_result,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_auth_client.patch(
        '/1.0/client/client1/user', json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert '_id' in response_json
    user_id = response_json['_id']
    db_item = await db.corp_users.find_one({'_id': user_id})

    if 'role_id' not in post_content['role']:
        db_role = await db.corp_roles.find_one({'user_id': user_id})
        assert db_item['role']['role_id'] == db_role['_id']
        assert db_role['name'] == user_id

        for key, value in expected_result['role'].items():
            assert db_role[key] == value

    del expected_result['role']
    for key, value in expected_result.items():
        assert db_item[key] == value, key


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'client_id, post_content, required_code, required_errors',
    [
        pytest.param(
            'client1',
            {},
            400,
            [
                '\'phone\' is a required property',
                '\'role\' is a required property',
                '\'is_active\' is a required property',
            ],
            id='empty_content',
        ),
        pytest.param(
            'client1',
            {'phone': '', 'is_active': ''},
            400,
            [
                '\'\' is not of type \'boolean\'',
                '\'role\' is a required property',
            ],
            id='required_fields',
        ),
        pytest.param(
            'client1',
            {'phone': 12345, 'is_active': 'true'},
            400,
            [
                '12345 is not of type \'string\'',
                '\'true\' is not of type \'boolean\'',
                '\'role\' is a required property',
            ],
            id='type_of_fields',
        ),
        pytest.param(
            'client1',
            {
                'phone': '+71234567890',
                'is_active': False,
                'role': {'unexpected': ''},
            },
            400,
            [
                '{\'unexpected\': \'\'} '
                'is not valid under any of the given schemas',
            ],
            id='empty_role.role_id_and_role.classes',
        ),
        pytest.param(
            '12345',
            {
                'phone': '+71234567890',
                'is_active': False,
                'role': {'role_id': 'role4'},
            },
            404,
            ['Client not found'],
            id='invalid_client_id',
        ),
        pytest.param(
            'client1',
            {
                'phone': '+71234567890',
                'is_active': False,
                'role': {'role_id': 'some_role_id'},
            },
            400,
            ['Role not found'],
            id='invalid_role_id',
        ),
        pytest.param(
            'client1',
            {
                'phone': '+71234567890',
                'is_active': False,
                'role': {'role_id': 'role4'},
                'department_id': 'invalid',
            },
            404,
            ['Department not found'],
            id='invalid_department_id',
        ),
        pytest.param(
            'client1',
            {
                'fullname': 'Boe',
                'email': 'boe@mail.com',
                'phone': '+71234567890',
                'is_active': False,
                'role': {'role_id': 'role3'},
                'department_id': 'd2',
            },
            400,
            ['role_id should belong to this department_id'],
            id='role_outside_department',
        ),
        pytest.param(
            'client1',
            {
                'phone': '+71234567891',
                'is_active': True,
                'role': {
                    'role_id': 'role1',
                    'classes': ['econom'],
                    'limit': 200,
                    'no_specific_limit': False,
                },
            },
            400,
            [
                '{\'role_id\': \'role1\', \'classes\': [\'econom\'], '
                '\'limit\': 200, \'no_specific_limit\': False} '
                'is not valid under any of the given schemas',
            ],
            id='sending_all_fields',
        ),
        pytest.param(
            'client1',
            {
                'fullname': 'Boe',
                'email': 'boe@mail.com',
                'phone': '+71234567890',
                'is_active': False,
                'role': {'role_id': 'role1'},
                'department_id': 'd1',
                'cost_centers': {
                    'required': 'invalid format',
                    'format': 'invalid value',
                    'values': 'invalid type',
                },
            },
            400,
            [
                '\'invalid format\' is not of type \'boolean\'',
                (
                    '\'invalid value\' is not one of '
                    '[\'select\', \'text\', \'mixed\']'
                ),
                '\'invalid type\' is not of type \'array\'',
            ],
            id='invalid_cost_centers',
        ),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+712', '+79'],
            'matches': ['^712', '^79'],
        },
    ],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_712)
async def test_general_patch_fail(
        taxi_corp_real_auth_client,
        pd_patch,
        patch,
        passport_mock,
        client_id,
        post_content,
        required_code,
        required_errors,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/{}/user'.format(client_id), json=post_content,
    )
    response_json = await response.json()
    assert response.status == required_code, response_json
    response_errors = [
        error['text'] for error in response_json.get('errors', [])
    ]
    assert response_errors == required_errors


@pytest.mark.parametrize(
    'client_id, post_content',
    [
        (
            'client1',
            {
                'phone': '+79291112211',
                'role': {'role_id': 'role1'},
                'is_active': True,
                'fullname': 'Full Name',
                'email': 'test@email.com',
                'nickname': 'tester',
                'cost_center': 'TAXI',
                'department_id': 'd1',
            },
        ),
    ],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_general_created_patch(
        taxi_corp_auth_client, pd_patch, db, patch, client_id, post_content,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_auth_client.patch(
        '/1.0/client/{}/user'.format(client_id), json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, await response.json()
    db_item = await db.corp_users.find_one({'_id': response_json['_id']})
    assert 'created' in db_item
    assert isinstance(db_item['created'], datetime.datetime)
