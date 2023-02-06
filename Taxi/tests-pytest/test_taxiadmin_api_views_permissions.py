# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pytest

from django import test as django_test


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    ADMIN_VIEW_ALLOWED_PERMISSIONS=['view_map'])
def test_get_users_with_permission():
    response = django_test.Client().get(
        '/api/permissions/get_users/?permission=view_map')

    assert json.loads(response.content) == [
        'test_login_1', 'test_login_2'
    ]
