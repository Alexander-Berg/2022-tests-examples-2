import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from price_estimate_api_plugins import *  # noqa: F403 F401


@pytest.fixture()
def uapi_keys_auth(mockserver):
    @mockserver.json_handler('/uapi-keys/v2/authorization')
    def _mock_auth(request):
        if request.headers['X-API-Key'] == 'badkey':
            return mockserver.make_response('{"code":"","message":""}', 403)
        return {'key_id': 'some_id'}

    return _mock_auth
