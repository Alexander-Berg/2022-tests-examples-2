import json
import time

import pytest


@pytest.mark.config(CRUTCH=True, CLIENTDRIVER_CHAT_TRANSLATION_ENABLED=True)
@pytest.mark.now('2018-05-15T17:07:57.000000Z')
def test_with_comment_ctl(taxi_chat, mockserver):
    rdata = {
        'metadata': {'order_locale': 'ru'},
        'participants': [
            {
                'action': 'add',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'role': 'client',
            },
            {'action': 'add', 'id': 'driver_id', 'role': 'driver'},
        ],
    }
    response = taxi_chat.post(
        '1.0/chat', rdata, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'hint': 'de,en,ru,ro'}
        return {'code': 200, 'lang': 'de'}

    # post ctl message
    update = {
        'created_date': '',
        'newest_message_id': '3',
        'message': {
            'id': 'msg_1',
            'metadata': {
                'language_hint': {
                    'keyboard_languages': ['de', 'en'],
                    'app_language': 'ru',
                    'system_languages': ['en', 'ro'],
                },
            },
            'sender': {'id': 'user_id_1', 'role': 'client'},
            'text': 'translate-en//Hallo!',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    # post message to translate
    update = {
        'created_date': '',
        'newest_message_id': '4',
        'message': {
            'id': 'msg_1',
            'metadata': {
                'language_hint': {
                    'keyboard_languages': ['de', 'en', 'wtf'],
                    'app_language': 'ru',
                    'system_languages': ['en', 'ro'],
                },
            },
            'sender': {'id': 'driver_id', 'role': 'driver'},
            'text': 'Hallo',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'lang': 'de-en'}
        assert request.get_data().decode() == 'text=Hallo'
        return {'code': 200, 'lang': 'de-en', 'text': ['Hello']}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id_1', 'role': 'client'},
        },
    )
    assert response.status_code == 200
    data = response.json()

    updates = data.pop('updates')
    assert data == {
        'total': 5,
        'participants': [
            {'active': True, 'role': 'driver', 'id': 'driver_id'},
            {'active': True, 'role': 'system', 'id': 'system'},
            {
                'active': True,
                'role': 'client',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'metadata': {
                    'translation_settings': {
                        'do_not_translate': [],
                        'to': 'en',
                    },
                },
            },
        ],
        'newest_message_id': '5',
        'all_languages': ['de'],
        'metadata': {
            'order_locale': 'ru',
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
        'can_translate': True,
    }
    assert updates[0:2] == [
        {
            'message': {
                'sender': {'role': 'driver', 'id': 'driver_id'},
                'language': 'de',
                'text': 'Hallo',
                'translations': [{'text': 'Hello', 'language': 'en'}],
                'id': '5',
                'metadata': {
                    'language_hint': {
                        'system_languages': ['en', 'ro'],
                        'keyboard_languages': ['de', 'en', 'wtf'],
                        'app_language': 'ru',
                    },
                },
            },
            'newest_message_id': '4',
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
        {
            'message': {
                'text': 'translate-en//Hallo!',
                'sender': {'role': 'client', 'id': 'user_id_1'},
                'id': '4',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': ['de', 'en'],
                        'app_language': 'ru',
                        'system_languages': ['en', 'ro'],
                    },
                },
            },
            'newest_message_id': '3',
            'update_participants': {
                'action': 'add',
                'role': 'client',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'metadata': {
                    'translation_settings': {
                        'do_not_translate': [],
                        'to': 'en',
                    },
                },
            },
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
    ]

    # test use cached translations
    time.sleep(2)  # just in case, caching is async

    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect_invalid(request):
        return mockserver.make_response('{"code": 500}', 500)

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate_invalid(request):
        return mockserver.make_response('{"code": 500}', 500)

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id_1', 'role': 'client'},
            'range': {'message_ids': {'newer_than': '2'}},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['updates'][0] == {
        'message': {
            'sender': {'role': 'driver', 'id': 'driver_id'},
            'language': 'de',
            'text': 'Hallo',
            'translations': [{'text': 'Hello', 'language': 'en'}],
            'id': '5',
            'metadata': {
                'language_hint': {
                    'system_languages': ['en', 'ro'],
                    'keyboard_languages': ['de', 'en', 'wtf'],
                    'app_language': 'ru',
                },
            },
        },
        'newest_message_id': '4',
        'created_date': '2018-05-15T17:07:57.000000Z',
    }
    time.sleep(2)

    # scenario for messages with different languages
    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect_multiple(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'hint': 'de,en,ru,ro'}
        data = request.get_data()
        if data == b'text=Privet':
            return {'code': 200, 'lang': 'ru'}
        else:
            assert data == b'text=Hallo'
            return {'code': 200, 'lang': 'de'}

    update = {
        'created_date': '',
        'newest_message_id': '5',
        'message': {
            'id': 'msg_1',
            'metadata': {
                'language_hint': {
                    'keyboard_languages': ['de', 'en'],
                    'app_language': 'ru',
                    'system_languages': ['en', 'ro'],
                },
            },
            'sender': {'id': 'driver_id', 'role': 'driver'},
            'text': 'Hallo',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    update = {
        'created_date': '',
        'newest_message_id': '6',
        'message': {
            'id': 'msg_1',
            'metadata': {
                'language_hint': {
                    'keyboard_languages': ['de', 'en'],
                    'app_language': 'ru',
                    'system_languages': ['en', 'ro'],
                },
            },
            'sender': {'id': 'driver_id', 'role': 'driver'},
            'text': 'Privet',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate_multiple(request):
        if request.get_data() == b'text=Privet':
            assert request.args.to_dict() == {'srv': 'taxi', 'lang': 'ru-en'}
            return {'code': 200, 'lang': 'ru-en', 'text': ['Hello']}
        else:
            assert request.get_data() == b'text=Hallo'
            assert request.args.to_dict() == {'srv': 'taxi', 'lang': 'de-en'}
            return {'code': 200, 'lang': 'de-en', 'text': ['Hello']}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id_1', 'role': 'client'},
            'range': {'message_ids': {'newer_than': '5'}},
        },
    )
    assert response.status_code == 200
    data = response.json()

    data.pop('all_languages')
    updates = data.pop('updates')
    assert data == {
        'total': 7,
        'participants': [
            {'active': True, 'role': 'driver', 'id': 'driver_id'},
            {'active': True, 'role': 'system', 'id': 'system'},
            {
                'active': True,
                'role': 'client',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'metadata': {
                    'translation_settings': {
                        'do_not_translate': [],
                        'to': 'en',
                    },
                },
            },
        ],
        'newest_message_id': '7',
        'metadata': {
            'order_locale': 'ru',
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
        'can_translate': True,
    }
    assert updates[0:2] == [
        {
            'message': {
                'sender': {'role': 'driver', 'id': 'driver_id'},
                'language': 'ru',
                'text': 'Privet',
                'translations': [{'text': 'Hello', 'language': 'en'}],
                'id': '7',
                'metadata': {
                    'language_hint': {
                        'system_languages': ['en', 'ro'],
                        'keyboard_languages': ['de', 'en'],
                        'app_language': 'ru',
                    },
                },
            },
            'newest_message_id': '6',
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
        {
            'message': {
                'sender': {'role': 'driver', 'id': 'driver_id'},
                'language': 'de',
                'text': 'Hallo',
                'translations': [{'text': 'Hello', 'language': 'en'}],
                'id': '6',
                'metadata': {
                    'language_hint': {
                        'system_languages': ['en', 'ro'],
                        'keyboard_languages': ['de', 'en'],
                        'app_language': 'ru',
                    },
                },
            },
            'newest_message_id': '5',
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
    ]


@pytest.mark.config(CRUTCH=True, CLIENTDRIVER_CHAT_TRANSLATION_ENABLED=True)
@pytest.mark.now('2018-05-15T17:07:57.000000Z')
def test_error_response(taxi_chat, mockserver):
    rdata = {
        'metadata': {'order_locale': 'ru'},
        'participants': [
            {
                'action': 'add',
                'id': 'user_id_1',
                'nickname': 'U5eR1',
                'role': 'client',
                'metadata': {
                    'translation_settings': {
                        'do_not_translate': [],
                        'to': 'en',
                    },
                },
            },
            {'action': 'add', 'id': 'driver_id', 'role': 'driver'},
        ],
    }
    response = taxi_chat.post(
        '1.0/chat', rdata, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect_invalid(request):
        return mockserver.make_response('{"code": 500}', 500)

    update = {
        'created_date': '',
        'newest_message_id': '3',
        'message': {
            'id': 'msg_1',
            'metadata': {
                'language_hint': {
                    'keyboard_languages': ['de', 'en', 'wtf'],
                    'app_language': 'ru',
                    'system_languages': ['en', 'ro'],
                },
            },
            'sender': {'id': 'driver_id', 'role': 'driver'},
            'text': 'Hallo',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate_fail(request):
        return mockserver.make_response('{"code": 500}', 500)

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id_1', 'role': 'client'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    updates = data.pop('updates')
    assert data == {
        'all_languages': [],
        'can_translate': True,
        'newest_message_id': '4',
        'participants': [
            {'active': True, 'role': 'driver', 'id': 'driver_id'},
            {'active': True, 'role': 'system', 'id': 'system'},
            {
                'active': True,
                'role': 'client',
                'nickname': 'U5eR1',
                'id': 'user_id_1',
                'metadata': {
                    'translation_settings': {
                        'to': 'en',
                        'do_not_translate': [],
                    },
                },
            },
        ],
        'total': 4,
        'metadata': {
            'order_locale': 'ru',
            'created_date': '2018-05-15T17:07:57.000000Z',
        },
    }

    assert updates[0] == {
        'message': {
            'text': 'Hallo',
            'sender': {'role': 'driver', 'id': 'driver_id'},
            'id': '4',
            'metadata': {
                'language_hint': {
                    'system_languages': ['en', 'ro'],
                    'keyboard_languages': ['de', 'en', 'wtf'],
                    'app_language': 'ru',
                },
            },
        },
        'newest_message_id': '3',
        'created_date': '2018-05-15T17:07:57.000000Z',
    }

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate_bad_response(request):
        return mockserver.make_response('waddafuk')

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id_1', 'role': 'client'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['updates'][0] == updates[0]


@pytest.mark.config(CRUTCH=True, CLIENTDRIVER_CHAT_TRANSLATION_ENABLED=True)
@pytest.mark.now('2018-05-15T17:07:57.000000Z')
def test_dont_translate_same_language(taxi_chat, mockserver):
    response = taxi_chat.post(
        '1.0/chat',
        {
            'metadata': {'order_locale': 'ru'},
            'participants': [
                {
                    'action': 'add',
                    'id': 'user_id',
                    'role': 'client',
                    'metadata': {
                        'translation_settings': {
                            'do_not_translate': [],
                            'to': 'de',
                        },
                    },
                },
                {'action': 'add', 'id': 'driver_id', 'role': 'driver'},
            ],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'hint': 'de,en,ru,ro'}
        return {'code': 200, 'lang': 'de'}

    update = {
        'created_date': '',
        'newest_message_id': '3',
        'message': {
            'id': 'msg_1',
            'metadata': {
                'language_hint': {
                    'keyboard_languages': ['de', 'en', 'wtf'],
                    'app_language': 'ru',
                    'system_languages': ['en', 'ro'],
                },
            },
            'sender': {'id': 'driver_id', 'role': 'driver'},
            'text': 'Hello',
        },
    }
    response = taxi_chat.post('1.0/chat/' + chat_id + '/add_update', update)
    assert response.status_code == 201

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate(request):
        assert False

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id', 'role': 'client'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['updates'][0] == {
        'message': {
            'text': 'Hello',
            'sender': {'role': 'driver', 'id': 'driver_id'},
            'id': '4',
            'metadata': {
                'language_hint': {
                    'system_languages': ['en', 'ro'],
                    'keyboard_languages': ['de', 'en', 'wtf'],
                    'app_language': 'ru',
                },
            },
            'language': 'de',
        },
        'newest_message_id': '3',
        'created_date': '2018-05-15T17:07:57.000000Z',
    }


@pytest.mark.config(CLIENTDRIVER_CHAT_TRANSLATION_ENABLED=True)
@pytest.mark.now('2018-05-15T17:07:57.000000Z')
def test_translate_to_accept_language(taxi_chat, mockserver):
    # 1. create
    response = taxi_chat.post(
        '1.0/chat',
        {
            'metadata': {'order_locale': 'ru'},
            'participants': [
                {
                    'action': 'add',
                    'id': 'user_id',
                    'role': 'client',
                    'metadata': {
                        'translation_settings': {
                            'do_not_translate': [],
                            'to': 'ru-RU, ru;q=0.8,en;q=0.6',
                        },
                    },
                },
                {'action': 'add', 'id': 'driver_id', 'role': 'driver'},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    # 2. post message as driver
    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'hint': 'ru,en'}
        return {'code': 200, 'lang': 'en'}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/add_update',
        {
            'created_date': '',
            'newest_message_id': '3',
            'message': {
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': ['ru', 'en'],
                        'app_language': 'en',
                        'system_languages': ['en'],
                    },
                },
                'sender': {'id': 'driver_id', 'role': 'driver'},
                'text': 'Hello',
            },
        },
    )
    assert response.status_code == 201

    # 3. read message as client
    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'lang': 'en-ru'}
        assert request.get_data() == b'text=Hello'
        return {'code': 200, 'lang': 'en-ru', 'text': ['Привет']}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'user_id', 'role': 'client'},
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    updates = data.pop('updates')
    assert data == {
        'all_languages': ['en'],
        'can_translate': True,
        'metadata': {
            'created_date': '2018-05-15T17:07:57.000000Z',
            'order_locale': 'ru',
        },
        'newest_message_id': '4',
        'participants': [
            {'active': True, 'id': 'driver_id', 'role': 'driver'},
            {'active': True, 'id': 'system', 'role': 'system'},
            {
                'active': True,
                'id': 'user_id',
                'role': 'client',
                'metadata': {
                    'translation_settings': {
                        'do_not_translate': [],
                        'to': 'ru',
                    },
                },
            },
        ],
        'total': 4,
    }
    assert updates[0] == {
        'created_date': '2018-05-15T17:07:57.000000Z',
        'message': {
            'id': '4',
            'language': 'en',
            'metadata': {
                'language_hint': {
                    'app_language': 'en',
                    'keyboard_languages': ['ru', 'en'],
                    'system_languages': ['en'],
                },
            },
            'sender': {'id': 'driver_id', 'role': 'driver'},
            'text': 'Hello',
            'translations': [{'language': 'ru', 'text': 'Привет'}],
        },
        'newest_message_id': '3',
    }

    # test parsing of participant language with add_update handler
    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/add_update',
        {
            'created_date': '',
            'newest_message_id': '4',
            'message': {
                'id': '',
                'sender': {'id': 'system', 'role': 'system'},
            },
            'update_participants': {
                'role': 'driver',
                'action': 'add',
                'id': 'driver_id',
                'metadata': {
                    'translation_settings': {
                        'do_not_translate': [],
                        'to': 'de_DE, language $@',
                    },
                },
            },
        },
    )
    assert response.status_code == 201

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/history',
        {
            'include_metadata': True,
            'include_participants': True,
            'on_behalf_of': {'id': 'driver_id', 'role': 'driver'},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data['participants'] == [
        {
            'active': True,
            'id': 'driver_id',
            'role': 'driver',
            'metadata': {
                'translation_settings': {'do_not_translate': [], 'to': 'de'},
            },
        },
        {'active': True, 'id': 'system', 'role': 'system'},
        {
            'active': True,
            'id': 'user_id',
            'role': 'client',
            'metadata': {
                'translation_settings': {'do_not_translate': [], 'to': 'ru'},
            },
        },
    ]


@pytest.mark.config(CLIENTDRIVER_CHAT_TRANSLATION_ENABLED=True)
@pytest.mark.now('2018-05-15T17:07:57.000000Z')
def test_translate_callbacks(taxi_chat, mockserver):
    # 1. create
    response = taxi_chat.post(
        '1.0/chat',
        {
            'metadata': {'order_locale': 'ru'},
            'participants': [
                {
                    'action': 'add',
                    'id': 'user_id',
                    'role': 'client',
                    'metadata': {
                        'translation_settings': {
                            'do_not_translate': [],
                            'to': 'ru-RU, ru;q=0.8,en;q=0.6',
                        },
                    },
                    'subscription': {
                        'callback_url': mockserver.url('callback_url'),
                        'fields': ['newest_message_id', 'text'],
                    },
                },
                {'action': 'add', 'id': 'driver_id', 'role': 'driver'},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    # 2. post message as driver

    @mockserver.json_handler('/callback_url')
    def mock_callback(request):
        data = json.loads(request.get_data())
        assert request.headers['Accept-Language'] == 'ru'
        assert 'newest_message_id' in data
        assert data['text'] == 'Привет'
        return {}

    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'hint': 'ru,en'}
        assert request.get_data().decode() == 'text=Hello'
        return {'code': 200, 'lang': 'en'}

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'lang': 'en-ru'}
        assert request.get_data().decode() == 'text=Hello'
        return {'code': 200, 'lang': 'en-ru', 'text': ['Привет']}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/add_update',
        {
            'created_date': '',
            'newest_message_id': '3',
            'message': {
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': ['ru', 'en'],
                        'app_language': 'en',
                        'system_languages': ['en'],
                    },
                },
                'sender': {'id': 'driver_id', 'role': 'driver'},
                'text': 'Hello',
            },
        },
    )
    assert response.status_code == 201

    mock_callback.wait_call()

    # 3. post message with same language (test not translating)

    @mockserver.json_handler('/ya_translate/detect')
    def mock_detect_same(request):
        assert request.args.to_dict() == {'srv': 'taxi', 'hint': 'ru,en'}
        assert request.get_data().decode() == 'text=nottr'
        return {'code': 200, 'lang': 'ru'}

    @mockserver.json_handler('/ya_translate/translate')
    def mock_translate_same(request):
        assert False

    @mockserver.json_handler('/callback_url')
    def mock_callback_same(request):
        data = json.loads(request.get_data())
        assert request.headers['Accept-Language'] == 'ru'
        assert 'newest_message_id' in data
        assert data['text'] == 'nottr'
        return {}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/add_update',
        {
            'created_date': '',
            'newest_message_id': '4',
            'message': {
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': ['ru', 'en'],
                        'app_language': 'en',
                        'system_languages': ['en'],
                    },
                },
                'sender': {'id': 'driver_id', 'role': 'driver'},
                'text': 'nottr',
            },
        },
    )
    assert response.status_code == 201

    mock_callback_same.wait_call()


@pytest.mark.config(CLIENTDRIVER_CHAT_TRANSLATION_ENABLED=True)
@pytest.mark.now('2018-05-15T17:07:57.000000Z')
def test_empty_translations(taxi_chat, mockserver):
    # 1. create
    response = taxi_chat.post(
        '1.0/chat',
        {
            'metadata': {'order_locale': 'ru'},
            'participants': [
                {
                    'action': 'add',
                    'id': 'user_id',
                    'role': 'client',
                    'metadata': {
                        'translation_settings': {
                            'do_not_translate': [],
                            'to': 'ru-RU, ru;q=0.8,en;q=0.6',
                        },
                    },
                    'subscription': {
                        'callback_url': mockserver.url('callback_url'),
                        'fields': ['newest_message_id', 'text'],
                    },
                },
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    chat_id = data['id']

    # 2. add driver

    @mockserver.json_handler('/callback_url')
    def mock_empty_text_callback(request):
        data = json.loads(request.get_data())
        assert data['text'] == ''
        return {}

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/add_update',
        {
            'created_date': '',
            'newest_message_id': '2',
            'update_participants': {
                'id': 'driver_id',
                'role': 'driver',
                'action': 'add',
            },
        },
    )
    assert response.status_code == 201

    # 3. add empty message as driver

    response = taxi_chat.post(
        '1.0/chat/' + chat_id + '/add_update',
        {
            'created_date': '',
            'newest_message_id': '3',
            'message': {
                'id': '',
                'metadata': {
                    'language_hint': {
                        'keyboard_languages': ['ru', 'en'],
                        'app_language': 'en',
                        'system_languages': ['en'],
                    },
                },
                'sender': {'id': 'driver_id', 'role': 'driver'},
                'text': '',
            },
        },
    )
    assert response.status_code == 201

    mock_empty_text_callback.wait_call()
    mock_empty_text_callback.wait_call()
