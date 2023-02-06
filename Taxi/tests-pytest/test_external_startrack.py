# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from taxi.external import startrack


@pytest.mark.parametrize(
    'profile, kwargs, expected_method, expected_url, expected_kwargs',
    [
        (
            None,
            {
                'path': 'some_path',
            },
            'GET',
            'https://st-api.test.yandex-team.ru/v2/some_path',
            {
                'data': None,
                'params': None,
                'headers': {
                    'Authorization': 'OAuth None',
                },
                'timeout': 5,
                'verify': False,
                'log_extra': None,
            },
        ),
        (
            None,
            {
                'path': 'some_path',
                'method': 'POST',
                'data': {'some': 'data'},
                'params': {'some': 'params'},
                'content_type': 'application/json',
            },
            'POST',
            'https://st-api.test.yandex-team.ru/v2/some_path',
            {
                'data': {'some': 'data'},
                'params': {'some': 'params'},
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': 'OAuth None',
                },
                'timeout': 5,
                'verify': False,
                'log_extra': None,
            },
        ),
        (
            'support-taxi-admin',
            {
                'path': 'some_path',
                'method': 'POST',
                'data': {'some': 'data'},
                'params': {'some': 'params'},
                'content_type': 'application/json',
            },
            'POST',
            'http://test-startrack-url/some_path',
            {
                'data': {'some': 'data'},
                'params': {'some': 'params'},
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': 'OAuth some_startrack_token',
                    'X-Org-Id': '0',
                },
                'timeout': 5,
                'verify': False,
                'log_extra': None,
            },
        ),
    ],
)
@pytest.inline_callbacks
def test_request(mock, areq_request, profile, kwargs, expected_method,
                 expected_url, expected_kwargs):
    @mock
    @areq_request
    def _dummy_request(method, url, **kwargs):
        return 200, b'{}'

    yield startrack._request(profile=profile, **kwargs)

    arequests_call = _dummy_request.calls[0]
    assert arequests_call['args'] == (expected_method, expected_url)
    assert arequests_call['kwargs'] == expected_kwargs
