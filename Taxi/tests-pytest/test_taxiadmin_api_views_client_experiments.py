# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import test as django_test
import pytest

from taxi.conf import settings


@pytest.mark.asyncenv('blocking')
def test_request_to_exp(areq_request):
    expected_data = {'test_key': 'test_value'}

    @areq_request
    def aresponse(method, url, **kwargs):
        assert url.startswith(settings.TAXI_EXP_URL + '/v1/experiments/')
        if 'filters' in url or 'name' in kwargs['params']:
            return areq_request.response(200, json.dumps(expected_data))
        else:
            return areq_request.response(
                400, json.dumps(
                    {
                        'details': 'name is required'
                    }
                ),
                headers={'Content-Type': 'application/json'},
            )

    response = django_test.Client().get('/api/client_experiments/filters/')
    assert response.status_code == 200
    assert json.loads(response.content) == expected_data

    response = django_test.Client().get('/api/client_experiments/')
    assert response.status_code == 400
    assert json.loads(response.content)['message'] == 'name is required'

    response = django_test.Client().post(
        '/api/client_experiments/?name=test'
    )
    assert response.status_code == 200
    response = django_test.Client().put(
        '/api/client_experiments/?name=test'
    )
    assert response.status_code == 200
    response = django_test.Client().delete(
        '/api/client_experiments/?name=test'
    )
    assert response.status_code == 200
