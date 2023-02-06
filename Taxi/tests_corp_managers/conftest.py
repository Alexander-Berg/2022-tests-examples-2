# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from corp_managers_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_personal(mockserver, load_json):
    @mockserver.json_handler(
        r'/personal/v1/(?P<data_type>\w+)/store', regex=True,
    )
    async def _mock_store(request, data_type):
        requested_value = request.json['value']
        return {'id': requested_value + '_id', 'value': requested_value}
