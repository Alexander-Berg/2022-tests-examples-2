# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

import internal_b2b_automations.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['internal_b2b_automations.generated.service.pytest_plugins']


@pytest.fixture
def mock_salesforce_auth(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    async def _handler(request):
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': '$mockserver/multi-salesforce',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mocks_chat_change_status(mockserver):
    @mockserver.json_handler('corp-support-chat/v1/chats/change_status')
    async def change(request):  # pylint: disable=W0612
        if request.json['sf_id'] != '1' or request.json['status'] != 'OnHold':
            return mockserver.make_response(status=500)

        return mockserver.make_response(status=200)
