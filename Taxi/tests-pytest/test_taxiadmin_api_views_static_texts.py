# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pytest

from django import test as django_test

from taxi.core import db


@pytest.mark.parametrize('data,code,expected', [
    (
        {'id': 'new_id'}, 400, None
    ),
    (
        {'page': 'test_page_text', 'id': 'old_id'}, 400, None
    ),
    (
        {'page': 'test_page_text', 'id': 'new_id'}, 200,
        {'page': 'test_page_text', '_id': 'new_id'}
    ),
    (
        {'page': 'test_page_text', 'id': 'new_id_2', 'obsolete_id': 'old_id'},
        200,
        {'page': 'test_page_text', '_id': 'new_id_2'}
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_text(data, code, expected):
    response = django_test.Client().post(
        '/api/static_text/create/',
        json.dumps(data), 'application/json'
    )

    assert response.status_code == code
    if expected:
        text = yield db.static.find_one({'_id': data['id']})
        assert text == expected
        if 'obsolete_id' in data:
            text = yield db.static.find_one({'_id': data['obsolete_id']})
            assert text is None


@pytest.mark.parametrize('data,code,expected', [
    (
        {'id': 'new_id'}, 400, None
    ),
    (
        {'page': 'test_page_text', 'id': 'old_id1'}, 404, None
    ),
    (
        {'page': 'new_test_page_text', 'id': 'old_id'}, 200,
        {'page': 'new_test_page_text', '_id': 'old_id'}
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_edit_text(data, code, expected):
    response = django_test.Client().post(
        '/api/static_text/edit/',
        json.dumps(data), 'application/json'
    )

    assert response.status_code == code
    if expected:
        text = yield db.static.find_one({'_id': data['id']})
        assert text == expected


@pytest.mark.parametrize('data,code,expected', [
    (
        {'id': 'new_id'}, 404, None
    ),
    (
        {'id': 'old_id'}, 200, True
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_text(data, code, expected):
    response = django_test.Client().post(
        '/api/static_text/delete/',
        json.dumps(data), 'application/json'
    )

    assert response.status_code == code
    if expected:
        text = yield db.static.find_one({'_id': data['id']})
        assert text is None


@pytest.mark.parametrize('code,id,expected', [
    (
        404, 'old_id1', None
    ),
    (
        200, 'test/Москва$$',
        {'page': 'Lorem ipsum dolor sit amet', 'id': 'test/Москва$$'}
    )
])
@pytest.mark.asyncenv('blocking')
def test_get_text(code, id, expected):
    response = django_test.Client().get(
        '/api/static_text/?id=%s' % id
    )

    assert response.status_code == code
    if expected:
        assert json.loads(response.content) == expected


@pytest.mark.parametrize('params,expected', [
    ({}, [0, 1, 2]),
    ({'limit': 1, 'offset': 1}, [1]),
    ({'id': 'id'}, [0, 1]),
    ({'id': 'id', 'offset': 1}, [1]),
    ({'id': 'id', 'limit': 1}, [0]),
    ({'id': 'test/Москва'}, [2]),
    ({'id': '1324'}, []),
    ({'id': '$$'}, [2])
])
@pytest.mark.asyncenv('blocking')
def test_texts_list(expected, params):
    all_texts = [
        {'text_length': 53, 'id': 'delete_id'},
        {'text_length': 11, 'id': 'old_id'},
        {'text_length': 26, 'id': 'test/Москва$$'}
    ]

    response = django_test.Client().get('/api/static_texts/', params)
    assert response.status_code == 200

    data = json.loads(response.content)
    assert data['texts'] == [all_texts[i] for i in expected]
