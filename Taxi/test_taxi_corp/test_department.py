# pylint: disable=too-many-lines

import asyncio
import itertools

import pytest


@pytest.mark.parametrize(
    'post_content, expected_doc',
    [
        (
            {'name': 'jack', 'parent_id': None},
            {
                'name': 'jack',
                'parent_id': None,
                'ancestors': [],
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
        (
            {'name': 'jack', 'parent_id': 'd1', 'limit': {'budget': 10000.00}},
            {
                'name': 'jack',
                'parent_id': 'd1',
                'ancestors': ['d1'],
                'limits': {
                    'taxi': {'budget': 10000.00},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
        (
            {
                'name': 'jack',
                'parent_id': 'd1_1',
                'limits': {'tanker': {'budget': 11645.00}},
            },
            {
                'name': 'jack',
                'parent_id': 'd1_1',
                'ancestors': ['d1', 'd1_1'],
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': 11645.00},
                },
            },
        ),
        (
            {'name': 'jack', 'parent_id': 'd1_1_1'},
            {
                'name': 'jack',
                'parent_id': 'd1_1_1',
                'ancestors': ['d1', 'd1_1', 'd1_1_1'],
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
    ],
)
async def test_create_department(
        taxi_corp_auth_client, db, post_content, expected_doc,
):

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/department', json=post_content,
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert list(response_json) == ['_id']

    db_item = await db.corp_departments.find_one({'_id': response_json['_id']})
    assert db_item['client_id'] == 'client1'
    for key, value in expected_doc.items():
        assert db_item[key] == value

    assert db_item['counters'] == {'users': 0}


@pytest.mark.parametrize(
    'passport_mock, post_content, expected_status, expected_response',
    [
        (
            'client1',
            {},
            400,
            {
                'errors': [
                    {
                        'text': '\'parent_id\' is a required property',
                        'code': 'GENERAL',
                    },
                    {
                        'text': '\'name\' is a required property',
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'parent_id\' is a required property',
                            'path': [],
                        },
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'name\' is a required property',
                            'path': [],
                        },
                    ],
                },
            },
        ),
        (
            'client1',
            {'name': None, 'parent_id': None},
            400,
            {
                'errors': [
                    {
                        'text': 'None is not of type \'string\'',
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': 'None is not of type \'string\'',
                            'path': ['name'],
                        },
                    ],
                },
            },
        ),
        (
            'client1',
            {'name': '', 'parent_id': None},
            400,
            {
                'errors': [{'text': '\'\' is too short', 'code': 'GENERAL'}],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'\' is too short',
                            'path': ['name'],
                        },
                    ],
                },
            },
        ),
        (
            'client1',
            {'name': 'd1', 'parent_id': None},
            409,
            {
                'errors': [
                    {
                        'text': 'error.duplicate_department_name_error_code',
                        'code': 'DUPLICATE_DEPARTMENT_NAME',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'DUPLICATE_DEPARTMENT_NAME',
                            'message': (
                                'error.duplicate_department_name_error_code'
                            ),
                            'path': ['name'],
                        },
                    ],
                },
            },
        ),
        (
            'client1',
            {'name': 'd1_1', 'parent_id': 'd1'},
            409,
            {
                'errors': [
                    {
                        'text': 'error.duplicate_department_name_error_code',
                        'code': 'DUPLICATE_DEPARTMENT_NAME',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'DUPLICATE_DEPARTMENT_NAME',
                            'message': (
                                'error.duplicate_department_name_error_code'
                            ),
                            'path': ['name'],
                        },
                    ],
                },
            },
        ),
        (
            'client1',
            {'name': 'any', 'parent_id': '404'},
            404,
            {
                'errors': [
                    {'text': 'Department not found', 'code': 'GENERAL'},
                ],
                'message': 'Department not found',
                'code': 'GENERAL',
            },
        ),
        (
            # departments disable
            'client2',
            {'name': 'new', 'parent_id': None},
            403,
            {
                'errors': [{'text': 'Access denied', 'code': 'GENERAL'}],
                'message': 'Access denied',
                'code': 'GENERAL',
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_create_department_fail(
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        post_content,
        expected_status,
        expected_response,
):

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/department'.format(passport_mock), json=post_content,
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == expected_response


@pytest.mark.parametrize(
    'passport_mock', ['client2'], indirect=['passport_mock'],
)
async def test_access_by_parent_id(taxi_corp_real_auth_client, passport_mock):
    post_content = {'name': 'jack', 'parent_id': 'd1'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/department', json=post_content,
    )
    assert response.status == 403, await response.json()


async def test_get_root_children(taxi_corp_auth_client):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/client1/department',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {
        'departments': [
            {
                '_id': 'd1',
                'name': 'd1',
                'parent_id': None,
                'limit': {'budget': None},
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': 45116},
                },
            },
            {
                '_id': 'd1_dup',
                'name': 'd1_dup',
                'parent_id': None,
                'limit': {'budget': 0},
                'limits': {
                    'taxi': {'budget': 0},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ],
    }


@pytest.mark.parametrize(
    'department_id, expected_departments',
    [('d1', ['d1_1']), ('d1_1', ['d1_1_1']), ('d1_1_1', [])],
)
async def test_get_item_children(
        taxi_corp_auth_client, department_id, expected_departments,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/client1/department/{}/children'.format(department_id),
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    for expected_id, response_doc in zip(
            expected_departments, response_json['departments'],
    ):
        assert response_doc['_id'] == expected_id
        assert response_doc['parent_id'] == department_id


@pytest.mark.parametrize(
    'name, ids, expected_result',
    [
        ('not-found', None, []),
        (
            '1_1_1',
            None,
            [
                {'_id': 'd1_1_1', 'parents': ['d1', 'd1_1']},
                {'_id': 'd1_1_1_1', 'parents': ['d1', 'd1_1', 'd1_1_1']},
            ],
        ),
        (
            ' d1_1 ',
            None,
            [
                {'_id': 'd1_1', 'parents': ['d1']},
                {'_id': 'd1_1_1', 'parents': ['d1', 'd1_1']},
                {'_id': 'd1_1_1_1', 'parents': ['d1', 'd1_1', 'd1_1_1']},
            ],
        ),
        (
            None,
            None,
            [
                {'_id': 'd1', 'parents': []},
                {'_id': 'd1_1', 'parents': ['d1']},
                {'_id': 'd1_1_1', 'parents': ['d1', 'd1_1']},
                {'_id': 'd1_1_1_1', 'parents': ['d1', 'd1_1', 'd1_1_1']},
                {'_id': 'd1_dup', 'parents': []},
            ],
        ),
        (
            None,
            ['d1_1', 'd1_1_1_1'],
            [
                {'_id': 'd1_1', 'parents': ['d1']},
                {'_id': 'd1_1_1_1', 'parents': ['d1', 'd1_1', 'd1_1_1']},
            ],
        ),
        (None, [], []),
    ],
)
async def test_search_all(
        taxi_corp_auth_client,
        acl_access_data_patch,
        name,
        ids,
        expected_result,
):
    data = {'client_id': 'client1'}
    if name:
        data['name'] = name
    if ids is not None:
        data['ids'] = ids
    response = await taxi_corp_auth_client.post(
        '/1.0/search/departments', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    assert expected_result == filter_id(response_json['departments'])


def filter_id(items):
    return [
        {
            '_id': item['_id'],
            'parents': [parent['_id'] for parent in item['parents']],
        }
        for item in items
    ]


@pytest.mark.parametrize(
    'passport_mock, expected_result',
    [
        (
            'client1_manager1',
            [
                {'_id': 'd1', 'parents': []},
                {'_id': 'd1_1', 'parents': ['d1']},
                {'_id': 'd1_1_1', 'parents': ['d1', 'd1_1']},
                {'_id': 'd1_1_1_1', 'parents': ['d1', 'd1_1', 'd1_1_1']},
            ],
        ),
        (
            'client1_manager1_1',
            [
                {'_id': 'd1_1', 'parents': ['d1']},
                {'_id': 'd1_1_1', 'parents': ['d1', 'd1_1']},
                {'_id': 'd1_1_1_1', 'parents': ['d1', 'd1_1', 'd1_1_1']},
            ],
        ),
    ],
    indirect=['passport_mock'],
)
async def test_search_restrictions(
        taxi_corp_real_auth_client, passport_mock, expected_result,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/search/departments', json={'client_id': 'client1'},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert len(response_json['departments']) == response_json['total']

    response_result = [
        {
            '_id': doc['_id'],
            'parents': [parent['_id'] for parent in doc['parents']],
        }
        for doc in response_json['departments']
    ]
    assert expected_result == response_result


@pytest.mark.parametrize(
    'offset, limit, order, expected_ids',
    [
        (0, 1, 'asc', ['d1']),
        (1, 2, 'asc', ['d1_1', 'd1_1_1']),
        (5, 2, 'asc', []),
        (0, 2, 'desc', ['d1_dup', 'd1_1_1_1']),
    ],
)
async def test_search_navigation(
        taxi_corp_auth_client,
        acl_access_data_patch,
        offset,
        limit,
        order,
        expected_ids,
):
    response = await taxi_corp_auth_client.post(
        '/1.0/search/departments',
        json={
            'client_id': 'client1',
            'name': 'd1',
            'offset': offset,
            'limit': limit,
            'sorting_direction': order,
        },
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['total'] == 5
    response_ids = [doc['_id'] for doc in response_json['departments']]
    assert response_ids == expected_ids


@pytest.mark.parametrize(
    'ids, expected_result',
    [
        (
            ['d1_1', 'd1_1_1'],
            [
                {
                    '_id': 'd1_1',
                    'name': 'd1_1',
                    'parent_id': 'd1',
                    'parents': [
                        {'_id': 'd1', 'name': 'd1', 'parent_id': None},
                    ],
                    'limit': {'budget': None},
                    'limits': {
                        'taxi': {'budget': None},
                        'eats2': {'budget': None},
                        'tanker': {'budget': None},
                    },
                },
                {
                    '_id': 'd1_1_1',
                    'name': 'd1_1_1',
                    'parent_id': 'd1_1',
                    'parents': [
                        {'_id': 'd1', 'name': 'd1', 'parent_id': None},
                        {'_id': 'd1_1', 'name': 'd1_1', 'parent_id': 'd1'},
                    ],
                    'limit': {'budget': None},
                    'limits': {
                        'taxi': {'budget': None},
                        'eats2': {'budget': None},
                        'tanker': {'budget': None},
                    },
                },
            ],
        ),
    ],
)
async def test_search_ids(
        taxi_corp_auth_client, acl_access_data_patch, ids, expected_result,
):
    response = await taxi_corp_auth_client.post(
        '/1.0/search/departments', json={'client_id': 'client1', 'ids': ids},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json['total'] == len(ids)
    assert response_json['departments'] == expected_result


@pytest.mark.parametrize(
    'doc_id, put_content, expected_doc',
    [
        (
            'd1',
            {'name': 'jack', 'parent_id': None},
            {
                'name': 'jack',
                'parent_id': None,
                'ancestors': [],
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
        (
            'd1',
            {'name': 'jack', 'parent_id': 'd1_dup', 'limit': {'budget': 0}},
            {
                'name': 'jack',
                'parent_id': 'd1_dup',
                'ancestors': ['d1_dup'],
                'limits': {
                    'taxi': {'budget': 0},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
        (
            'd1_dup',
            {
                'name': 'jack',
                'parent_id': 'd1_1',
                'limits': {'tanker': {'budget': 11645.00}},
            },
            {
                'name': 'jack',
                'parent_id': 'd1_1',
                'ancestors': ['d1', 'd1_1'],
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': 11645.00},
                },
            },
        ),
    ],
)
async def test_update_department(
        taxi_corp_auth_client, db, doc_id, put_content, expected_doc,
):

    response = await taxi_corp_auth_client.put(
        '/1.0/client/client1/department/{}'.format(doc_id), json=put_content,
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == {}

    db_item = await db.corp_departments.find_one({'_id': doc_id})
    assert db_item['client_id'] == 'client1'
    for key, value in expected_doc.items():
        assert db_item[key] == value


@pytest.mark.parametrize(
    'doc_id, put_content, response_doc',
    [
        (
            'd1_dup',
            {'name': 'jack', 'parent_id': 'd1_1'},
            {
                'errors': [
                    {
                        'text': 'error.departments.locked',
                        'code': 'DEPT_UPDATE_LOCK_ERROR',
                    },
                ],
                'message': 'error.departments.locked',
                'code': 'DEPT_UPDATE_LOCK_ERROR',
            },
        ),
    ],
)
async def test_update_department_lock(
        taxi_corp_auth_client, db, patch, doc_id, put_content, response_doc,
):
    @patch('taxi_corp.api.common.departmentinfo.update_ancestors')
    async def _update_ancestors(*args, **kwargs):
        await asyncio.wait(handler_coroutine)

    handler_coroutine = taxi_corp_auth_client.put(
        '/1.0/client/client1/department/{}'.format(doc_id), json=put_content,
    )

    responses = await asyncio.gather(
        handler_coroutine,
        taxi_corp_auth_client.put(
            '/1.0/client/client1/department/{}'.format(doc_id),
            json=put_content,
        ),
    )
    for response in responses:
        if response.status == 409:
            result = response
            break
    response_json = await result.json()
    assert response_json == response_doc


@pytest.mark.parametrize(
    'put_content, expected_status, expected_response, expected_doc',
    [
        (
            {},
            400,
            {
                'errors': [
                    {
                        'text': '\'parent_id\' is a required property',
                        'code': 'GENERAL',
                    },
                    {
                        'text': '\'name\' is a required property',
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'parent_id\' is a required property',
                            'path': [],
                        },
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'name\' is a required property',
                            'path': [],
                        },
                    ],
                },
            },
            None,
        ),
        (
            {'name': None, 'parent_id': None},
            400,
            {
                'errors': [
                    {
                        'text': 'None is not of type \'string\'',
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': 'None is not of type \'string\'',
                            'path': ['name'],
                        },
                    ],
                },
            },
            None,
        ),
        (
            {'name': '', 'parent_id': None},
            400,
            {
                'errors': [{'text': '\'\' is too short', 'code': 'GENERAL'}],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'\' is too short',
                            'path': ['name'],
                        },
                    ],
                },
            },
            None,
        ),
        (
            {'name': 'jack', 'parent_id': None},
            200,
            {},
            {'name': 'jack', 'parent_id': None},
        ),
        (
            {'name': 'jack', 'parent_id': 'd1_dup'},
            200,
            {},
            {'name': 'jack', 'parent_id': 'd1_dup'},
        ),
        (
            {'name': 'd1_dup', 'parent_id': None},
            409,
            {
                'errors': [
                    {
                        'text': 'error.duplicate_department_name_error_code',
                        'code': 'DUPLICATE_DEPARTMENT_NAME',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'DUPLICATE_DEPARTMENT_NAME',
                            'message': (
                                'error.duplicate_department_name_error_code'
                            ),
                            'path': ['name'],
                        },
                    ],
                },
            },
            None,
        ),
        (  # cyclic on self
            {'name': 'department-unique', 'parent_id': 'd1'},
            409,
            {
                'errors': [
                    {
                        'text': 'error.cyclic_hierarchy_error_code',
                        'code': 'CYCLIC_HIERARCHY',
                    },
                ],
                'message': 'error.cyclic_hierarchy_error_code',
                'code': 'CYCLIC_HIERARCHY',
            },
            None,
        ),
        (  # cyclic on children
            {'name': 'department-unique', 'parent_id': 'd1_1'},
            409,
            {
                'errors': [
                    {
                        'text': 'error.cyclic_hierarchy_error_code',
                        'code': 'CYCLIC_HIERARCHY',
                    },
                ],
                'message': 'error.cyclic_hierarchy_error_code',
                'code': 'CYCLIC_HIERARCHY',
            },
            None,
        ),
    ],
)
async def test_update_department_fail(
        taxi_corp_auth_client,
        db,
        put_content,
        expected_status,
        expected_response,
        expected_doc,
):

    response = await taxi_corp_auth_client.put(
        '/1.0/client/client1/department/d1', json=put_content,
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json

    if expected_status == 200:
        assert response_json == {}
    assert response_json == expected_response

    if expected_doc:
        db_item = await db.corp_departments.find_one({'_id': 'd1'})
        assert db_item['client_id'] == 'client1'
        for key, value in expected_doc.items():
            assert db_item[key] == value


@pytest.mark.parametrize(
    'department_id, deleted_ids',
    [
        ('d1', ['d1', 'd1_1', 'd1_1_1']),
        ('d1_1', ['d1_1', 'd1_1_1']),
        ('d1_1_1', ['d1_1_1']),
        ('d6', ['d6']),
    ],
)
async def test_delete_department(
        taxi_corp_auth_client, mockserver, db, department_id, deleted_ids,
):
    @mockserver.json_handler('/corp-managers/v1/managers/search')
    async def _mock_search_managers(request):
        return mockserver.make_response(
            json={'managers': [], 'total': 0}, status=200,
        )

    no_role_id = await db.corp_clients.find_one(
        {'_id': 'client1'}, {'cabinet_only_role_id': 1},
    )
    no_role_id = no_role_id['cabinet_only_role_id']
    was_deleted = await db.corp_users.find(
        {'department_id': department_id, 'is_deleted': True},
        projection=['_id'],
    ).to_list(None)
    del_ids = [u['_id'] for u in was_deleted]

    assert (
        await db.corp_roles.count({'department_id': {'$in': deleted_ids}}) == 1
    )

    response = await taxi_corp_auth_client.delete(
        '/1.0/client/client1/department/{}'.format(department_id),
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    assert (
        await db.corp_roles.count({'department_id': {'$in': deleted_ids}}) == 0
    )

    assert await db.corp_users.count(
        {
            '_id': {'$in': del_ids},
            'role.role_id': no_role_id,
            'limits': {'$exists': False},
        },
    ) == len(del_ids)

    assert (
        await db.corp_users.count(
            {'department_id': {'$in': deleted_ids}, 'is_deleted': True},
        )
        == 0
    )

    deleted = await db.corp_departments.find(
        {'_id': {'$in': deleted_ids}}, projection=['_id', 'is_deleted'],
    ).to_list(None)

    assert len(deleted) == len(deleted_ids)
    assert all(dep['is_deleted'] for dep in deleted)


@pytest.mark.parametrize(
    'department_id, expected_status, expected_response',
    [
        (
            'd2',
            400,
            {
                'errors': [
                    {
                        'text': 'error.department_has_users_error',
                        'code': 'DEPARTMENT_HAS_USERS_ERROR',
                    },
                ],
                'message': 'error.department_has_users_error',
                'code': 'DEPARTMENT_HAS_USERS_ERROR',
            },
        ),
        (
            'd3',
            400,
            {
                'errors': [
                    {
                        'text': 'error.department_has_users_error',
                        'code': 'DEPARTMENT_HAS_USERS_ERROR',
                    },
                ],
                'message': 'error.department_has_users_error',
                'code': 'DEPARTMENT_HAS_USERS_ERROR',
            },
        ),
        (
            'd1',
            400,
            {
                'errors': [
                    {
                        'text': 'error.department_has_managers_error',
                        'code': 'DEPARTMENT_HAS_MANAGERS_ERROR',
                    },
                ],
                'message': 'error.department_has_managers_error',
                'code': 'DEPARTMENT_HAS_MANAGERS_ERROR',
            },
        ),
        (
            'd1_1',
            400,
            {
                'errors': [
                    {
                        'text': 'error.department_has_managers_error',
                        'code': 'DEPARTMENT_HAS_MANAGERS_ERROR',
                    },
                ],
                'message': 'error.department_has_managers_error',
                'code': 'DEPARTMENT_HAS_MANAGERS_ERROR',
            },
        ),
        (
            'd3_1_1_1',
            400,
            {
                'errors': [
                    {
                        'text': 'error.department_has_users_error',
                        'code': 'DEPARTMENT_HAS_USERS_ERROR',
                    },
                ],
                'message': 'error.department_has_users_error',
                'code': 'DEPARTMENT_HAS_USERS_ERROR',
            },
        ),
    ],
)
async def test_delete_department_fail(
        taxi_corp_auth_client,
        mockserver,
        load_json,
        db,
        department_id,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/corp-managers/v1/managers/search')
    async def _mock_search_managers(request):
        mock_managers_search = load_json('mock_managers_search.json')
        for manager in mock_managers_search:
            if (
                    manager['client_id'] == request.json['client_id']
                    and manager['department_id']
                    in request.json['department_ids']
            ):
                return mockserver.make_response(
                    json={'managers': [manager], 'total': 1}, status=200,
                )

        return mockserver.make_response(
            json={'managers': [], 'total': 0}, status=200,
        )

    response = await taxi_corp_auth_client.delete(
        '/1.0/client/client1/department/{}'.format(department_id),
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == expected_response


@pytest.mark.parametrize(
    'target, destination, expected_subtree',
    [
        # fake move
        (
            'd3_2',
            'd3',
            [
                {'_id': 'd3_2', 'ancestors': ['d3']},
                {'_id': 'd3_2_1', 'ancestors': ['d3', 'd3_2']},
                {'_id': 'd3_2_1_1', 'ancestors': ['d3', 'd3_2', 'd3_2_1']},
                {'_id': 'd3_2_1_2', 'ancestors': ['d3', 'd3_2', 'd3_2_1']},
                {'_id': 'd3_2_2', 'ancestors': ['d3', 'd3_2']},
            ],
        ),
        # move to root
        (
            'd3_2',
            None,
            [
                {'_id': 'd3_2', 'ancestors': []},
                {'_id': 'd3_2_1', 'ancestors': ['d3_2']},
                {'_id': 'd3_2_1_1', 'ancestors': ['d3_2', 'd3_2_1']},
                {'_id': 'd3_2_1_2', 'ancestors': ['d3_2', 'd3_2_1']},
                {'_id': 'd3_2_2', 'ancestors': ['d3_2']},
            ],
        ),
        # typical move
        (
            'd3_2',
            'd3_1_1_1',
            [
                {
                    '_id': 'd3_2',
                    'ancestors': ['d3', 'd3_1', 'd3_1_1', 'd3_1_1_1'],
                },
                {
                    '_id': 'd3_2_1',
                    'ancestors': ['d3', 'd3_1', 'd3_1_1', 'd3_1_1_1', 'd3_2'],
                },
                {
                    '_id': 'd3_2_1_1',
                    'ancestors': [
                        'd3',
                        'd3_1',
                        'd3_1_1',
                        'd3_1_1_1',
                        'd3_2',
                        'd3_2_1',
                    ],
                },
                {
                    '_id': 'd3_2_1_2',
                    'ancestors': [
                        'd3',
                        'd3_1',
                        'd3_1_1',
                        'd3_1_1_1',
                        'd3_2',
                        'd3_2_1',
                    ],
                },
                {
                    '_id': 'd3_2_2',
                    'ancestors': ['d3', 'd3_1', 'd3_1_1', 'd3_1_1_1', 'd3_2'],
                },
            ],
        ),
    ],
)
async def test_ancestors(
        taxi_corp_auth_client, db, target, destination, expected_subtree,
):

    response = await taxi_corp_auth_client.put(
        '/1.0/client/client3/department/{}'.format(target),
        json={'name': target, 'parent_id': destination},
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    stored_subtree = (
        await db.corp_departments.find(
            {'$or': [{'_id': target}, {'ancestors': target}]},
        )
        .sort([('name', 1)])
        .to_list(None)
    )
    for stored, expected in itertools.zip_longest(
            stored_subtree, expected_subtree,
    ):
        assert stored['_id'] == expected['_id']
        assert stored['ancestors'] == expected['ancestors']


@pytest.mark.parametrize(
    'target, destination, expected_counters',
    [
        # fake move
        (
            'd3_2',
            'd3',
            {'d3': 2, 'd3_2': 1, 'd3_1': 1, 'd3_1_1': 1, 'd3_1_1_1': 1},
        ),
        # move to root
        (
            'd3_2',
            None,
            {'d3': 1, 'd3_2': 1, 'd3_1': 1, 'd3_1_1': 1, 'd3_1_1_1': 1},
        ),
        # typical move
        (
            'd3_2',
            'd3_1_1_1',
            {'d3': 2, 'd3_2': 1, 'd3_1': 2, 'd3_1_1': 2, 'd3_1_1_1': 2},
        ),
    ],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_user_counters(
        taxi_corp_auth_client, db, target, destination, expected_counters,
):
    response = await taxi_corp_auth_client.put(
        '/1.0/client/client3/department/{}'.format(target),
        json={'name': target, 'parent_id': destination},
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    departments = await db.corp_departments.find(
        {'_id': {'$in': list(expected_counters.keys())}},
        projection=['counters'],
    ).to_list(None)
    counters = {
        department['_id']: department['counters']['users']
        for department in departments
    }

    assert counters == expected_counters


@pytest.mark.parametrize('name', [('',), (' ',)])
async def test_search_bad_name(taxi_corp_auth_client, name):
    response = await taxi_corp_auth_client.post(
        '/1.0/search/departments', json={'client_id': 'client1', 'name': name},
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'new_parent_id, limit, expected_status', [('d1', 1, 400), ('d1', 2, 200)],
)
async def test_create_dept_depth_limit(
        taxi_corp_auth_client,
        config_patcher,
        db,
        new_parent_id,
        limit,
        expected_status,
):
    config_patcher(CORP_DEPARTMENT_DEPTH_LIMIT=limit)

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/department',
        json={'name': 'spooky', 'parent_id': new_parent_id},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'dept, new_parent_id, limit, expected_status',
    [('d3', 'd1_1', 5, 400), ('d3', 'd1_1', 6, 200), ('d3', 'd1_1_1', 6, 400)],
)
async def test_change_dept_depth_limit(
        taxi_corp_auth_client,
        config_patcher,
        db,
        dept,
        new_parent_id,
        limit,
        expected_status,
):
    config_patcher(CORP_DEPARTMENT_DEPTH_LIMIT=limit)

    response = await taxi_corp_auth_client.put(
        '/1.0/client/client1/department/{}'.format(dept),
        json={'name': 'skeleton', 'parent_id': new_parent_id},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'passport_mock, client_id, department_id, expected_result',
    [
        (
            'client1',
            'client1',
            'd1_1',
            {
                '_id': 'd1_1',
                'name': 'd1_1',
                'parent_id': 'd1',
                'limit': {'budget': None},
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
        (
            'client4_manager4_1',
            'client4',
            'd4_1',
            {
                '_id': 'd4_1',
                'name': 'd4_1',
                'parent_id': 'd4',
                'limit': {'budget': 10000.00},
                'limits': {
                    'taxi': {'budget': 10000.00},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
        (
            'client4_manager4_1',
            'client4',
            'd4_1_1',
            {
                '_id': 'd4_1_1',
                'name': 'd4_1_1',
                'parent_id': 'd4_1',
                'limit': {'budget': None},
                'limits': {
                    'taxi': {'budget': None},
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                },
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_one(
        taxi_corp_real_auth_client,
        passport_mock,
        client_id,
        department_id,
        expected_result,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/{}/department/{}'.format(client_id, department_id),
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected_result


@pytest.mark.parametrize(
    'passport_mock, department_id, expected_status',
    [('client2', 'd1', 403), ('client4_manager4_1', 'd4', 403)],
    indirect=['passport_mock'],
)
async def test_get_one_fail(
        taxi_corp_real_auth_client,
        passport_mock,
        department_id,
        expected_status,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/department/{}'.format(department_id),
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
