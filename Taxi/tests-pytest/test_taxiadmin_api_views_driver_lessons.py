# -*- coding: utf-8 -*-

import json

import pytest
from django import test as django_test

from taxi.conf import settings
from taxi.core import db


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('uri',
                         ['/', '/8127312631623', '/very/strange/query'])
def test_get_request(areq_request, uri):
    expected_data = {'test_key': 'test_value'}
    req_params = {'arg': 'param', 'arg_arg': 'param'}

    @areq_request
    def aresponse(method, url, headers, params, **kwargs):
        assert method == 'GET'
        assert params == req_params
        assert headers['X-API-Key'] == settings.DRIVER_LESSONS_API_KEY
        assert url == settings.DRIVER_LESSONS_API_HOST + '/admin/lessons' + uri
        return areq_request.response(200, json.dumps(expected_data))

    response = django_test.Client().get('/api/driver_lessons' + uri,
                                        req_params)
    assert aresponse.call
    assert response.status_code == 200
    assert json.loads(response.content) == expected_data


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('uri',
                         ['/', '/8127312631623', '/very/strange/query'])
@pytest.inline_callbacks
def test_post_request(areq_request, uri):
    expected_data = {'test_key': 'test_value'}

    @areq_request
    def aresponse(method, url, headers, **kwargs):
        assert method == 'POST'
        assert headers['X-API-Key'] == settings.DRIVER_LESSONS_API_KEY
        assert url == settings.DRIVER_LESSONS_API_HOST + '/admin/lessons' + uri
        return areq_request.response(200, json.dumps(expected_data))

    response = django_test.Client().post('/api/driver_lessons' + uri,
                                         data=json.dumps(expected_data),
                                         content_type='application/json')
    assert aresponse.call
    assert response.status_code == 200
    assert json.loads(response.content) == expected_data

    doc = yield db.log_admin.find_one({'action': 'edit_driver_lessons'})
    assert doc is not None
    assert doc['arguments'] == {
        'path': 'admin/lessons' + uri,
        'body': json.dumps(expected_data),
        'method': 'POST',
        'response': expected_data
    }


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('code', [401, 404, 405])
def test_status_proxying(areq_request, code):
    @areq_request
    def aresponse(method, url, headers, **kwargs):
        assert headers['X-API-Key'] == settings.DRIVER_LESSONS_API_KEY
        return areq_request.response(code)

    response = django_test.Client().get('/api/driver_lessons/')
    assert aresponse.call
    assert response.status_code == code
