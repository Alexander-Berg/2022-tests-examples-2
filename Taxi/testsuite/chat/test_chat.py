import json

import pytest


class Chat:
    def __init__(self, client):
        self.client = client

    def create(self, metadata={}, participants=()):
        response = self.client.post(
            '1.0/chat',
            {'metadata': metadata, 'participants': list(participants)},
            headers={'Accept-Language': 'ru'},
        )

        assert response.status_code == 201
        data = response.json()
        return data['id']

    def info(self, chat_id):
        response = self.client.get('1.0/chat/' + chat_id)
        assert response.status_code == 200
        data = response.json()
        return data

    def post_message(
            self, chat_id, newest_id, text, sender, expected_code=201,
    ):
        update = {
            'created_date': '',
            'newest_message_id': newest_id,
            'message': {
                'id': '',
                'metadata': {},
                'sender': sender,
                'text': text,
            },
        }
        response = self.client.post(
            '1.0/chat/' + chat_id + '/add_update', update,
        )
        assert response.status_code == expected_code
        if expected_code != 201:
            return
        return response.json()['message_id']

    def admin_history(
            self,
            chat_id,
            on_behalf_of=None,
            range={},
            include_metadata=True,
            include_participatns=True,
    ):
        request = {
            'include_metadata': include_metadata,
            'include_participants': include_participatns,
        }
        if on_behalf_of:
            request['on_behalf_of'] = on_behalf_of
        if range.get('from'):
            request['range']['message_ids']['newer_than'] = range['from']
        if range.get('to'):
            request['range']['message_ids']['older_than'] = range['from']
        response = self.client.post(
            'admin/1.0/chat/' + chat_id + '/history', request,
        )
        assert response.status_code == 200
        data = response.json()
        return data

    def history(
            self,
            chat_id,
            on_behalf_of=None,
            range={},
            include_metadata=True,
            include_participatns=True,
    ):
        request = {
            'include_metadata': include_metadata,
            'include_participants': include_participatns,
        }

        if 'from' in range or 'to' in range:
            request['range'] = {'message_ids': {}}

        if on_behalf_of:
            request['on_behalf_of'] = on_behalf_of
        if range.get('from'):
            request['range']['message_ids']['newer_than'] = range['from']
        if range.get('to'):
            request['range']['message_ids']['older_than'] = range['to']
        response = self.client.post(
            '1.0/chat/' + chat_id + '/history', request,
        )
        assert response.status_code == 200
        data = response.json()
        return data

    def add_participant(
            self, chat_id, newest_id, participant, sender, text=None,
    ):
        request = {
            'created_date': '',
            'newest_message_id': newest_id,
            'update_participants': {
                'action': 'add',
                'id': participant['id'],
                'role': participant['role'],
                'nickname': '{}s nickname'.format(participant['id']),
            },
        }
        if text:
            request['message'] = {'id': '', 'text': text, 'sender': sender}
        response = self.client.post(
            '1.0/chat/' + chat_id + '/add_update', request,
        )
        assert response.status_code == 201
        data = response.json()
        return data['message_id']

    def remove_participant(
            self, chat_id, newest_id, participant, sender, text=None,
    ):
        request = {
            'created_date': '',
            'newest_message_id': newest_id,
            'update_participants': self.make_participant_update(
                participant, 'remove',
            ),
        }
        if text:
            request['message'] = {'id': '', 'text': text, 'sender': sender}
        response = self.client.post(
            '1.0/chat/' + chat_id + '/add_update', request,
        )
        assert response.status_code == 201
        data = response.json()
        return data['message_id']

    def make_participant_update(self, participant, action='add'):
        return {
            'action': action,
            'id': participant['id'],
            'role': participant['role'],
            'nickname': '{}s nickname'.format(participant['id']),
        }


@pytest.fixture()
def chat(taxi_chat, mockserver):

    chat_ = Chat(taxi_chat)
    return chat_


def test_create_get(taxi_chat, load_json, mockserver, now, yt_client):

    response = taxi_chat.get('1.0/chat/somechatid')
    assert response.status_code == 404

    def add_message(text, newest_id, sender_id='system', sender_role='system'):
        update = {
            'created_date': '',
            'newest_message_id': newest_id,
            'message': {
                'id': 'msg_1',
                'metadata': {},
                'sender': {'id': sender_id, 'role': sender_role},
                'text': text,
            },
        }
        response = taxi_chat.post(
            '1.0/chat/' + chat_id + '/add_update', update,
        )
        assert response.status_code == 201
        return response.json()['message_id']

    def get_history(
            chat_id,
            newer_than=None,
            older_than=None,
            on_behalf_of={'id': 'system', 'role': 'system'},
    ):
        response = taxi_chat.post(
            '1.0/chat/' + chat_id + '/history',
            {
                'include_metadata': True,
                'include_participants': True,
                'on_behalf_of': {
                    'id': on_behalf_of['id'],
                    'role': on_behalf_of['role'],
                },
                'range': {
                    'message_ids': {
                        'newer_than': newer_than or '',
                        'older_than': older_than or '',
                    },
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        return data

    rdata = {
        'metadata': {'key': 'value', 'key2': ['a', 'b']},
        'participants': [
            {
                'action': 'add',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'role': 'client',
            },
        ],
    }
    response = taxi_chat.post(
        '1.0/chat', rdata, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    response = taxi_chat.get('1.0/chat/' + chat_id)
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == chat_id
    newest_message_id = data['newest_message_id']

    update = {
        'created_date': '1',
        'newest_message_id': newest_message_id,
        'message': {
            'id': 'msg_1',
            'metadata': {},
            'sender': {'id': 'user_id_1', 'role': 'client'},
            'text': 'message text',
            'location': [1, 1],
        },
        'update_metadata': {'new': 'meta'},
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201
    data = response.json()
    newest_message_id = data['message_id']

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {'include_metadata': True, 'include_participants': True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 3
    assert data['metadata'] == {'new': 'meta'}
    assert data['newest_message_id'] == newest_message_id
    assert sorted(data['participants'], key=lambda k: k['id']) == [
        {'id': 'system', 'role': 'system', 'active': True},
        {
            'id': 'user_id_1',
            'nickname': 'U5eR1',
            'role': 'client',
            'active': True,
        },
    ]
    assert data['updates'][0]['message']['text'] == 'message text'
    assert data['updates'][0]['message']['location'] == [1, 1]

    add_message('hello!', newest_message_id)
    data = get_history(chat_id, newest_message_id)
    assert data['total'] == 4
    assert len(data['updates']) == 1


def test_callbacks(taxi_chat, mockserver):
    rdata = {
        'metadata': {'order_locale': 'ru'},
        'participants': [
            {
                'action': 'add',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'role': 'client',
                'subscription': {
                    'callback_url': mockserver.url('callback_url'),
                    'fields': ['newest_message_id', 'text'],
                },
            },
            {
                'action': 'add',
                'id': 'driver_id_1',
                'nickname': 'v0di1a',
                'role': 'driver',
                'subscription': {
                    'callback_url': mockserver.url('callback_url2'),
                },
            },
        ],
    }
    response = taxi_chat.post(
        '1.0/chat', rdata, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    @mockserver.json_handler('/callback_url')
    def mock_callback(request):
        data = json.loads(request.get_data())
        assert request.headers['Accept-Language'] == 'ru'
        assert 'newest_message_id' in data
        assert data['text'] == 'hi'
        return {}

    @mockserver.json_handler('/callback_url2')
    def mock_callback2(request):
        data = json.loads(request.get_data())
        assert request.headers['Accept-Language'] == 'ru'
        assert 'newest_message_id' in data
        assert 'updated_date' in data
        assert 'chat_id' in data
        return {}

    update = {
        'created_date': '',
        'newest_message_id': '3',
        'message': {
            'id': 'msg_1',
            'metadata': {},
            'sender': {'id': 'system', 'role': 'system'},
            'text': 'hi',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    mock_callback.wait_call()
    mock_callback2.wait_call()


@pytest.mark.now('2017-11-03T17:14:00+0300')
def test_hide_history(chat):
    client = {'id': 'user_id', 'role': 'client'}
    system = {'id': 'system', 'role': 'system'}
    driver = {'id': 'driver_id', 'role': 'driver'}
    participants = chat.make_participant_update(client)
    chat_id = chat.create(
        metadata={'comment': 'order comment'}, participants=[participants],
    )

    info = chat.info(chat_id)
    assert info['id'] == chat_id

    expected_data = {
        'metadata': {
            'comment': 'order comment',
            'created_date': '2017-11-03T14:14:00.000000Z',
        },
        'newest_message_id': '2',
        'participants': [
            {'active': True, 'id': 'system', 'role': 'system'},
            {
                'active': True,
                'id': 'user_id',
                'nickname': 'user_ids nickname',
                'role': 'client',
            },
        ],
        'total': 2,
        'updates': [
            {
                'newest_message_id': '1',
                'message': {
                    'sender': {'role': 'system', 'id': 'system'},
                    'id': '2',
                    'metadata': {},
                },
                'update_participants': {
                    'action': 'add',
                    'role': 'client',
                    'nickname': 'user_ids nickname',
                    'id': 'user_id',
                },
                'created_date': '2017-11-03T14:14:00.000000Z',
            },
            {
                'newest_message_id': '0',
                'message': {
                    'sender': {'role': 'system', 'id': 'system'},
                    'id': '1',
                    'metadata': {},
                },
                'update_participants': {
                    'action': 'add',
                    'role': 'system',
                    'id': 'system',
                },
                'update_metadata': {
                    'comment': 'order comment',
                    'created_date': '2017-11-03T14:14:00.000000Z',
                },
                'created_date': '2017-11-03T14:14:00.000000Z',
            },
        ],
    }
    data = chat.history(chat_id)
    assert data == expected_data
    admin_data = chat.admin_history(chat_id)
    assert admin_data == expected_data

    chat.post_message(
        chat_id, info['newest_message_id'], 'first', sender=client,
    )

    data = chat.history(chat_id, on_behalf_of=client)
    assert data['total'] == 3
    assert len(data['updates']) == 2
    assert data['updates'][0]['message']['text'] == 'first'

    chat.add_participant(
        chat_id,
        data['newest_message_id'],
        participant=driver,
        text='driver assigned',
        sender=system,
    )
    data = chat.history(chat_id, on_behalf_of=driver)
    # first message must be order comment
    assert data['total'] == 4
    assert len(data['updates']) == 1
    assert data['updates'][0]['update_participants']['action'] == 'add'


@pytest.mark.now('2017-11-03T17:14:00+0300')
@pytest.mark.config(CLIENTDRIVER_CHAT_SHOULD_IGNORE_WRONG_HISTORY_RANGE=True)
def test_chat_history_fixed_wrong_range(chat):
    client = {'id': 'user_id', 'role': 'client'}
    participants = chat.make_participant_update(client)
    chat_id = chat.create(
        metadata={'comment': 'order comment'}, participants=[participants],
    )

    info = chat.info(chat_id)
    assert info['id'] == chat_id

    expected_data = {
        'metadata': {
            'comment': 'order comment',
            'created_date': '2017-11-03T14:14:00.000000Z',
        },
        'newest_message_id': '2',
        'participants': [
            {'active': True, 'id': 'system', 'role': 'system'},
            {
                'active': True,
                'id': 'user_id',
                'nickname': 'user_ids nickname',
                'role': 'client',
            },
        ],
        'total': 2,
        'updates': [
            {
                'newest_message_id': '1',
                'message': {
                    'sender': {'role': 'system', 'id': 'system'},
                    'id': '2',
                    'metadata': {},
                },
                'update_participants': {
                    'action': 'add',
                    'role': 'client',
                    'nickname': 'user_ids nickname',
                    'id': 'user_id',
                },
                'created_date': '2017-11-03T14:14:00.000000Z',
            },
            {
                'newest_message_id': '0',
                'message': {
                    'sender': {'role': 'system', 'id': 'system'},
                    'id': '1',
                    'metadata': {},
                },
                'update_participants': {
                    'action': 'add',
                    'role': 'system',
                    'id': 'system',
                },
                'update_metadata': {
                    'comment': 'order comment',
                    'created_date': '2017-11-03T14:14:00.000000Z',
                },
                'created_date': '2017-11-03T14:14:00.000000Z',
            },
        ],
    }
    data = chat.history(
        chat_id,
        range={
            'from': '0c75bcdaca7e8d97966db95ca80ae4a7',
            'to': '0c75bcdaca7e8d97966db95ca80ae4a7',
        },
    )
    assert data == expected_data
    admin_data = chat.admin_history(chat_id)
    assert admin_data == expected_data


def test_join_after_many_messages(chat):
    client = {'id': 'user_id', 'role': 'client'}
    driver = {'id': 'driver_id', 'role': 'driver'}
    system = {'id': 'system', 'role': 'system'}
    participants = chat.make_participant_update(client)
    chat_id = chat.create(participants=[participants])

    info = chat.info(chat_id)
    newest_id = info['newest_message_id']

    for i in range(50):
        newest_id = chat.post_message(
            chat_id, newest_id, 'message %d' % i, sender=client,
        )

    # add driver
    chat.add_participant(
        chat_id,
        newest_id,
        participant=driver,
        text='driver assigned',
        sender=system,
    )
    data = chat.history(chat_id, on_behalf_of=driver)
    assert data['total'] == 53
    assert len(data['updates']) == 1
    assert data['updates'][0]['message']['text'] == 'driver assigned'


def test_join_after_remove_messages(chat):
    client = {'id': 'user_id', 'role': 'client'}
    driver = {'id': 'driver_id', 'role': 'driver'}
    system = {'id': 'system', 'role': 'system'}
    participants = chat.make_participant_update(client)
    chat_id = chat.create(participants=[participants])

    info = chat.info(chat_id)
    newest_id = info['newest_message_id']

    newest_id = chat.add_participant(
        chat_id, newest_id, participant=driver, sender=system,
    )
    for i in range(50):
        newest_id = chat.post_message(
            chat_id, newest_id, 'message %d' % i, sender=client,
        )

    newest_id = chat.remove_participant(chat_id, newest_id, driver, system)
    newest_id = chat.post_message(
        chat_id, newest_id, 'hidden message', sender=client,
    )
    newest_id = chat.add_participant(
        chat_id, newest_id, driver, system, 'driver rejoined',
    )

    data = chat.history(chat_id, on_behalf_of=driver)
    assert data['total'] == 56
    assert len(data['updates']) == 1
    assert data['updates'][0]['message']['text'] == 'driver rejoined'


@pytest.mark.config(CLIENTDRIVER_CHAT_BANNED_WORDS={'words': ['ban']})
def test_banned_words(chat):
    client = {'id': 'user_id', 'role': 'client'}
    participants = chat.make_participant_update(client)
    chat_id = chat.create(participants=[participants])

    info = chat.info(chat_id)
    newest_id = info['newest_message_id']

    newest_id = chat.post_message(
        chat_id,
        newest_id,
        'Hello, im from england',
        sender=client,
        expected_code=201,
    )

    newest_id = chat.post_message(
        chat_id,
        newest_id,
        'this message is banned',
        sender=client,
        expected_code=400,
    )
