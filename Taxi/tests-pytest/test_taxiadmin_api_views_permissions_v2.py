# coding=utf-8
from __future__ import unicode_literals

import json
from collections import namedtuple

import pytest

from django import test as django_test

from taxi.internal import dbh


@pytest.mark.parametrize('name,permissions,code,expected', [
    (
        'group',
        [
            {'id': 'edit_subventions', 'mode': 'unrestricted'},
            {
                'id': 'view_subventions',
                'mode': 'countries_filter',
                'countries_filter': ['rus', 'blr']
            }
        ],
        200,
        'create_expected.json'
    ),
    (
        'Админы',
        [
            {'id': 'edit_subventions', 'mode': 'unrestricted'},
            {
                'id': 'view_subventions',
                'mode': 'countries_filter',
                'countries_filter': ['rus', 'blr']
            }
        ],
        400,
        None
    ),
    (
        'group',
        [
            {'id': 'edit_subventions', 'mode': 'unrestricted'},
            {
                'id': 'edit_subventions',
                'mode': 'countries_filter',
                'countries_filter': ['rus', 'blr']
            }
        ],
        400,
        None
    ),
    ('group', [{'id': 'nonexistent', 'mode': 'unrestricted'}], 400, None),
    (
        'group',
        [
            {
                'id': 'edit_subventions',
                'mode': 'countries_filter',
                'countries_filter': ['rus', 'mda']
            }
        ],
        400,
        None
    ),
    ('group', [{'id': 'edit_subventions', 'mode': 'test'}], 400, None),
    ('group', ['edit_subventions', 'view_subventions'], 400, None)
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_group(
        name, permissions, code, expected, patch, load, areq_request
):
    @patch('uuid.uuid4')
    def uuid():
        return namedtuple('uuid4', 'hex')('group_id')

    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(200, body=json.dumps({
            'permissions': {
                'new_permission_id': {
                    'category_id': 'new_category_id',
                    'action': 'new_action',
                    'category_name': 'новая категория',
                    'comment': 'new_comment',
                }
            }
        }))

    response = django_test.Client().post(
        '/api/permissions/v2/groups/create/',
        data=json.dumps({
            'name': name,
            'permissions': permissions
        }),
        content_type='application/json'
    )

    assert response.status_code == code

    if response.status_code == 200:
        expected = json.loads(load(expected))
        assert json.loads(response.content) == expected
        db_group = yield dbh.admin_groups.Doc.find_one_by_id('group_id')
        assert db_group.name == name
        assert db_group.permissions == permissions


@pytest.mark.parametrize('group_id,name,permissions,code,expected', [
    (
        'group_1',
        'group',
        [{'id': 'edit_subventions', 'mode': 'unrestricted'}],
        200,
        'update_expected_1.json'
    ),
    (
        'group_2',
        'Адмиралы',
        [
            {
                'id': 'edit_exams',
                'mode': 'countries_filter',
                'countries_filter': ['rus']
            }
        ],
        200,
        'update_expected_2.json'
    ),
    (
        'group_3',
        'Адмиралы',
        [{'id': 'edit_exams', 'mode': 'unrestricted'}],
        400,
        None
    ),
    (
        'group_3',
        'group',
        [{'id': 'edit_subventions', 'mode': None}],
        400,
        None
    ),
    (
        'group_4',
        'group',
        [{'id': 'edit_subventions', 'mode': 'unrestricted'}],
        404,
        None
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_group(
        group_id, permissions, code, name, expected, load, areq_request
):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(200, body=json.dumps({
            'permissions': {
                'new_permission_id': {
                    'category_id': 'new_category_id',
                    'action': 'new_action',
                    'category_name': 'новая категория',
                    'comment': 'new_comment',
                }
            }
        }))

    response = django_test.Client().post(
        '/api/permissions/v2/groups/%s/update/' % group_id,
        data=json.dumps({
            'name': name,
            'permissions': permissions
        }),
        content_type='application/json'
    )

    assert response.status_code == code

    if response.status_code == 200:
        expected = json.loads(load(expected))
        assert json.loads(response.content) == expected
        db_group = yield dbh.admin_groups.Doc.find_one_by_id(group_id)
        assert db_group.name == name
        assert db_group.permissions == permissions


@pytest.mark.parametrize('group_id,code,expected', [
    ('group_1', 200, 'get_expected_old.json'),
    ('group_3', 200, 'get_expected_new.json'),
    ('group_4', 404, 'get_expected_not_found.json')
])
@pytest.mark.asyncenv('blocking')
def test_get_group(group_id, code, expected, load, areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(200, body=json.dumps({
            'permissions': {
                'new_permission_id': {
                    'category_id': 'new_category_id',
                    'action': 'new_action',
                    'category_name': 'новая категория',
                    'comment': 'new_comment',
                }
            }
        }))

    expected = json.loads(load(expected))
    response = django_test.Client().get(
        '/api/permissions/v2/groups/%s/' % group_id
    )
    assert response.status_code == code
    assert json.loads(response.content) == expected


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_group():
    group_id = 'group_3'
    response = django_test.Client().post(
        '/api/permissions/v2/groups/%s/delete/' % group_id
    )
    assert response.status_code == 200

    db_group = yield dbh.admin_groups.Doc.find_many_by_ids([group_id])
    assert db_group == []

    response = django_test.Client().post(
        '/api/permissions/v2/groups/%s/delete/' % group_id
    )

    assert response.status_code == 404


@pytest.mark.parametrize('params,expected_indexes', [
    ({'limit': 1, 'offset': 1}, [1]),
    ({'name': 'адми'}, [0, 1]),
    ({}, [0, 1, 2]),
    ({'name': 'Страны'}, [2]),
    ({'permission_id': 'view_classification_rules'}, [0, 2]),
    ({'permission_id': 'taxi_scripts'}, [1, 2]),
])
@pytest.mark.asyncenv('blocking')
def test_get_groups_list(params, expected_indexes):
    full_data = [
        {'id': 'group_1', 'name': 'Админы'},
        {'id': 'group_2', 'name': 'Адмиралы'},
        {'id': 'group_3', 'name': 'Страны'}
    ]
    expected = [full_data[i] for i in expected_indexes]
    response = django_test.Client().get(
        '/api/permissions/v2/groups/list/', params
    )
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data == {'groups': expected}


@pytest.mark.asyncenv('blocking')
def test_get_all_categories(areq_request):

    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(200, body=json.dumps({
            'permissions': {
                'new_permission_id': {
                    'category_id': 'new_category_id',
                    'action': 'new_action',
                    'category_name': 'новая категория',
                    'comment': 'new_comment',
                }
            }
        }))

    response = django_test.Client().get('/api/permissions/v2/list/')
    assert response.status_code == 200

    response = django_test.Client().get(
        '/api/permissions/v2/list/?from_api_admin=true'
    )
    assert response.status_code == 200
