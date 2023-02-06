# coding: utf-8

from __future__ import unicode_literals

import json

from django import test as django_test
import pytest


@pytest.mark.asyncenv('blocking')
def test_api_currencies():
    response = django_test.Client().get('/api/currencies/')

    assert response.status_code == 200
    got_data = json.loads(response.content)
    assert got_data == {
        'items': [
            {
                'name': 'BYN'
            },
            {
                'name': 'EUR'
            },
            {
                'name': 'RUB'
            },
        ]
    }
