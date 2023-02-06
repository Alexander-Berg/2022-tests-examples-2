# pylint: disable=wildcard-import,unused-wildcard-import,redefined-outer-name
# pylint: disable=inconsistent-return-statements,unused-variable
import pytest

import cars_catalog.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['cars_catalog.generated.service.pytest_plugins']


@pytest.fixture
def patch_misspells_get(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session('http://misspell-host', 'GET')
    def patch_misspells(method, url, **kwargs):
        text = kwargs['params']['text']
        if text == 'брюнза':
            text = 'бронза'
        return response_mock(json={'text': text, 'r': 101, 'code': 200})
