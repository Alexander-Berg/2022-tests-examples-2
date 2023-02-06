# pylint: disable=too-many-lines

import datetime

import pytest

from taxi_corp.internal import consts
from .conftest import DELETE_FIELD


ROLE_MAP = {
    'role1': {
        '_id': 'role1',
        'name': 'Продавцы',
        'counters': {'users': 0},
        'limit': 5000,
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': False,
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
        'department_id': None,
    },
    'role2': {
        '_id': 'role2',
        'name': 'managers',
        'counters': {'users': 0},
        'limit': 5000,
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': False,
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
    },
    'role3': {
        '_id': 'role3',
        'name': 'role.cabinet_only_name',
        'counters': {'users': 0},
        'limit': 0,
        'classes': ['econom'],
        'deletable': False,
        'putable': False,
        'is_cabinet_only': True,
        'no_specific_limit': False,
        'department_id': 'department_id_1',
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
    },
    'role4': {
        '_id': 'role4',
        'name': 'some role',
        'counters': {'users': 0},
        'limit': 0,
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': False,
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
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
            {
                'type': 'weekly_date',
                'start_time': '03:10:10',
                'end_time': '03:20:10',
                'days': ['su', 'mo'],
            },
        ],
    },
    'role5': {
        '_id': 'role5',
        'counters': {'users': 0},
        'limit': 3000,
        'name': 'fockers',
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': False,
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
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
                'days': ['su', 'mo'],
            },
        ],
    },
    'role6': {
        '_id': 'role6',
        'counters': {'users': 0},
        'limit': 8000,
        'name': 'empty restrictions',
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'no_specific_limit': False,
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
        'restrictions': [],
    },
    'role7': {
        '_id': 'role7',
        'counters': {'users': 0},
        'name': 'no_specific_limit',
        'classes': ['econom'],
        'deletable': True,
        'putable': True,
        'limit': consts.INF,
        'no_specific_limit': True,
        'period': 'month',
        'orders': {'limit': consts.INF, 'no_specific_limit': True},
    },
    'role8': {
        '_id': 'role8',
        'counters': {'users': 0},
        'name': 'role.cabinet_only_name',
        'classes': ['econom'],
        'is_cabinet_only': True,
        'deletable': False,
        'putable': False,
        'limit': consts.INF,
        'no_specific_limit': True,
        'period': 'day',
        'orders': {'limit': 1000, 'no_specific_limit': False},
        'geo_restrictions': [
            {'source': 'geo_id_1', 'destination': 'geo_id_2'},
            {},
        ],
    },
}


@pytest.mark.parametrize(
    'client_id, url_args, expected_result',
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
)
@pytest.mark.config(CORP_CATEGORIES={'__default__': {'econom': 'econom'}})
async def test_general_get(
        taxi_corp_auth_client, client_id, url_args, expected_result,
):

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/role'.format(client_id), params=url_args,
    )

    response_result = await response.json()
    assert response.status == 200, response_result
    assert response_result == expected_result


@pytest.mark.parametrize(
    'passport_mock, post_content, expected_result',
    [
        (
            'client2',
            {
                'name': 'engineers',
                'limit': 7000,
                'classes': ['econom', 'non-existing'],
            },
            {
                'name': 'engineers',
                'limit': 7000,
                'no_specific_limit': False,
                'classes': ['econom'],
            },
        ),
        (
            'client2',
            {'name': 'engineers', 'limit': 7000, 'classes': ['econom']},
            {
                'name': 'engineers',
                'limit': 7000,
                'no_specific_limit': False,
                'classes': ['econom'],
            },
        ),
        (
            'client2',
            {'name': 'engineers', 'limit': 0, 'classes': ['econom']},
            {
                'name': 'engineers',
                'limit': 0,
                'no_specific_limit': False,
                'classes': ['econom'],
            },
        ),
        (
            'client2',
            {'name': 'engineers', 'classes': ['econom']},
            {
                'name': 'engineers',
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
            },
        ),
        (
            'client2',
            {'name': 'engineers', 'limit': consts.INF, 'classes': ['econom']},
            {
                'name': 'engineers',
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
            },
        ),
        (
            'client1',
            {'name': 'engineers', 'limit': 0, 'classes': ['econom']},
            {
                'name': 'engineers',
                'limit': 0,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': None,
            },
        ),
        (
            'client1',
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'department_id': None,
            },
            {
                'name': 'engineers',
                'limit': 0,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': None,
            },
        ),
        (
            'client1',
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'department_id': 'department1',
            },
            {
                'name': 'engineers',
                'limit': 0,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': 'department1',
            },
        ),
        (
            'client1',
            {
                'name': 'engineers',
                'limit': 1000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': 'department1',
            },
            {
                'name': 'engineers',
                'limit': 1000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': 'department1',
            },
        ),
        (
            'client1',
            {
                'name': 'engineers',
                'limit': 0,
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
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['su', 'mo'],
                    },
                ],
            },
            {
                'name': 'engineers',
                'limit': 0,
                'no_specific_limit': False,
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
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['su', 'mo'],
                    },
                ],
            },
        ),
        (
            'client1',
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'restrictions': [],
            },
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'restrictions': [],
                'no_specific_limit': False,
            },
        ),
        (
            'client2',
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'restrictions': [],
                'geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_2'},
                ],
            },
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'restrictions': [],
                'no_specific_limit': False,
                'geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_2'},
                ],
            },
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(ALLOW_CORP_BILLING_REQUESTS=True)
async def test_general_post(
        patch,
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        post_content,
        expected_result,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/role'.format(passport_mock), json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    db_item = await db.corp_roles.find_one({'_id': response_json['_id']})
    for key, value in expected_result.items():
        assert db_item[key] == value

    assert (
        await db.secondary.corp_limits.count({'role_id': response_json['_id']})
        == 2
    )

    assert db_item['counters'] == {'users': 0}


@pytest.mark.parametrize(
    'method, url, passport_mock',
    [
        ('POST', '/1.0/client/client1/role', 'client1'),
        ('PUT', '/1.0/client/client1/role/role2', 'client1'),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'request_content, response_code, response_error',
    [
        ({'name': 'Продавцы'}, 406, 'error.duplicate_role_name_error'),
        ({'name': 123}, 400, '123 is not of type \'string\''),
        ({'classes': [123]}, 400, '123 is not of type \'string\''),
        ({'no_specific_limit': None}, 400, 'None is not of type \'boolean\''),
        ({'limit': 'invalid'}, 400, 'limit should be a positive int or None'),
        ({'limit': -100}, 400, 'limit should be a positive int or None'),
        ({'limit': 10 ** 8}, 400, 'error.validate_max_limit'),
        ({'name': DELETE_FIELD}, 400, '\'name\' is a required property'),
        (
            {'excess_field': 'value'},
            400,
            'Additional properties are not allowed '
            '(\'excess_field\' was unexpected)',
        ),
        ({'department_id': 'not_found'}, 404, 'Department not found'),
        (
            {'limit': 1000, 'no_specific_limit': True},
            400,
            'limit should be an infinite',
        ),
        (
            {
                'restrictions': [
                    {
                        'type': 'range_date',
                        'start_date': '0000-01-02T00:00:00',
                        'end_date': '2000-01-01T00:00:00',
                    },
                ],
            },
            400,
            'invalid format for start_date',
        ),
        (
            {
                'restrictions': [
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
                'restrictions': [
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
                'restrictions': [
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
        (
            {
                'restrictions': [
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
                'geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_not_found'},
                ],
            },
            400,
            'source or destination points are not found',
        ),
    ],
)
async def test_general_edit_fail(
        patch,
        taxi_corp_real_auth_client,
        patch_doc,
        passport_mock,
        method,
        url,
        request_content,
        response_code,
        response_error,
):
    base_content = {'name': 'new role', 'limit': 5000, 'classes': ['econom']}
    response = await taxi_corp_real_auth_client.request(
        method, url, json=patch_doc(base_content, request_content),
    )

    response_json = await response.json()
    assert response.status == response_code, response_json
    assert len(response_json['errors']) == 1
    assert response_json['errors'][0]['text'] == response_error


@pytest.mark.parametrize(
    'client_id, role_id, expected_result',
    [
        ('client1', 'role1', ROLE_MAP['role1']),
        ('client2', 'role7', ROLE_MAP['role7']),
        ('client2', 'role8', ROLE_MAP['role8']),
    ],
)
@pytest.mark.config(
    CORP_CATEGORIES={'__default__': {'econom': 'country_econom'}},
)
async def test_single_get(
        taxi_corp_auth_client, client_id, role_id, expected_result,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/role/{}'.format(client_id, role_id),
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == expected_result


@pytest.mark.parametrize(
    'client_id, role_id, response_code',
    [('client1', 'role404', 404), ('client404', 'role1', 404)],
)
async def test_single_get_fail(
        taxi_corp_auth_client, client_id, role_id, response_code,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/role/{}'.format(client_id, role_id),
    )

    assert response.status == response_code


@pytest.mark.parametrize(
    'passport_mock, role_id, put_content, expected_content',
    [
        (
            'client1',
            'role2',
            {
                'name': 'managers',
                'limit': 9000,
                'classes': ['econom', 'non-existing'],
                'period': 'day',
                'orders': {'no_specific_limit': True},
            },
            {
                'name': 'managers',
                'limit': 9000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': None,
                'period': 'day',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
            },
        ),
        (
            'client1',
            'role2',
            {
                'name': 'managers',
                'limit': 9000,
                'classes': ['econom'],
                'department_id': None,
            },
            {
                'name': 'managers',
                'limit': 9000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': None,
            },
        ),
        (
            'client1',
            'role2',
            {
                'name': 'managers',
                'limit': 9000,
                'classes': ['econom'],
                'department_id': 'department1',
            },
            {
                'name': 'managers',
                'limit': 9000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': 'department1',
            },
        ),
        (
            'client1',
            'role2',
            {
                'name': 'managers',
                'limit': 5000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': 'department1',
            },
            {
                'name': 'managers',
                'limit': 5000,
                'no_specific_limit': False,
                'classes': ['econom'],
                'department_id': 'department1',
            },
        ),
        (
            'client1',
            'role2',
            {
                'name': 'engineers',
                'limit': 0,
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
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['su', 'mo'],
                    },
                ],
            },
            {
                'name': 'engineers',
                'limit': 0,
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
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['su', 'mo'],
                    },
                ],
            },
        ),
        (
            'client1',
            'role2',
            {
                'name': 'engineers',
                'limit': 0,
                'classes': ['econom'],
                'restrictions': [],
            },
            {'name': 'engineers', 'limit': 0, 'classes': ['econom']},
        ),
        (
            'client1',
            'role2',
            {
                'name': 'managers',
                'limit': consts.INF,
                'classes': ['econom', 'non-existing'],
            },
            {
                'name': 'managers',
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
                'department_id': None,
            },
        ),
        (
            'client2',
            'role8',
            {
                'name': 'managers',
                'limit': consts.INF,
                'classes': ['econom', 'non-existing'],
                'geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_2'},
                ],
            },
            {
                'name': 'managers',
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
                'department_id': None,
                'geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_2'},
                ],
            },
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(ALLOW_CORP_BILLING_REQUESTS=True)
async def test_single_put(
        patch,
        taxi_corp_auth_client,
        db,
        passport_mock,
        role_id,
        put_content,
        expected_content,
):
    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/role/{}'.format(passport_mock, role_id),
        json=put_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == {}

    db_item = await db.corp_roles.find_one({'_id': role_id})

    for key, value in expected_content.items():
        assert db_item[key] == value

    if not db_item.get('is_cabinet_only'):
        assert await db.secondary.corp_limits.count({'role_id': role_id}) == 2

    db_user_items = await db.corp_users.find(
        {'role.role_id': role_id},
    ).to_list(None)

    for user in db_user_items:
        if put_content.get('department_id'):
            assert user['department_id'] == put_content['department_id']


@pytest.mark.parametrize(
    'passport_mock, client_id, role_id, response_code, response_error',
    [
        ('client1', 'client404', 'role2', 404, 'Client not found'),
        ('client1', 'client1', 'role404', 404, 'Role not found'),
        # FIXME: error.cabinet_only_update_attempt_error
        ('client1', 'client1', 'role3', 403, 'Access denied'),
    ],
    indirect=['passport_mock'],
)
async def test_single_put_fail(
        patch,
        taxi_corp_real_auth_client,
        passport_mock,
        client_id,
        role_id,
        response_code,
        response_error,
):
    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/role/{}'.format(client_id, role_id),
        json={'name': 'new role', 'limit': 5000, 'classes': ['econom']},
    )

    response_json = await response.json()
    assert response.status == response_code, response_json
    assert len(response_json['errors']) == 1
    assert response_json['errors'][0]['text'] == response_error


@pytest.mark.parametrize(
    'client_id, role_id, limit, classes, restrictions',
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
                    'start_date': '2000-01-01T00:00:00',
                    'end_date': '2000-01-02T00:00:00',
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
)
@pytest.mark.config(ALLOW_CORP_BILLING_REQUESTS=True)
async def test_single_delete(
        patch,
        taxi_corp_auth_client,
        db,
        client_id,
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

    response = await taxi_corp_auth_client.delete(
        '/1.0/client/{}/role/{}'.format(client_id, role_id),
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
    'passport_mock, client_id, role_id, expected_code',
    [
        ('client1', 'client1', '3c5c40a3cfc14447805e3c69f59aec2c', 404),
        ('client1', 'e5defdc1c4e54439b4b6fc40b5da46d8', 'role2', 404),
        ('client1', 'client1', 'role3', 403),
    ],
    indirect=['passport_mock'],
)
async def test_single_delete_fail(
        taxi_corp_real_auth_client,
        passport_mock,
        client_id,
        role_id,
        expected_code,
):
    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/{}/role/{}'.format(client_id, role_id),
    )

    assert response.status == expected_code


@pytest.mark.parametrize(
    'passport_mock, post_content',
    [
        (
            'client2',
            {
                'name': 'engineers',
                'limit': 7000,
                'classes': ['econom', 'non-existing'],
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_general_time_fields_post(
        patch, taxi_corp_real_auth_client, db, passport_mock, post_content,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/role'.format(passport_mock), json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    db_item = await db.corp_roles.find_one({'_id': response_json['_id']})
    assert 'created' in db_item and 'updated' in db_item
    assert isinstance(db_item['created'], datetime.datetime)
    assert isinstance(db_item['updated'], datetime.datetime)


@pytest.mark.parametrize(
    'passport_mock, post_content, put_content',
    [
        (
            'client1',
            {'name': 'from_client2', 'limit': 9000, 'classes': ['econom']},
            {'name': 'from_client1', 'limit': 8000, 'classes': ['econom']},
        ),
    ],
    indirect=['passport_mock'],
)
async def test_single_updated_field_put(
        patch,
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        post_content,
        put_content,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/role'.format(passport_mock), json=post_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    db_item = await db.corp_roles.find_one({'_id': response_json['_id']})
    role_id = db_item['_id']
    prev_created = db_item['created']
    prev_updated = db_item['updated']

    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/role/{}'.format(passport_mock, role_id),
        json=put_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json
    assert response_json == {}
    fresh_item = await db.corp_roles.find_one({'_id': role_id})
    assert fresh_item['created'] == prev_created
    assert fresh_item['updated'] > prev_updated
