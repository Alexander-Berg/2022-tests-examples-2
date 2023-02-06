import json
import urllib

import pytest

from django import test as django_test

from taxi.core import db
from taxiadmin.api import apiutils


@pytest.mark.parametrize(
    'params,expected_code,expected_result',
    [
        (
            # Use default limit
            {},
            200,
            {
                'terminals': [
                    {
                        'id': '78888887799',
                        'key': 'key_1'
                    },
                    {
                        'id': '78888886699',
                        'key': 'key_2'
                    },
                    {
                        'id': 'terminal_3',
                        'key': 'key_3'
                    },
                ],
            },
        ),
        (
            # Must use max limit instead
            {'limit': 10},
            200,
            {
                'terminals': [
                    {
                        'id': '78888887799',
                        'key': 'key_1'
                    },
                    {
                        'id': '78888886699',
                        'key': 'key_2'
                    },
                    {
                        'id': 'terminal_3',
                        'key': 'key_3'
                    },
                    {
                        'id': 'terminal_4',
                        'key': 'key_4'
                    },
                    {
                        'id': 'terminal_5',
                        'key': 'key_5'
                    },
                    {
                        'id': '78888888899',
                        'key': 'key_6',
                    },
                ],
            },
        ),
        (
            {'limit': 1},
            200,
            {
                'terminals': [
                    {
                        'id': '78888887799',
                        'key': 'key_1',
                    },
                ],
            },
        ),
        (
            {'offset': 1, 'limit': 1},
            200,
            {
                'terminals': [
                    {
                        'id': '78888886699',
                        'key': 'key_2',
                    },
                ],
            },
        ),
        (
            # Must use default limit
            {'offset': 1},
            200,
            {
                'terminals': [
                    {
                        'id': '78888886699',
                        'key': 'key_2'
                    },
                    {
                        'id': 'terminal_3',
                        'key': 'key_3'
                    },
                    {
                        'id': 'terminal_4',
                        'key': 'key_4'
                    },
                ],
            },
        ),
        (
            # Must use default offset
            {'limit': 1},
            200,
            {
                'terminals': [
                    {
                        'id': '78888887799',
                        'key': 'key_1'
                    },
                ],
            },
        ),
        (
            # Must shout
            {'limit': '1_'},
            400,
            None,
        ),
        (
            # Must shout
            {'offset': '1_'},
            400,
            None,
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_terminals(monkeypatch, params, expected_code, expected_result):
    monkeypatch.setattr(apiutils, 'DEFAULT_LIMIT', 3)
    path = '/api/terminals/'
    if params:
        query = '?' + urllib.urlencode(params)
    else:
        query = ''
    response = django_test.Client().get(path + query)
    assert response.status_code == expected_code
    if expected_code == 200:
        assert json.loads(response.content) == expected_result


@pytest.mark.parametrize('terminal_id,expected_code,expected_result', [
    (
        '+78888887799',
        200,
        {
            'phone': '+78888887799',
            'key': 'key_1'
        },
    ),
    (
        '88888886699',
        404,
        None,
    ),
    (
        '78888886699',
        200,
        {
            'phone': '+78888886699',
            'key': 'key_2'
        },
    ),
    (
        None,
        400,
        None,
    ),
])
@pytest.mark.asyncenv('blocking')
def test_get_terminal(terminal_id, expected_code, expected_result):
    if terminal_id is None:
        response = django_test.Client().get('/api/terminal/')
    else:
        response = django_test.Client().get(
            '/api/terminal/?phone=%s' % terminal_id)
    assert response.status_code == expected_code
    if expected_code == 200:
        assert json.loads(response.content) == expected_result


@pytest.mark.parametrize('terminal_id,code', [
    (
        '+78888888888', 200
    ),
    (
        'terminal_3', 400
    ),
    (
        '+78888888899', 400
    ),
    (
        '+37410010010', 400
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_terminal(terminal_id, code):
    response = django_test.Client().post(
        '/api/terminal/create/',
        json.dumps({'phone': terminal_id}),
        'application/json'
    )
    assert response.status_code == code
    if code == 200:
        res = yield db.terminals.find_one({'_id': terminal_id[1:]})
        assert res is not None


@pytest.mark.parametrize('terminal_id,code', [
    (
        '78888888899', 200
    ),
    (
        '88888888899', 404
    ),
    (
        '78787878787', 404
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_terminal(terminal_id, code):
    response = django_test.Client().post(
        '/api/terminal/delete/',
        json.dumps({'phone': terminal_id}),
        'application/json'
    )
    assert response.status_code == code
    if code == 200:
        res = yield db.terminals.find_one({'_id': terminal_id})
        assert res is None


@pytest.mark.parametrize('data,code', [
    (
        {
            'phone': '+78888888899',
            'new_key': True,
            'new_phone': '+71332233456'
        }, 200
    ),
    (
        {
            'phone': '+78787878787',
        }, 404
    ),
    (
        {
            'phone': '+78888888899',
            'new_key': True,
        }, 200
    ),
    (
        {
            'phone': '88888888899',
            'new_key': True,
        }, 404
    ),
    (
        {
            'phone': '+78888888899',
            'new_phone': '+71332233456'
        }, 200
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_update_terminal(data, code):
    if code == 200:
        old_doc = yield db.terminals.find_one({'_id': data['phone'][1:]})
    response = django_test.Client().post(
        '/api/terminal/edit/',
        json.dumps(data),
        'application/json'
    )

    assert response.status_code == code
    if code == 200:
        if 'new_phone' in data:
            key_str = 'new_phone'
            old = yield db.terminals.find_one({'_id': data['phone'][1:]})
            assert old is None
        else:
            key_str = 'phone'
        res = yield db.terminals.find_one({'_id': data[key_str][1:]})
        assert res is not None
        if 'new_key' in data:
            assert old_doc['key'] != res['key']
