# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

from taxi import discovery

import billing_payment_adapter.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['billing_payment_adapter.generated.service.pytest_plugins']


@pytest.fixture
def mock_archive_api(patch_aiohttp_session, response_mock, load_json):
    host_url = discovery.find_service('archive_api').url

    @patch_aiohttp_session(host_url, 'POST')
    def _mock_api(method, url, **kwargs):
        assert url == host_url + '/v1/yt/select_rows'
        return response_mock(json=load_json('archive_response.json'))
