# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest

from eats_restapp_support_chat_plugins.generated_tests import *


@pytest.fixture
def _mock_support_chat(mockserver, load_json):
    data = load_json('support_chat_search_response.json')
    chats_by_id = {chat['id']: chat for chat in data['chats']}

    @mockserver.json_handler(
        r'/support-chat/v1/chat/(?P<chat_id>[0-9a-f]+)', regex=True,
    )
    def _mock(request, chat_id):
        return chats_by_id[chat_id]

    return _mock


@pytest.mark.parametrize(
    'partner_id,params,expected_status,expected_response',
    [
        (1, {}, 200, {'role': 'ROLE_MANAGER'}),
        (2, {}, 200, {'role': 'ROLE_OPERATOR'}),
        (1, {'chat_id': '01'}, 200, {'role': 'ROLE_MANAGER'}),
        (
            1,
            {'chat_id': '03'},
            403,
            {
                'code': 'NO_ACCESS',
                'message': 'partner 1 has no access to chat 03',
            },
        ),
        (1, {'place_id': '111'}, 200, {'role': 'ROLE_MANAGER'}),
        (
            1,
            {'place_id': '333'},
            403,
            {
                'code': 'NO_ACCESS',
                'message': 'partner 1 has no access to place 333',
            },
        ),
        (3, {'chat_id': '04'}, 200, {'role': 'ROLE_OPERATOR'}),
        (
            1,
            {'chat_id': '04'},
            403,
            {
                'code': 'NO_ACCESS',
                'message': 'partner 1 has no access to chat 04',
            },
        ),
    ],
)
async def test_partner_check_access(
        _mock_support_chat,
        taxi_eats_restapp_support_chat,
        partner_id,
        params,
        expected_status,
        expected_response,
):
    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/restapp-front/support_chat/v1/partner/check_access/',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params=params,
    )
    assert response.status == expected_status
    assert response.json() == expected_response
