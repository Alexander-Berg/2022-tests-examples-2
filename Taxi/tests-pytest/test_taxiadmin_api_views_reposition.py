from __future__ import unicode_literals

import json

from django import test as django_test
import pytest

from taxi.core import async


REPOSITION_HOST = 'http://reposition.taxi.yandex.net/'
API_REPOSITION = '/api/reposition'


@pytest.mark.parametrize(
    'method, url, data, expected_code, expected_request, expected_response', [
    ('get', '/settings/modes', None,
        200, 'v1/settings/modes', (200, 'ok message')),
    ('put', '/settings/modes', {'mode': 'new_mode'},
        200, 'v1/settings/modes', (200, 'ok message')),
    ('get', '/drivers/locations?driver_id=a&park_db_id=b', None,
        200, 'v1/drivers/locations', (200, 'ok message')),
    ('get', '/v2/settings/deviation_formulae', None,
        200, 'v2/settings/deviation_formulae', (200, 'ok message')),
    ('put', '/v2/settings/deviation_formulae', {'mode': 'new_mode'},
        200, 'v2/settings/deviation_formulae', (200, 'ok message'))
])
@pytest.mark.asyncenv('blocking')
def test_handle_api_reposition(
        patch,
        method,
        url,
        data,
        expected_request,
        expected_code,
        expected_response):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def _request(*args, **kwargs):
        assert args[0] == method.upper()
        assert args[1] == REPOSITION_HOST + expected_request
        async.return_value(expected_response)

    args = [API_REPOSITION + url]
    if data is not None:
        args.append(json.dumps(data))
        args.append('application/json')

    request_method = getattr(django_test.Client(), method)
    http_response = request_method(*args)
    assert http_response.status_code == expected_code
