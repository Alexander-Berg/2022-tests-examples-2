# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime
import urllib

import bson
import pytest

from django import test as django_test

from taxi.core import db


@pytest.mark.parametrize(
    'query,code,expected',
    [
        (
            {'skip': '0', 'limit': '50'},
            200,
            {
                'news': [
                    {
                        'id': '5a1bf5f40bb9aacea5aaa94f',
                        'title': 'regex_test',
                        'content': 'test_content_3',
                        'created': '2016-10-08T14:04:27+0300',
                        'city': 'Пермь'
                    },
                    {
                        'id': '5a1bf5f40bb9aacea5aaa94e',
                        'title': 'test_title_2',
                        'content': 'test_content_2',
                        'created': '2016-10-07T14:04:27+0300',
                        'city': 'Пермь'
                    },
                    {
                        'id': 'test_id_1',
                        'title': 'test_title_1',
                        'content': 'test_content_1',
                        'created': '2016-10-06T14:04:27+0300',
                        'city': 'Москва'
                    },
                ]
            }
        ),
        (
            {
                'skip': '0',
                'limit': '50',
                'date_from': '2016-10-07T10:04:27+0300',
                'date_to': '2016-10-07T18:04:27+0300'
            },
            200,
            {
                'news': [
                    {
                        'id': '5a1bf5f40bb9aacea5aaa94e',
                        'title': 'test_title_2',
                        'content': 'test_content_2',
                        'created': '2016-10-07T14:04:27+0300',
                        'city': 'Пермь'
                    }
                ]
            }
        ),
        (
            {
                'skip': '0',
                'limit': '50',
                'date_from': '2016-10-07T10:04:27+0300',
            },
            200,
            {
                'news': [
                    {
                        'id': '5a1bf5f40bb9aacea5aaa94f',
                        'title': 'regex_test',
                        'content': 'test_content_3',
                        'created': '2016-10-08T14:04:27+0300',
                        'city': 'Пермь'
                    },
                    {
                        'id': '5a1bf5f40bb9aacea5aaa94e',
                        'title': 'test_title_2',
                        'content': 'test_content_2',
                        'created': '2016-10-07T14:04:27+0300',
                        'city': 'Пермь'
                    }
                ]
            }
        ),
        (
            {
                'skip': '0',
                'limit': '50',
                'date_to': '2016-10-07T10:04:27+0300',
            },
            200,
            {
                'news': [
                    {
                        'id': 'test_id_1',
                        'title': 'test_title_1',
                        'content': 'test_content_1',
                        'created': '2016-10-06T14:04:27+0300',
                        'city': 'Москва'
                    },
                ]
            }
        ),
        (
            {
                'title': 'Re',
            },
            200,
            {
                'news': [
                    {
                        'id': '5a1bf5f40bb9aacea5aaa94f',
                        'title': 'regex_test',
                        'content': 'test_content_3',
                        'created': '2016-10-08T14:04:27+0300',
                        'city': 'Пермь'
                    },
                ]
            }
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_get_all_news(query, code, expected):
    response = django_test.Client().get(
        '/api/news/list/?{0}'.format(urllib.urlencode(query))
    )

    assert response.status_code == code
    assert json.loads(response.content) == expected


@pytest.mark.parametrize('id,code,expected', [
    (
        '5a1bf5f40bb9aacea5aaa94e', 200, {
            'id': '5a1bf5f40bb9aacea5aaa94e',
            'title': 'test_title_2',
            'content': 'test_content_2',
            'created': '2016-10-07T14:04:27+0300',
            'city': 'Пермь'
        },
    ),
    (
        'test_id_111', 400, None,
    ),
    (
        '5a1bf6e60bb9aacea5aaa94f', 404, None,
    )
])
@pytest.mark.asyncenv('blocking')
def test_get_news(id, code, expected):
    response = django_test.Client().get('/api/news/%s/' % id)

    assert response.status_code == code
    if expected:
        assert json.loads(response.content) == expected


@pytest.mark.parametrize('id,code', [
    ('5a1bf5f40bb9aacea5aaa94e', 200),
    ('test_id_111', 400),
    ('5a1bf6e60bb9aacea5aaa94f', 404)
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_news(id, code):
    response = django_test.Client().post(
        '/api/news/%s/delete/' % id,
        json.dumps({}), 'application/json')

    assert response.status_code == code
    if code == 200:
        doc = yield db.news.find_one({'_id': id})
        assert doc is None
        assert json.loads(response.content) == {}


@pytest.mark.parametrize('id,data,code,expected', [
    (
        '5a1bf5f40bb9aacea5aaa94e',
        {
            'title': 'test_title_3',
            'content': 'test_content_3',
            'city': 'Кисловодск',
            'created': '2017-11-11 21:05:33'
        }, 200,
        {
            '_id': bson.ObjectId('5a1bf5f40bb9aacea5aaa94e'),
            'title': 'test_title_3',
            'content': 'test_content_3',
            'city': 'Кисловодск',
            'created': datetime.datetime(2017, 11, 11, 18, 5, 33)
        }
    ),
    (
        '5a1bf6e60bb9aacea5aaa94f',
        {
            'title': 'test_title_3',
            'content': 'test_content_3',
            'city': 'Кисловодск',
            'created': '2017-11-11 21:05:33'
        }, 404, None
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_edit_news(id, data, code, expected):
    response = django_test.Client().post(
        '/api/news/%s/edit/' % id,
        json.dumps(data), 'application/json')

    assert response.status_code == code
    if code == 200:
        doc = yield db.news.find_one({'_id': bson.ObjectId(id)})
        assert doc == expected
        assert json.loads(response.content) == {}


@pytest.mark.load_data(countries='test')
@pytest.mark.parametrize('data,code,expected', [
    (
        {
            'title': 'test_title',
            'content': 'test_content',
            'city': 'Москва',
            'created': '2017-11-11 21:05:33'
        }, 200,
        [
            {
                'title': 'test_title',
                'content': 'test_content',
                'city': 'Москва',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
        ]
    ),
    (
        {
            'title': 'test_title',
            'content': 'test_content',
            'city': '',
            'created': '2017-11-11 21:05:33'
        }, 200,
        [
            {
                'title': 'test_title',
                'content': 'test_content',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
        ]
    ),
    (
        {
            'title': 'test_title',
            'content': 'test_content',
            'city': 'asdef',
            'created': '2017-11-11 21:05:33'

        }, 400, None
    ),
    (
        {
            'title': 'test_title',
            'content': 'test_content',
            'cities': ['Москва', 'Кисловодск'],
            'created': '2017-11-11 21:05:33'
        }, 200,
        [
            {
                'title': 'test_title',
                'content': 'test_content',
                'city': 'Москва',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
            {
                'title': 'test_title',
                'content': 'test_content',
                'city': 'Кисловодск',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
        ]
    ),
    (
        {
            'title': 'test_title',
            'content': 'test_content',
            'country': 'rus',
            'created': '2017-11-11 21:05:33'
        }, 200,
        [
            {
                'title': 'test_title',
                'content': 'test_content',
                'city': 'Москва',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
            {
                'title': 'test_title',
                'content': 'test_content',
                'city': 'Кисловодск',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
            {
                'title': 'test_title',
                'content': 'test_content',
                'city': 'Санкт-Петербург',
                'created': datetime.datetime(2017, 11, 11, 18, 5, 33),
                'login': 'dmkurilov',
            },
        ]
    )
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_news(data, code, expected):
    response = django_test.Client().post(
        '/api/news/create/',
        json.dumps(data), 'application/json')

    assert response.status_code == code
    if code == 200:
        for exp in expected:
            query = {
                'title': 'test_title'
            }
            if exp.get('city'):
                query['city'] = exp['city']
            doc = yield db.news.find_one(query)
            doc.pop('_id')
            assert doc == exp
        assert json.loads(response.content) == {}
