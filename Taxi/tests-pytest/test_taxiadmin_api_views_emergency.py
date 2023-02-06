# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import pytest

from django import test as django_test

from taxi import config


@pytest.mark.parametrize('code, value, expected', [
    (
        200,
        {'ignore_emergency': True, 'is_emergency': False},
        {'is_emergency': False},
    ),
    (
        200,
        {'ignore_emergency': True, 'is_emergency': True},
        {'is_emergency': False},
    ),
    (
        200,
        {'ignore_emergency': False, 'is_emergency': True},
        {'is_emergency': True},
    ),
    (
        200,
        {'ignore_emergency': False, 'is_emergency': False},
        {'is_emergency': False},
    ),

])
@pytest.mark.asyncenv('blocking')
def test_get_emergency_mode(code, value, expected):
    url = '/api/get_emergency_mode/'

    config.ADMIN_EMERGENCY_MODE.save(value)
    response = django_test.Client().get(url)
    result = json.loads(response.content)
    assert response.status_code == code
    assert result == expected


@pytest.mark.parametrize('code, data, expected', [
    (
        200,
        {'is_emergency': True},
        {'message': None}
    ),
    (
        200,
        {'is_emergency': True, 'ignore_emergency': False},
        {'message': None}
    ),
    (
        400,
        {},
        {'status': 'error', 'code': 'general', 'message': None}
    ),
    (
        400,
        {'something_else': True},
        {'status': 'error', 'code': 'general', 'message': None}
    ),
])
@pytest.mark.asyncenv('blocking')
def test_set_emergency_mode(code, data, expected):
    response = django_test.Client().post('/api/set_emergency_mode/',
                                         json.dumps(data),
                                         'application/json')

    result = json.loads(response.content)
    result['message'] = None
    assert response.status_code == code
    assert result == expected
