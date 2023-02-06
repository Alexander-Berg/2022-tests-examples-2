import datetime

import bson
import pytest

from taxi_corp.internal import consts
from .conftest import DELETE_FIELD

NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)
MOCK_ROLE_ID = 'mock_role_id'

GEO_RESTRICTIONS = [
    {
        'source': 'geo_id_1',
        'destination': 'geo_id_2',
        'prohibiting_restriction': True,
    },
]


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
    'post_content, expected_result',
    [
        pytest.param(
            {'role': {'role_id': 'role1'}},
            {'role': {'role_id': 'role1'}, 'limits': [{'service': 'taxi'}]},
            id='role_by_role_id',
        ),
        pytest.param(
            {
                'role.classes': ['econom', 'non-existing'],
                'nickname': 'BoeTheMan',
            },
            {
                'role.classes': ['econom'],
                'role.limit': 5000,
                'nickname': 'BoeTheMan',
            },
            id='classses_non-existing_and_nickname',
        ),
        pytest.param(
            {'role.limit': '5000'}, {'role.limit': 5000}, id='limit_as_string',
        ),
        pytest.param(
            {
                'role.limit': '123',
                'cost_center': 'BoeCostCenter',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['123'],
                },
            },
            {
                'role.limit': 123,
                'cost_center': 'BoeCostCenter',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['123'],
                },
            },
            id='cost_center',
        ),
        pytest.param(
            {'role.limit': None},
            {'role.limit': consts.INF, 'role.no_specific_limit': True},
            id='limit_is_null',
        ),
        pytest.param(
            {'role.limit': float('inf')},
            {'role.limit': consts.INF, 'role.no_specific_limit': True},
            id='limit_is_inf',
        ),
        pytest.param(
            {'role.limit': DELETE_FIELD},
            {'role.limit': consts.INF, 'role.no_specific_limit': True},
            id='without_limit',
        ),
        pytest.param(
            {'phone': '+79291112205'},
            {
                'phone': '+79291112205',
                'phone_id': bson.ObjectId('AAAAAAAAAAAAA79291112205'),
                'role.limit': 5000,
            },
            id='other_phone',
        ),
        pytest.param(
            {'role': {'role_id': 'role4'}, 'department_id': DELETE_FIELD},
            {
                'role': {'role_id': 'role4'},
                'department_id': None,
                'limits': [],
                'services': {
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'drive': {
                        'drive_user_id': None,
                        'group_id': None,
                        'is_active': False,
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'eats2': {'was_sms_sent': False},
                    'taxi': {'send_activation_sms': True},
                },
            },
            id='role_without_department',
        ),
        pytest.param(
            {
                'role.restrictions': [
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
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['su', 'mo'],
                    },
                ],
                'role.geo_restrictions': GEO_RESTRICTIONS,
            },
            {
                'role.restrictions': [
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
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['su', 'mo'],
                    },
                ],
                'role.limit': 5000,
            },
            id='fill restrictions',
        ),
        pytest.param(
            {'role.restrictions': []},
            {'role.restrictions': [], 'role.limit': 5000},
            id='empty_restrictions',
        ),
        pytest.param(
            {'email': ' BOE@mail.com  '},
            {'email': 'boe@mail.com', 'role.limit': 5000},
            id='normalize_email',
        ),
        pytest.param(
            {'services': {'drive': {'is_active': True, 'soft_limit': '1000'}}},
            {
                'role.limit': 5000,
                'services': {
                    'drive': {
                        'drive_user_id': None,
                        'is_active': True,
                        'group_id': None,
                        'soft_limit': '1000',
                        'hard_limit': '1000',
                    },
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'eats2': {'was_sms_sent': False},
                    'taxi': {'send_activation_sms': True},
                },
            },
            id='services_drive',
        ),
        pytest.param(
            {
                'services': {
                    'drive': {
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '1000',
                    },
                },
                'yandex_login': 'user_login',
            },
            {
                'role.limit': 5000,
                'services': {
                    'drive': {
                        'drive_user_id': None,
                        'is_active': True,
                        'group_id': None,
                        'soft_limit': '1000',
                        'hard_limit': '1000',
                    },
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'eats2': {'was_sms_sent': False},
                    'taxi': {'send_activation_sms': True},
                },
                'yandex_uid': '4009429274',
            },
        ),
    ],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_general_post(
        taxi_corp_auth_client,
        db,
        pd_patch,
        drive_patch,
        patch,
        patch_doc,
        post_content,
        expected_result,
):
    @patch('taxi.clients.drive.DriveClient.descriptions')
    async def _descriptions(*args, **kwargs):
        return {
            'accounts': [
                {
                    'name': 'example',
                    'soft_limit': 0,
                    'hard_limit': 0,
                    'meta': {'parent_id': 123},
                },
            ],
        }

    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):
        return {'uid': '4009429274'}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi.stq.client.put')
    async def _put_stq_task(*args, **kwargs):
        pass

    base_post_content = {
        'fullname': 'Boe',
        'phone': '+79291112214',
        'role': {'limit': 5000, 'classes': ['econom']},
        'email': 'boe@mail.com',
        'is_active': True,
        'department_id': 'd1',
    }
    base_expected_result = {
        'fullname': 'Boe',
        'phone': '+79291112214',
        'phone_id': bson.ObjectId('AAAAAAAAAAAAA79291112214'),
        'personal_phone_id': 'pd_id',
        'role': {},
        'email': 'boe@mail.com',
        'email_id': 'pd_id',
        'is_active': True,
        'department_id': 'd1',
        'services': {
            'eats': {'is_active': False, 'send_activation_sms': True},
            'drive': {
                'drive_user_id': None,
                'is_active': False,
                'group_id': None,
                'soft_limit': None,
                'hard_limit': None,
            },
            'taxi': {'send_activation_sms': True},
            'eats2': {'was_sms_sent': False},
        },
    }
    base_role = {
        'role': {
            'no_specific_limit': False,
            'classes': ['econom'],
            'client_id': 'client1',
        },
    }

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/user',
        json=patch_doc(base_post_content, post_content),
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    db_item = await db.corp_users.find_one({'_id': response_json['_id']})
    db_client = await db.corp_clients.find_one({'_id': 'client1'})

    role_id = db_item['role']['role_id']
    assert db_item['client_id'] == 'client1'
    assert isinstance(db_item['created'], datetime.datetime)
    if 'role.geo_restrictions' in post_content:
        geo_limit = await db.corp_limits.find_one(
            {'_id': db_item['limits'][0]['limit_id']},
        )
        assert geo_limit['geo_restrictions'] == GEO_RESTRICTIONS

    if 'limits' in expected_result:
        for limit in db_item['limits']:
            limit.pop('limit_id')
        assert expected_result['limits'] == db_item['limits']
    else:
        if (
                expected_result.get('services', {})
                .get('drive', {})
                .get('is_active', False)
        ):
            assert len(db_item['limits']) == 2
            drive_limit = await db.corp_limits.find_one(
                {'service': 'drive'},
                projection={
                    '_id': False,
                    'created': False,
                    'updated': False,
                    'name': False,
                    'user_id': False,
                    'title': False,
                },
            )
            assert drive_limit == {
                'client_id': 'client1',
                'department_id': 'd1',
                'limits': {
                    'orders_cost': {'period': 'month', 'value': '1000'},
                },
                'service': 'drive',
            }
        else:
            assert len(db_item['limits']) == 1
            assert db_item['limits'][0]['service'] == 'taxi'

    for name in ['_id', 'client_id', 'created', 'updated', 'role', 'limits']:
        del db_item[name]

    expected_user = patch_doc(base_expected_result, expected_result)
    del expected_user['role']
    expected_user.pop('limits', None)
    assert db_item == expected_user

    if 'role_id' not in post_content.get('role', {}):
        stripped_expected_role = {
            key: value
            for key, value in expected_result.items()
            if 'role' in key
        }
        expected_role = patch_doc(base_role, stripped_expected_role)['role']
        db_role = await db.corp_roles.find_one({'_id': role_id})

        assert db_role['user_id'] == response_json['_id']
        assert db_role['name'] == response_json['_id']

        for key, value in expected_role.items():
            assert db_role[key] == value, key

    if role_id == db_client['cabinet_only_role_id']:
        assert not _put_stq_task.calls
    else:
        assert len(_put_stq_task.calls) == 1


@pytest.mark.parametrize(
    ['extra_doc', 'expected_code', 'expected_error'],
    [
        pytest.param(
            {
                'cost_center': 'ZoeCostCenter',
                'email': 'zoe@mail.com',
                'fullname': 'Zoe',
                'is_active': True,
                'nickname': 'ZoeTheCoolest',
                'phone': '+79291112201',
                'role': {'role_id': 'role1'},
            },
            406,
            {
                'errors': [
                    {
                        'code': 'DUPLICATE_USER_PHONE',
                        'text': 'error.duplicate_user_phone_error_code',
                    },
                ],
                'message': 'error.duplicate_user_phone_error_code',
                'code': 'DUPLICATE_USER_PHONE',
            },
            id='duplicated_phone',
        ),
        pytest.param(
            {},
            400,
            {
                'errors': [
                    {
                        'code': 'USER_IS_DELETED_ERROR',
                        'text': 'user is deleted',
                    },
                ],
                'message': 'user is deleted',
                'code': 'USER_IS_DELETED_ERROR',
            },
            id='deleted_user',
        ),
        pytest.param(
            {'phone': '+79992220404', 'cost_center': 'cc' * 256 + '_'},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'Longer than maximum length 512.',
                    },
                ],
                'details': {
                    'fields': [
                        {
                            'message': 'Longer than maximum length 512.',
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'path': ['cost_center'],
                        },
                    ],
                },
                'message': 'Invalid input',
            },
            id='too long default cost center',
        ),
        pytest.param(
            {
                'phone': '+79992220404',
                'cost_centers': {
                    'format': 'select',
                    'required': True,
                    'values': [],
                },
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'error.incompatible_cost_centers',
                    },
                ],
                'details': {
                    'fields': [
                        {
                            'message': 'error.incompatible_cost_centers',
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'path': ['cost_centers', '_schema'],
                        },
                    ],
                },
                'message': 'Invalid input',
            },
            id='invalid_cost_center',
        ),
    ],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_general_post_fail(
        taxi_corp_auth_client,
        pd_patch,
        patch,
        patch_doc,
        extra_doc,
        expected_code,
        expected_error,
):
    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    base_doc = {
        'fullname': 'UserX',
        'phone': '+79291112204',
        'role': {'limit': 5000, 'classes': ['econom']},
        'email': 'boe@mail.com',
        'is_active': True,
        'department_id': 'd1',
    }
    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/user', json=patch_doc(base_doc, extra_doc),
    )
    response_json = await response.json()
    assert response.status == expected_code
    assert response_json == expected_error


@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_create_inactive_drive(
        taxi_corp_auth_client, pd_patch, patch, db,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    post_content = {
        'fullname': 'Boe',
        'phone': '+79291112214',
        'role': {'limit': 5000, 'classes': ['econom']},
        'email': 'boe@mail.com',
        'is_active': True,
        'department_id': 'd1',
        'cost_centers_id': 'cost_center_1',
    }
    expected_result = {
        'fullname': 'Boe',
        'phone': '+79291112214',
        'phone_id': bson.ObjectId('AAAAAAAAAAAAA79291112214'),
        'personal_phone_id': 'pd_id',
        'email': 'boe@mail.com',
        'email_id': 'pd_id',
        'is_active': True,
        'department_id': 'd1',
        'services': {
            'eats': {'is_active': False, 'send_activation_sms': True},
            'drive': {
                'drive_user_id': None,
                'is_active': False,
                'group_id': None,
                'soft_limit': None,
                'hard_limit': None,
            },
            'taxi': {'send_activation_sms': True},
            'eats2': {'was_sms_sent': False},
        },
        'cost_centers_id': 'cost_center_1',
    }

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client3/user', json=post_content,
    )

    assert response.status == 200

    db_item = await db.corp_users.find_one(
        {'_id': (await response.json())['_id']},
    )
    assert db_item['client_id'] == 'client3'
    for name in ['_id', 'client_id', 'created', 'updated', 'role', 'limits']:
        del db_item[name]

    assert db_item == expected_result
