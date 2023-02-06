import pytest

from taxi import discovery


@pytest.mark.parametrize(
    'user_role', ['support', 'client', 'eats_client', 'driver', 'sms_client'],
)
async def test_first_message(
        cbox, patch_aiohttp_session, response_mock, user_role,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def _dummy_support_chat_request(method, url, **kwargs):
        if url.endswith('/history'):
            return response_mock(
                json={
                    'messages': [
                        {
                            'sender': {'id': 'some_login', 'role': 'support'},
                            'text': 'some support text',
                            'metadata': {'created': '2018-05-05T15:34:57'},
                        },
                        {
                            'sender': {'id': 'some_login', 'role': user_role},
                            'text': 'some user message',
                            'metadata': {'created': '2018-05-05T15:34:56'},
                        },
                    ],
                },
            )

        return response_mock(json={})

    task = {
        '_id': 'task_id_1',
        'line': 'first',
        'tags': [],
        'type': 'chat',
        'external_id': 'external',
    }
    message = await cbox.app.task_source_manager.first_client_message(task)
    if user_role == 'support':
        assert not message
    else:
        assert message == 'some user message'
