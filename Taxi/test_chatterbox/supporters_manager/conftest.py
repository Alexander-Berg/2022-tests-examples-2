import pytest

from taxi import settings
from taxi.clients import compendium


@pytest.fixture
def patch_compendium_get_info(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200):

        compendium_url = settings.Settings.COMPENDIUM_URL
        get_supporters_info_url = compendium_url + '/api/v2/get_users_info'

        @patch_aiohttp_session(get_supporters_info_url, 'POST')
        def get_supporters_info(method, url, headers, **kwargs):
            assert headers[compendium.API_KEY_HEADER] == 'COMPENDIUM_KEY'
            result = {} if response is None else response
            return response_mock(json=result, status=status)

        return get_supporters_info

    return wrapper


@pytest.fixture
def patch_agent_get_info(mockserver, response_mock):
    def wrapper(response=None, status=200):
        @mockserver.json_handler('/agent/get_support_settings')
        def _dummy_agent(request):
            result = {} if response is None else response
            return mockserver.make_response(json=result, status=status)

        return _dummy_agent

    return wrapper
