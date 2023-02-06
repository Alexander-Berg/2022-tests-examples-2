# pylint: disable=too-many-lines

import datetime

import pytest

from taxi_corp.internal import consts
from .conftest import DELETE_FIELD


ROLE_MAP = {
    'role1': {
        '_id': 'role1',
        'counters': {'users': 0},
        'deletable': True,
        'department_id': None,
        'name': 'Продавцы',
        'putable': True,
        'services': {
            'eats2': {
                'is_active': True,
                'limits': {
                    'monthly': {
                        'amount': '6000.00',
                        'no_specific_limit': False,
                    },
                },
            },
            'taxi': {
                'classes': ['econom'],
                'limit': 5000,
                'no_specific_limit': False,
                'period': 'month',
                'orders': {'limit': 1000, 'no_specific_limit': False},
            },
        },
    },
    'role2': {
        '_id': 'role2',
        'counters': {'users': 0},
        'deletable': True,
        'department_id': None,
        'name': 'managers',
        'putable': True,
        'services': {
            'eats2': {
                'is_active': True,
                'limits': {
                    'monthly': {
                        'amount': '6000.00',
                        'no_specific_limit': False,
                    },
                },
            },
            'taxi': {
                'classes': ['econom'],
                'limit': 5000,
                'no_specific_limit': False,
                'period': 'day',
                'orders': {'limit': 1000, 'no_specific_limit': False},
            },
        },
    },
    'role3': {
        '_id': 'role3',
        'is_cabinet_only': True,
        'counters': {'users': 0},
        'deletable': False,
        'department_id': 'department_id_1',
        'name': 'role.cabinet_only_name',
        'putable': False,
        'services': {
            'eats2': {'is_active': False, 'limits': {}},
            'taxi': {
                'classes': ['econom'],
                'limit': 0,
                'no_specific_limit': False,
                'period': 'month',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
            },
        },
    },
    'role4': {
        '_id': 'role4',
        'counters': {'users': 0},
        'deletable': True,
        'department_id': None,
        'name': 'some group',
        'putable': True,
        'services': {
            'eats2': {
                'is_active': True,
                'limits': {
                    'monthly': {
                        'amount': '6000.00',
                        'no_specific_limit': False,
                    },
                },
            },
            'taxi': {
                'classes': ['econom'],
                'limit': 0,
                'no_specific_limit': False,
                'period': 'month',
                'orders': {'limit': 1000, 'no_specific_limit': False},
                'restrictions': [
                    {
                        'end_date': '2000-01-02T00:00:00',
                        'start_date': '2000-01-01T00:00:00',
                        'type': 'range_date',
                    },
                    {
                        'days': [],
                        'end_time': '03:20:10',
                        'start_time': '03:10:10',
                        'type': 'weekly_date',
                    },
                    {
                        'days': ['su', 'mo'],
                        'end_time': '03:20:10',
                        'start_time': '03:10:10',
                        'type': 'weekly_date',
                    },
                ],
                'geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_2'},
                    {'source': 'geo_id_1'},
                ],
            },
        },
    },
    'role5': {
        '_id': 'role5',
        'counters': {'users': 0},
        'deletable': True,
        'department_id': None,
        'name': 'fockers',
        'putable': True,
        'services': {
            'eats2': {
                'is_active': True,
                'limits': {
                    'monthly': {
                        'amount': '6000.00',
                        'no_specific_limit': False,
                    },
                },
            },
            'taxi': {
                'classes': ['econom'],
                'limit': 3000,
                'no_specific_limit': False,
                'period': 'month',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
                'restrictions': [
                    {
                        'end_date': '2000-01-02T00:00:00',
                        'start_date': '2000-01-01T00:00:00',
                        'type': 'range_date',
                    },
                    {
                        'days': ['su', 'mo'],
                        'end_time': '03:20:10',
                        'start_time': '03:10:10',
                        'type': 'weekly_date',
                    },
                ],
            },
        },
    },
    'role6': {
        '_id': 'role6',
        'counters': {'users': 0},
        'deletable': True,
        'department_id': None,
        'name': 'empty restrictions',
        'putable': True,
        'services': {
            'eats2': {
                'is_active': True,
                'limits': {
                    'monthly': {
                        'amount': '6000.00',
                        'no_specific_limit': False,
                    },
                },
            },
            'taxi': {
                'classes': ['econom'],
                'limit': 8000,
                'no_specific_limit': False,
                'period': 'month',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
                'restrictions': [],
            },
        },
    },
    'role7': {
        '_id': 'role7',
        'counters': {'users': 0},
        'deletable': True,
        'department_id': None,
        'name': 'no_specific_limit',
        'putable': True,
        'services': {
            'eats2': {
                'is_active': True,
                'limits': {
                    'monthly': {
                        'amount': '6000.00',
                        'no_specific_limit': False,
                    },
                },
            },
            'taxi': {
                'classes': ['econom'],
                'limit': 200,
                'no_specific_limit': False,
                'period': 'month',
                'orders': {'limit': 1000, 'no_specific_limit': False},
            },
        },
    },
    'role8': {
        '_id': 'role8',
        'counters': {'users': 0},
        'deletable': False,
        'putable': False,
        'department_id': None,
        'name': 'role.cabinet_only_name',
        'is_cabinet_only': True,
        'services': {
            'eats2': {'is_active': False, 'limits': {}},
            'taxi': {
                'classes': ['econom'],
                'limit': consts.INF,
                'no_specific_limit': True,
                'period': 'month',
                'orders': {'limit': 1000, 'no_specific_limit': False},
            },
        },
    },
    'role10': {
        '_id': 'role10',
        'counters': {'users': 0},
        'deletable': False,
        'putable': False,
        'department_id': None,
        'name': 'role.cabinet_only_name',
        'is_cabinet_only': True,
        'services': {
            'eats2': {'is_active': False, 'limits': {}},
            'taxi': {
                'limit': 0,
                'period': 'month',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
            },
        },
    },
}


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED={'rus': {'currency': 'RUB'}})
@pytest.mark.parametrize(
    'passport_mock, url_args, expected_result',
    [
        (
            'client1',
            {},
            {
                'amount': 4,
                'sorting_direction': 1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'name',
                'items': [
                    ROLE_MAP['role3'],
                    ROLE_MAP['role6'],
                    ROLE_MAP['role2'],
                    ROLE_MAP['role1'],
                ],
            },
        ),
        (
            'client1',
            {'sorting_direction': -1, 'limit': 1, 'skip': 1},
            {
                'amount': 4,
                'sorting_direction': -1,
                'limit': 1,
                'skip': 1,
                'sorting_field': 'name',
                'items': [ROLE_MAP['role2']],
            },
        ),
        (
            'client2',
            {},
            {
                'amount': 4,
                'sorting_direction': 1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'name',
                'items': [
                    ROLE_MAP['role8'],
                    ROLE_MAP['role5'],
                    ROLE_MAP['role7'],
                    ROLE_MAP['role4'],
                ],
            },
        ),
        (
            'client1',
            {'department_id': 'department_id_1'},
            {
                'amount': 1,
                'sorting_direction': 1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'name',
                'items': [ROLE_MAP['role3']],
            },
        ),
        (
            'client1',
            {'department_id': 'null'},
            {
                'amount': 3,
                'sorting_direction': 1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'name',
                'items': [
                    ROLE_MAP['role6'],
                    ROLE_MAP['role2'],
                    ROLE_MAP['role1'],
                ],
            },
        ),
        (
            'client1',
            {'ids': 'role2,role3'},
            {
                'amount': 2,
                'sorting_direction': 1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'name',
                'items': [ROLE_MAP['role3'], ROLE_MAP['role2']],
            },
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_DEFAULT_CATEGORIES={'rus': ['econom']})
async def test_general_get(
        taxi_corp_real_auth_client, passport_mock, url_args, expected_result,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/group', params=url_args,
    )

    response_result = await response.json()
    assert response.status == 200, response_result
    assert response_result == expected_result


@pytest.mark.parametrize(
    ['passport_mock', 'post_content', 'expected_role', 'expected_eats2_limit'],
    [
        pytest.param(
            'client2',
            {
                'name': 'engineers',
                'services': {
                    'taxi': {
                        'no_specific_limit': False,
                        'limit': 7000,
                        'classes': ['econom', 'non-existing'],
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
            },
            {
                'name': 'engineers',
                'limit': 7000,
                'no_specific_limit': False,
                'classes': ['econom'],
            },
            {
                'name': 'engineers',
                'service': consts.EATS2_SERVICE,
                'limits': {
                    'orders_cost': {'value': '6000.00', 'period': 'month'},
                },
            },
            id='simple create',
        ),
        pytest.param(
            'client3',
            {
                'name': 'engineers',
                'services': {
                    'taxi': {
                        'no_specific_limit': False,
                        'limit': 7000,
                        'classes': ['econom', 'non-existing'],
                        'period': 'day',
                        'orders': {'limit': 1000, 'no_specific_limit': False},
                    },
                },
            },
            {
                'name': 'engineers',
                'limit': 7000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'period': 'day',
                'orders': {'limit': 1000, 'no_specific_limit': False},
            },
            {
                'name': 'engineers',
                'service': consts.EATS2_SERVICE,
                'limits': {
                    'orders_cost': {'value': '0.0000', 'period': 'month'},
                },
            },
            id='simple create without eats',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_general_post(
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        post_content,
        expected_role,
        expected_eats2_limit,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/group', json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    db_role_item = await db.corp_roles.find_one({'_id': response_json['_id']})
    for key, value in expected_role.items():
        assert db_role_item[key] == value

    db_eats2_item = await db.corp_limits.find_one(
        {'role_id': response_json['_id'], 'service': consts.EATS2_SERVICE},
    )
    for key, value in expected_eats2_limit.items():
        assert db_eats2_item[key] == value

    assert (
        await db.secondary.corp_limits.count({'role_id': response_json['_id']})
        == 2
    )
    assert db_role_item['counters'] == {'users': 0}


@pytest.mark.parametrize(
    'method, url, passport_mock',
    [
        ('POST', '/1.0/group', 'client1'),
        ('PUT', '/1.0/group/role2', 'client1'),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'request_content, response_code, response_error',
    [
        ({'name': 'Продавцы'}, 406, 'error.duplicate_role_name_error'),
        (
            {'services.taxi.limit': 'invalid'},
            400,
            'limit should be a positive int or None',
        ),
        (
            {'services.taxi.limit': -100},
            400,
            'limit should be a positive int or None',
        ),
        ({'services.taxi.limit': 10 ** 8}, 400, 'error.validate_max_limit'),
        ({'name': DELETE_FIELD}, 400, '\'name\' is a required property'),
        (
            {'excess_field': 'value'},
            400,
            'Additional properties are not allowed '
            '(\'excess_field\' was unexpected)',
        ),
        ({'department_id': 'not_found'}, 404, 'Department not found'),
        (
            {
                'services.taxi.limit': 1000,
                'services.taxi.no_specific_limit': True,
            },
            400,
            'limit should be an infinite',
        ),
        (
            {
                'services.taxi.restrictions': [
                    {
                        'type': 'range_date',
                        'start_date': '2000-01-02T00:00:00',
                        'end_date': '2000-01-01T00:00:00',
                    },
                ],
            },
            400,
            '\'start_date\' must be less than \'end_date\'',
        ),
        (
            {
                'services.taxi.restrictions': [
                    {
                        'type': 'weekly_date',
                        'start_time': '03:20:10',
                        'end_time': '03:10:10',
                        'days': ['mo'],
                    },
                ],
            },
            400,
            '\'start_time\' must be less than \'end_time\'',
        ),
        (
            {
                'services.taxi.restrictions': [
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['mo', 'mo'],
                    },
                ],
            },
            400,
            '{\'type\': \'weekly_date\', \'start_time\': \'03:10:10\', '
            '\'end_time\': \'03:20:10\', \'days\': [\'mo\', \'mo\']} '
            'is not valid under any of the given schemas',
        ),
    ],
)
async def test_general_edit_fail(
        taxi_corp_real_auth_client,
        patch_doc,
        passport_mock,
        method,
        url,
        request_content,
        response_code,
        response_error,
):
    # base_content = {'name': 'new role', 'limit': 5000, 'classes': ['econom']}
    base_content = {
        'name': 'new role',
        'services': {
            'taxi': {'limit': 5000, 'classes': ['econom']},
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
    }
    response = await taxi_corp_real_auth_client.request(
        method, url, json=patch_doc(base_content, request_content),
    )

    response_json = await response.json()
    assert response.status == response_code, response_json
    assert len(response_json['errors']) == 1
    assert response_json['errors'][0]['text'] == response_error


@pytest.mark.parametrize(
    'passport_mock, role_id, expected_result',
    [
        ('client1', 'role3', ROLE_MAP['role3']),
        ('client2', 'role7', ROLE_MAP['role7']),
        ('client2', 'role8', ROLE_MAP['role8']),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_DEFAULT_CATEGORIES={'rus': ['econom']})
async def test_single_get(
        taxi_corp_real_auth_client, passport_mock, role_id, expected_result,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/group/{}'.format(role_id),
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == expected_result


@pytest.mark.parametrize(
    'client_id, role_id, response_code',
    [('client1', 'role404', 404), ('client404', 'role1', 404)],
)
async def test_single_get_fail(
        taxi_corp_auth_client,
        acl_access_data_patch,
        client_id,
        role_id,
        response_code,
):
    response = await taxi_corp_auth_client.get('/1.0/group/{}'.format(role_id))

    assert response.status == response_code


@pytest.mark.parametrize(
    [
        'passport_mock',
        'role_id',
        'put_content',
        'expected_role',
        'expected_eats2_limit',
    ],
    [
        (
            'client1',
            'role2',
            {
                'name': 'engineers',
                'services': {
                    'taxi': {
                        'no_specific_limit': False,
                        'limit': 7000,
                        'classes': ['econom', 'non-existing'],
                        'geo_restrictions': [
                            {'source': 'geo_id_3', 'destination': 'geo_id_4'},
                            {'source': 'geo_id_3', 'destination': 'geo_id_3'},
                        ],
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
            },
            {
                'name': 'engineers',
                'limit': 7000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': None,
                'geo_restrictions': [
                    {'source': 'geo_id_3', 'destination': 'geo_id_4'},
                    {'source': 'geo_id_3', 'destination': 'geo_id_3'},
                ],
            },
            {
                'name': 'engineers',
                'service': consts.EATS2_SERVICE,
                'department_id': None,
                'limits': {
                    'orders_cost': {'value': '6000.00', 'period': 'month'},
                },
            },
        ),
        (
            'client1',
            'role2',
            {
                'name': 'engineers',
                'services': {
                    'taxi': {
                        'no_specific_limit': False,
                        'limit': 7000,
                        'classes': ['econom', 'non-existing'],
                        'period': 'week',
                        'orders': {'no_specific_limit': True},
                    },
                },
            },
            {
                'name': 'engineers',
                'limit': 7000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': None,
                'period': 'week',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
            },
            {
                'name': 'engineers',
                'service': consts.EATS2_SERVICE,
                'department_id': None,
                'limits': {
                    'orders_cost': {
                        'value': '0.0000',  # overwrite eats2 limit (6000.00)
                        'period': 'month',
                    },
                },
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_single_put(
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        role_id,
        put_content,
        expected_role,
        expected_eats2_limit,
):
    response = await taxi_corp_real_auth_client.put(
        '/1.0/group/{}'.format(role_id), json=put_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == {}

    db_item = await db.corp_roles.find_one({'_id': role_id})
    for key, value in expected_role.items():
        assert db_item[key] == value

    db_eats2_item = await db.corp_limits.find_one(
        {'role_id': role_id, 'service': consts.EATS2_SERVICE},
    )
    for key, value in expected_eats2_limit.items():
        assert db_eats2_item[key] == value

    assert await db.secondary.corp_limits.count({'role_id': role_id}) == 2

    db_user_items = await db.corp_users.find(
        {'role.role_id': role_id},
    ).to_list(None)

    for user in db_user_items:
        if put_content.get('department_id'):
            assert user['department_id'] == put_content['department_id']


@pytest.mark.parametrize(
    'passport_mock, role_id, response_code, response_error',
    [
        ('client1', 'role404', 404, 'Role not found'),
        ('client1', 'role3', 403, 'Access denied'),
    ],
    indirect=['passport_mock'],
)
async def test_single_put_fail(
        taxi_corp_real_auth_client,
        passport_mock,
        role_id,
        response_code,
        response_error,
):
    response = await taxi_corp_real_auth_client.put(
        '/1.0/group/{}'.format(role_id),
        json={
            'name': 'new role',
            'services': {'taxi': {'limit': 5000, 'classes': ['econom']}},
        },
    )

    response_json = await response.json()
    assert response.status == response_code, response_json
    assert len(response_json['errors']) == 1
    assert response_json['errors'][0]['text'] == response_error


@pytest.mark.parametrize(
    'passport_mock, role_id, limit, classes, restrictions',
    [
        (
            'client1',
            'role2',
            5000,
            ['business', 'econom', 'non-existing'],
            None,
        ),
        ('client1', 'role6', 8000, ['business', 'econom', 'non-existing'], []),
        (
            'client2',
            'role5',
            3000,
            ['business', 'econom', 'non-existing'],
            [
                {
                    'type': 'range_date',
                    'end_date': '2000-01-02T00:00:00',
                    'start_date': '2000-01-01T00:00:00',
                },
                {
                    'type': 'weekly_date',
                    'start_time': '03:10:10',
                    'end_time': '03:20:10',
                    'days': ['su', 'mo'],
                },
            ],
        ),
        pytest.param(
            'client2', 'role7', 200, ['econom'], None, id='without_limit',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_single_delete(
        taxi_corp_real_auth_client,
        passport_mock,
        db,
        role_id,
        limit,
        classes,
        restrictions,
):
    former_users = await db.corp_users.find({'role.role_id': role_id}).to_list(
        None,
    )
    former_role = await db.corp_roles.find_one({'_id': role_id})

    assert former_users

    response = await taxi_corp_real_auth_client.delete(
        '/1.0/group/{}'.format(role_id),
    )
    response_json = await response.json()
    assert response.status == 200, 'Response is %s' % response_json
    assert not await db.corp_roles.find_one({'_id': role_id})

    updated_users = await db.corp_users.find(
        {'_id': {'$in': [u['_id'] for u in former_users]}},
        projection=['role.role_id'],
    ).to_list(None)
    new_roles = await db.corp_roles.find(
        {'user_id': {'$in': [u['_id'] for u in former_users]}},
    ).to_list(None)
    new_roles_by_user_id = {r['user_id']: r for r in new_roles}

    for user in updated_users:
        user_id = user['_id']
        role_id = user['role']['role_id']
        new_role = new_roles_by_user_id[user_id]

        assert new_role['_id'] == role_id
        assert new_role.get('limit') == limit
        assert new_role.get('period') == former_role.get('period')
        assert new_role.get('orders') == former_role.get('orders')
        assert new_role['classes'] == classes
        assert new_role.get('restrictions') == restrictions
        geo_restrictions = former_role.get('geo_restrictions')
        assert new_role.get('geo_restrictions') == geo_restrictions


@pytest.mark.parametrize(
    'passport_mock, role_id, expected_code',
    [
        ('client1', '3c5c40a3cfc14447805e3c69f59aec2c', 404),
        ('client1', 'role3', 403),
    ],
    indirect=['passport_mock'],
)
async def test_single_delete_fail(
        taxi_corp_real_auth_client, passport_mock, role_id, expected_code,
):
    response = await taxi_corp_real_auth_client.delete(
        '/1.0/group/{}'.format(role_id),
    )

    assert response.status == expected_code


@pytest.mark.parametrize(
    'passport_mock, post_content',
    [
        (
            'client2',
            {
                'name': 'engineers',
                'services': {
                    'taxi': {
                        'no_specific_limit': False,
                        'limit': 7000,
                        'classes': ['econom', 'non-existing'],
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
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_general_time_fields_post(
        taxi_corp_real_auth_client, db, passport_mock, post_content,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/group', json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    db_role_item = await db.corp_roles.find_one({'_id': response_json['_id']})
    assert 'created' in db_role_item and 'updated' in db_role_item
    assert isinstance(db_role_item['created'], datetime.datetime)
    assert isinstance(db_role_item['updated'], datetime.datetime)

    db_eats2_item = await db.corp_limits.find_one(
        {'role_id': response_json['_id'], 'service': consts.EATS2_SERVICE},
    )
    assert 'created' in db_eats2_item and 'updated' in db_role_item
    assert isinstance(db_eats2_item['created'], datetime.datetime)
    assert isinstance(db_eats2_item['updated'], datetime.datetime)


@pytest.mark.parametrize(
    'passport_mock, post_content, put_content',
    [
        (
            'client1',
            # {'name': 'from_client2', 'limit': 9000, 'classes': ['econom']},
            {
                'name': 'from_client2',
                'services': {'taxi': {'limit': 9000, 'classes': ['econom']}},
            },
            {
                'name': 'from_client1',
                'services': {'taxi': {'limit': 8000, 'classes': ['econom']}},
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_single_updated_field_put(
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        post_content,
        put_content,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/group', json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    db_item = await db.corp_roles.find_one({'_id': response_json['_id']})
    role_id = db_item['_id']
    prev_created = db_item['created']
    prev_updated = db_item['updated']

    response = await taxi_corp_real_auth_client.put(
        '/1.0/group/{}'.format(role_id), json=put_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == {}
    fresh_item = await db.corp_roles.find_one({'_id': role_id})
    assert fresh_item['created'] == prev_created
    assert fresh_item['updated'] > prev_updated
