# pylint: disable=redefined-outer-name
# pylint: disable=inconsistent-return-statements,unused-variable
import urllib.parse
import uuid

import bson
import pytest

from taxi import discovery

from taxi_sm_monitor import stq_task


TEST_CHAT = {
    '_id': {bson.ObjectId('5b436ca8779fb3302cc784ba')},
    'chatterbox_id': 'chatterbox_id',
    'csat_reasons': ['fast answer', 'thank you'],
    'csat_value': 'good',
    'incident_timestamp': {'$date': 1531217390000},
    'last_message_from_user': False,
    'messages': [
        {
            'author': 'user',
            'author_id': 'some_user_id',
            'id': 'message_11',
            'message': 'text_1',
            'timestamp': {'$date': 1530410630000},
        },
        {
            'author': 'support',
            'id': 'message_12',
            'message': 'text_2',
            'timestamp': {'$date': 1530680810000},
        },
        {
            'author': 'support',
            'id': 'message_13',
            'message': 'text_3',
            'metadata': {'is_echo': True},
            'timestamp': {'$date': 1530680810000},
        },
    ],
    'new_messages': 2,
    'open': True,
    'owner_id': '5b4f5059779fb332fcc26152',
    'page': '1960892827353514',
    'support_avatar_url': 4,
    'support_name': 'Иван',
    'type': 'facebook_support',
    'updated': {'$date': 1531311350000},
    'visible': True,
}


@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.parametrize(
    'chat_id, message_id, own_message',
    [
        (bson.ObjectId('5b436ca8779fb3302cc784ba'), 'message_12', False),
        (bson.ObjectId('5b436ca8779fb3302cc784ba'), 'message_11', False),
        (bson.ObjectId('5b436ca8779fb3302cc784ba'), 'message_13', True),
    ],
)
async def test_facebook_send_message(
        taxi_sm_monitor_app_stq,
        chat_id,
        message_id,
        own_message,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    class FakeLogger:
        messages = []

        def info(self, msg, *args, **kwargs):
            self.messages.append(msg % args)

        def warning(self, msg, *args, **kwargs):
            self.messages.append(msg % args)

    monkeypatch.setattr(stq_task, 'logger', FakeLogger())

    chat = TEST_CHAT

    @patch_aiohttp_session('https://graph.facebook.com/', 'POST')
    def facebook_api(method, url, **kwargs):
        assert method == 'post'
        assert url == 'https://graph.facebook.com/v6.0/me/messages'
        request_data = kwargs['json']
        for message in chat['messages']:
            if message['id'] == message_id:
                message_text = message['message']
        assert request_data == {
            'recipient': {'id': chat['owner_id']},
            'message': {'text': message_text, 'metadata': 'own_message'},
        }
        secdist = taxi_sm_monitor_app_stq.secdist
        tokens = secdist['settings_override']['FACEBOOK_PAGE_TOKENS']
        token = tokens[chat['page']]
        assert kwargs['params'] == {'access_token': token}
        return response_mock(json={'message_id': uuid.uuid4().hex})

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def support_chat_api(method, url, **kwargs):
        assert method == 'post'
        assert url.startswith(
            'http://support-chat.taxi.dev.yandex.net/v1/chat',
        )
        parsed_url = urllib.parse.urlparse(url)
        parsed_path = parsed_url.path.split('/')
        chat_id = parsed_path[2]
        assert chat_id == str(chat_id)
        request_data = kwargs['json']
        assert request_data == {
            'include_metadata': True,
            'include_participants': True,
        }

        data = {
            'messages': [],
            'metadata': {'page': chat.get('page', '')},
            'participants': [
                {'id': 'support', 'role': 'support'},
                {'id': chat['owner_id'], 'role': 'facebook_user'},
            ],
        }

        for message in chat['messages']:
            data['messages'].append(
                {
                    'id': message['id'],
                    'text': message['message'],
                    'metadata': message.get('metadata', {}),
                },
            )

        return response_mock(json=data)

    assert await taxi_sm_monitor_app_stq.db.smmonitor_locks.count() == 0
    await stq_task.facebook_task(taxi_sm_monitor_app_stq, chat_id, message_id)
    if own_message:
        log_message = 'Message %s is echo from fb, do not sending it to fb' % (
            message_id
        )
        assert stq_task.logger.messages[-1] == log_message
        return
    lock = await taxi_sm_monitor_app_stq.db.smmonitor_locks.find_one(
        {'_id': message_id},
    )
    assert lock
    await stq_task.facebook_task(taxi_sm_monitor_app_stq, chat_id, message_id)
    log_message = 'User already notify about %s message in chat %s' % (
        message_id,
        chat_id,
    )
    assert stq_task.logger.messages[-1] == log_message
