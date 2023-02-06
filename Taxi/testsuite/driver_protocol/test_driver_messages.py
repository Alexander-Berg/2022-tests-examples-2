import json

import pytest


def test_unauthorized(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.get('driver/messages')
    assert response.status_code == 401

    response = taxi_driver_protocol.get('driver/messages?db=1')
    assert response.status_code == 401

    response = taxi_driver_protocol.get('driver/messages?db=999&session=abc')
    assert response.status_code == 401

    response = taxi_driver_protocol.get(
        'driver/messages?db=abc&session=qwerty',
    )
    assert response.status_code == 401

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty',
    )
    assert response.status_code != 401


@pytest.mark.redis_store(
    [
        'lpush',
        'Chat:Messages:PRIVATE:999:888',
        json.dumps({'msg': 'Hello'}),
        json.dumps({'msg': 'World'}),
    ],
)
def test_messages(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty',
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert items == []

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty&channel=PRIVATE',
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 2


def test_disabled(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('666', 'qwerty', '888')

    response = taxi_driver_protocol.get(
        'driver/messages?db=666&session=qwerty',
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['db'] == 'SUPPORT'


@pytest.mark.redis_store(['hmset', 'ChatBlock:Items', {'999:888': '1'}])
def test_blocked(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty',
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 1
    assert items[0]['db'] == 'SUPPORT'


def test_clientchat(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:chatid/history')
    def mock_history(request):
        assert json.loads(request.get_data()) == {
            'include_metadata': True,
            'on_behalf_of': {'id': '999_888', 'role': 'driver'},
        }
        return mockserver.make_response(
            json.dumps(
                {
                    'updates': [
                        {
                            'created_date': 'cd',
                            'message': {
                                'id': 'msg_id',
                                'text': 'history message',
                                'sender': {
                                    'id': 'sender_id',
                                    'role': 'client',
                                },
                                'language': 'en',
                                'translations': [
                                    {'language': 'de', 'text': 'de text'},
                                ],
                            },
                            'newest_message_id': '4',
                        },
                        {
                            'created_date': 'cd',
                            'message': {
                                'id': 'msg_id3',
                                'sender': {'id': 'system', 'role': 'system'},
                            },
                            'newest_message_id': '3',
                        },
                        {
                            'created_date': 'cd',
                            'message': {
                                'id': 'msg_id3',
                                'text': 'history message',
                                'sender': {
                                    'id': 'sender_id',
                                    'role': 'client',
                                },
                                'metadata': {'action': 'user_ready'},
                            },
                            'newest_message_id': '3',
                        },
                        {
                            'created_date': 'cd',
                            'message': {
                                'id': 'msg_id2',
                                'text': 'tpl translate',
                                'sender': {'id': 'system', 'role': 'system'},
                                'metadata': {
                                    'message_key': 'tpl_key',
                                    'message_params': [
                                        {
                                            'name': 'param_1',
                                            'value': 'value_1',
                                        },
                                        {
                                            'name': 'param_2',
                                            'value': 'ru',
                                            'type': 'language',
                                        },
                                    ],
                                },
                            },
                            'newest_message_id': '2',
                        },
                    ],
                    'newest_message_id': '4',
                    'total': 3,
                    'all_languages': ['en', 'de'],
                    'can_translate': True,
                    'metadata': {'can_translate': True},
                },
            ),
            200,
        )

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty'
        '&channel=%24%24taxichat%3Achatid',
    )
    assert response.status_code == 200
    data = response.json()
    assert data['all_languages'] == ['en', 'de']
    assert data['can_translate'] is True
    assert data['items'] == [
        {
            'name': 'sender_id',
            'format': 0,
            'db': '999',
            'user_type': 0,
            'msg': 'history message',
            'user': 'client',
            'date': 'cd',
            'guid': 'msg_id',
            'language': 'en',
            'translation': {'text': 'de text', 'language': 'de'},
        },
        {
            'name': 'sender_id',
            'format': 0,
            'db': '999',
            'user_type': 0,
            'msg': 'On my way',
            'user': 'client',
            'date': 'cd',
            'guid': 'msg_id3',
        },
        {
            'date': 'cd',
            'db': '999',
            'format': 0,
            'guid': 'msg_id2',
            'msg': 'Text value_1 Russian',
            'name': 'system',
            'user': 'system',
            'user_type': 0,
        },
    ]


@pytest.mark.config(CLIENTDRIVER_CHAT_AUTOTRANSLATE_SYSTEM_MESSAGES=True)
@pytest.mark.parametrize(
    'text,tanker_key,tanker_locale,translations'
    ',can_translate,expected_text',
    [
        (  # no tanker key, use autotranslate
            'оригинал',
            None,
            None,
            [{'language': 'en', 'text': 'translation'}],
            True,
            'translation',
        ),
        (  # no tanker key, but translations disabled
            'оригинал',
            None,
            None,
            [{'language': 'en', 'text': 'translation'}],
            False,
            'оригинал',
        ),
        (  # no prefer tanker translation, ignore auto
            'оригинал',
            'key',
            'et',
            [{'language': 'en', 'text': 'translation'}],
            True,
            'value',
        ),
        (  # already in required language, dont translate
            'оригинал',
            'key',
            'en',
            [{'language': 'en', 'text': 'translation'}],
            True,
            'оригинал',
        ),
        (  # target language not supported by tanker, use autotranslate
            'оригинал',
            'key',
            'en',
            [{'language': 'et', 'text': 'translation'}],
            True,
            'translation',
        ),
        (
            # multiple translaitons, ignore
            'original text',
            None,
            None,
            [
                {'language': 'ru', 'text': 'Перевод оригинала'},
                {'language': 'en', 'text': 'translation'},
            ],
            True,
            'original text',
        ),
    ],
)
def test_clientchat_system_message_translate(
        text,
        tanker_key,
        tanker_locale,
        translations,
        can_translate,
        expected_text,
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    @mockserver.json_handler('/chat/1.0/chat/$$taxichat:chatid/history')
    def mock_history(request):
        response = {
            'updates': [
                {
                    'created_date': 'cd2',
                    'message': {
                        'id': '2',
                        'text': text,
                        'sender': {'id': 'system', 'role': 'system'},
                        'metadata': {},
                    },
                    'newest_message_id': '1',
                },
            ],
            'metadata': {'can_translate': can_translate},
            'can_translate': True,
            'participants': [],
            'newest_message_id': '2',
            'total': 2,
        }
        message = response['updates'][0]['message']
        if tanker_key:
            message['metadata']['message_key'] = tanker_key
        if tanker_locale:
            message['metadata']['tanker_locale'] = tanker_locale
        if translations:
            message['translations'] = translations
        return mockserver.make_response(json.dumps(response), 200)

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session='
        'qwerty&channel=%24%24taxichat%3Achatid',
    )
    assert response.status_code == 200
    data = response.json()
    expected = {
        'items': [
            {
                'name': 'system',
                'format': 0,
                'db': '999',
                'user_type': 0,
                'msg': expected_text,
                'user': 'system',
                'date': 'cd2',
                'guid': '2',
            },
        ],
        'md5': '2',
    }
    if can_translate:
        expected['can_translate'] = True
    assert data == expected


@pytest.mark.redis_store(
    [
        'lpush',
        'Chat:Messages:PRIVATE:999:888',
        json.dumps({'msg': 'Hello'}),
        json.dumps({'msg': 'World'}),
    ],
    ['set', 'Chat:Md5:PRIVATE:999:888', 'asdfgh'],
)
def test_messages_etag(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty&channel=PRIVATE',
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 2

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty&channel=PRIVATE&md5=asdfgh',
    )
    assert response.status_code == 200
    assert len(response.text) == 0

    response = taxi_driver_protocol.get(
        'driver/messages?db=999&session=qwerty&channel=PRIVATE&md5=zxcvbn',
    )
    assert response.status_code == 200
    items = response.json()['items']
    assert len(items) == 2
