import aiohttp
import pytest
import json

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from cargo_sf_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.

OAUTH_RESPONSE = {
    'access_token': 'token_from_sf',
    'instance_url': (
        'https://yandexdelivery--testing.sandbox.my.salesforce.com'
    ),
    'id': (
        'https://test.salesforce.com/id/00D1j0000008hfNEAQ/00509000009P3YoAAK'
    ),
    'token_type': 'Bearer',
    'issued_at': '1643151066030',
    'signature': 'XXXXXXXXX',
}


@pytest.fixture(autouse=True)
def _mock_auth(mockserver):
    @mockserver.json_handler('external_salesforce/services/oauth2/token')
    def mock(request):
        return mockserver.make_response(status=200, json=OAUTH_RESPONSE)

    return mock


@pytest.fixture(autouse=True)
def _mock_lead(mockserver):
    @mockserver.json_handler(
        '/salesforce-cargo/services/data/v53.0/sobjects/Lead/',
    )
    def _handler(request):
        body = {'id': '00Q1j000005ci7CEAQ', 'success': True, 'errors': []}
        return mockserver.make_response(status=201, json=body)
