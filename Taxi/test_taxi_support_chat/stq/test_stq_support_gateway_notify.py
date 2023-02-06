# pylint: disable=redefined-outer-name,unused-variable
import bson
import pytest

from taxi import discovery

from taxi_support_chat.stq import stq_task


@pytest.mark.parametrize(
    ('chat_id', 'request_id', 'event', 'expected_request'),
    [
        (
            bson.ObjectId('5b436ece779fb3302cc784bf'),
            '123',
            'new_message',
            {
                'method': 'notify',
                'params': {
                    'service': 'taxi-support-chat',
                    'chat_id': '5b436ece779fb3302cc784bf',
                    'chat_type': 'client_support',
                    'updated': 1530884690000,
                    'user_id': '5b4f5092779fb332fcc26153',
                    'event': 'new_message',
                    'request_id': '123',
                },
            },
        ),
    ],
)
async def test_task(
        patch_aiohttp_session,
        monkeypatch,
        response_mock,
        stq3_context,
        chat_id,
        request_id,
        event,
        expected_request,
):
    support_gateway_service = discovery.find_service('support_gateway')

    @patch_aiohttp_session(support_gateway_service.url)
    def mock_support_gateway(method, url, **kwargs):
        assert url == support_gateway_service.url + '/api/service'
        data = kwargs['json']
        assert data == expected_request
        return response_mock(status=200)

    await stq_task.support_gateway_notify_task(
        stq3_context, chat_id, request_id, event,
    )

    assert mock_support_gateway.calls
