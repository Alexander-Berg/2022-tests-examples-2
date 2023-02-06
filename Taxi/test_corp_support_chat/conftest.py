# pylint: disable=redefined-outer-name
import pytest

import corp_support_chat.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_support_chat.generated.service.pytest_plugins']


@pytest.fixture
def mock_sf_data_load(mockserver):
    @mockserver.json_handler(
        'sf-data-load/v1/corp_support_chat/b2b/update_status',
    )
    async def _handler(request):
        return mockserver.make_response(status=200)
