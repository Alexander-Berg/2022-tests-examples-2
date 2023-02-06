import re

import pytest


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_receive(taxi_messenger, mockserver, testpoint):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.12345.42',
            'payload': {'text': 'hello!', 'type': 'text'},
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'message': {
                        'message_id': 42,
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'type': 'private',
                        },
                        'date': 1648712035,
                        'text': 'hello!',
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
@pytest.mark.parametrize(
    'provider_message_type,message_type,media_type,media_body',
    [
        (
            'document',
            'document',
            'document',
            {
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'file_name': 'another_file_name.ext',
            },
        ),
        (
            'photo',
            'image',
            'image',
            [
                {
                    'file_id': 'SMALL_FILE_ID_VALUE',
                    'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                    'width': 10,
                    'height': 10,
                },
                {
                    'file_id': 'FILE_ID_VALUE',
                    'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                    'width': 100,
                    'height': 100,
                },
                {
                    'file_id': 'MIDDLE_FILE_ID_VALUE',
                    'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                    'width': 50,
                    'height': 50,
                },
            ],
        ),
        (
            'audio',
            'audio',
            'audio',
            {
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'file_name': 'another_file_name.ext',
                'duration': 3,
            },
        ),
        (
            'video',
            'video',
            'video',
            {
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'file_name': 'another_file_name.ext',
                'duration': 3,
                'width': 100,
                'height': 100,
            },
        ),
        (
            'sticker',
            'sticker',
            'image',
            {
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'width': 100,
                'height': 100,
                'is_animated': False,
            },
        ),
        (
            'voice',
            'audio',
            'voice',
            {
                'duration': 11,
                'mime_type': 'audio/ogg',
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'file_size': 39492,
            },
        ),
    ],
)
async def test_receive_media(
        taxi_messenger,
        mockserver,
        testpoint,
        provider_message_type,
        message_type,
        media_type,
        media_body,
):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        file_name = (
            media_body['file_name']
            if isinstance(media_body, dict) and ('file_name' in media_body)
            else 'some_file.ext'
        )
        assert request.json['payload'].pop('file_name') == file_name
        assert file_name in request.json['payload'].pop('url')

        media_id = request.json['payload'].pop('media_id')
        assert re.fullmatch(r'([0-9a-f]{32})', media_id)

        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.12345.42',
            'payload': {
                'type': 'media',
                'media_type': message_type,
                'caption': 'Support hello',
            },
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'message': {
                        'message_id': 42,
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'type': 'private',
                        },
                        'date': 1648712035,
                        provider_message_type: media_body,
                        'caption': 'Support hello',
                    },
                },
            ],
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getFile')
    def _get_file(request):
        assert request.json['file_id'] == 'FILE_ID_VALUE'
        return {
            'ok': True,
            'result': {
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'file_path': 'SOME_PATH/some_file.ext',
            },
        }

    @mockserver.handler('/file/bot_auth_token/SOME_PATH/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response('Some data', 200)

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_receive_location(taxi_messenger, mockserver, testpoint):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.12345.42',
            'payload': {
                'latitude': 55.597,
                'longitude': 38.113,
                'type': 'location',
            },
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'message': {
                        'message_id': 42,
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'type': 'private',
                        },
                        'date': 1648712035,
                        'location': {'latitude': 55.597, 'longitude': 38.113},
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_find_login(
        taxi_messenger, mockserver, testpoint, mongodb, load_json,
):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.1100.42',
            'payload': {'text': 'hello!', 'type': 'text'},
            'phone_id': '',
            'login_id': 'login_pdid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return load_json('get_updates.json')

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()

    user_doc = mongodb.messenger_telegram_users.find_one(
        {'private_chat_id': 1100},
    )
    assert user_doc['account'] == 'support_tg_bot'
    assert user_doc['personal_login_id'] == 'login_pdid'


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_store_login(taxi_messenger, mockserver, testpoint, load_json):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/personal/v1/telegram_logins/find')
    def _logins_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    @mockserver.json_handler('/personal/v1/telegram_logins/store')
    def _logins_store(request):
        return {'id': 'stored_login_pdid', 'value': 'marge'}

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.1100.42',
            'payload': {'text': 'hello!', 'type': 'text'},
            'phone_id': '',
            'login_id': 'stored_login_pdid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return load_json('get_updates.json')

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_personal_error(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/personal/v1/telegram_logins/find')
    def _logins_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    @mockserver.json_handler('/personal/v1/telegram_logins/store')
    def _logins_store(request):
        return mockserver.make_response(
            '{"code":"500","message":"Error"}', 500,
        )

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return load_json('get_updates.json')

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        pass


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_login_changed(taxi_messenger, mockserver, testpoint, mongodb):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/personal/v1/telegram_logins/find')
    def _logins_find(request):
        return {'id': 'lid', 'value': 'marge'}

    @mockserver.json_handler('/personal/v1/telegram_logins/store')
    def _logins_store(request):
        return {'id': 'stored_login_pdid', 'value': 'marge'}

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'message_id': 'support_tg_bot.12345.42',
            'channel': 'telegram',
            'payload': {'text': 'hello!', 'type': 'text'},
            'phone_id': 'phid',
            'login_id': 'stored_login_pdid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'message': {
                        'message_id': 42,
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge_new',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge_new',
                            'type': 'private',
                        },
                        'date': 1648712035,
                        'text': 'hello!',
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()

    user_doc = mongodb.messenger_telegram_users.find_one(
        {'private_chat_id': 12345},
    )
    assert user_doc['account'] == 'support_tg_bot'
    assert user_doc['personal_login_id'] == 'stored_login_pdid'


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_receice_contact_find(
        taxi_messenger, mockserver, testpoint, mongodb,
):
    @testpoint('telegram_event_store_contact')
    def store_contact(_):
        pass

    @mockserver.json_handler('/personal/v1/telegram_logins/find')
    def _logins_find(request):
        return {'id': 'find_login_id', 'value': 'marge'}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_find(request):
        return {'id': 'find_phone_id', 'value': '+79261231212'}

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 65549738,
                    'message': {
                        'message_id': 28,
                        'from': {
                            'id': 112233,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'mylogin',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 112233,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'mylogin',
                            'type': 'private',
                        },
                        'date': 112233,
                        'reply_to_message': {
                            'message_id': 27,
                            'from': {
                                'id': 5137140366,
                                'is_bot': True,
                                'first_name': 'MargeBot',
                                'username': 'test_bot',
                            },
                            'chat': {
                                'id': 112233,
                                'first_name': 'Maria',
                                'last_name': 'German',
                                'username': 'marge25',
                                'type': 'private',
                            },
                            'date': 1649929414,
                            'text': 'Предоставьте номер телефона',
                        },
                        'contact': {
                            'phone_number': '+79261231212',
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'user_id': 112233,
                        },
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await store_contact.wait_call()

    user_doc = mongodb.messenger_telegram_users.find_one(
        {'private_chat_id': 112233},
    )
    assert user_doc['account'] == 'support_tg_bot'
    assert user_doc['personal_login_id'] == 'find_login_id'
    assert user_doc['personal_phone_id'] == 'find_phone_id'


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_receice_contact_store(
        taxi_messenger, mockserver, testpoint, mongodb,
):
    @testpoint('telegram_event_store_contact')
    def store_contact(_):
        pass

    @mockserver.json_handler('/personal/v1/telegram_logins/find')
    def _logins_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_find(request):
        return mockserver.make_response(
            '{"code":"404","message":"No document with such id"}', 404,
        )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        return {'id': 'stored_phone_id', 'value': '+79261231212'}

    @mockserver.json_handler('/personal/v1/telegram_logins/store')
    def _logins_store(request):
        return {'id': 'stored_login_id', 'value': 'marge_new'}

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 65549738,
                    'message': {
                        'message_id': 28,
                        'from': {
                            'id': 112233,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'mylogin',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 112233,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'mylogin',
                            'type': 'private',
                        },
                        'date': 112233,
                        'reply_to_message': {
                            'message_id': 27,
                            'from': {
                                'id': 5137140366,
                                'is_bot': True,
                                'first_name': 'MargeBot',
                                'username': 'test_bot',
                            },
                            'chat': {
                                'id': 112233,
                                'first_name': 'Maria',
                                'last_name': 'German',
                                'username': 'marge25',
                                'type': 'private',
                            },
                            'date': 1649929414,
                            'text': 'Предоставьте номер телефона',
                        },
                        'contact': {
                            'phone_number': '+79261231212',
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'user_id': 112233,
                        },
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await store_contact.wait_call()

    user_doc = mongodb.messenger_telegram_users.find_one(
        {'private_chat_id': 112233},
    )
    assert user_doc['account'] == 'support_tg_bot'
    assert user_doc['personal_login_id'] == 'stored_login_id'
    assert user_doc['personal_phone_id'] == 'stored_phone_id'


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_receive_callback_query(taxi_messenger, mockserver, testpoint):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.5137140366.76',
            'payload': {'id': '12', 'text': 'Option11', 'type': 'list'},
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 65549758,
                    'callback_query': {
                        'id': '633351853078082065',
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'language_code': 'ru',
                        },
                        'message': {
                            'message_id': 76,
                            'from': {
                                'id': 5137140366,
                                'is_bot': True,
                                'first_name': 'MargeBot',
                                'username': 'marge_bot',
                            },
                            'chat': {
                                'id': 12345,
                                'first_name': 'Maria',
                                'last_name': 'German',
                                'username': 'marge',
                                'type': 'private',
                            },
                            'date': 1652953475,
                            'text': 'Choose one',
                            'reply_markup': {
                                'inline_keyboard': [
                                    [
                                        {
                                            'text': 'Option11',
                                            'callback_data': '12',
                                        },
                                        {
                                            'text': 'Option12',
                                            'callback_data': '12',
                                        },
                                    ],
                                    [
                                        {
                                            'text': 'Option2',
                                            'callback_data': '2',
                                        },
                                    ],
                                ],
                            },
                        },
                        'chat_instance': '-2937322146019649726',
                        'data': '12',
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_edited(taxi_messenger, mockserver, testpoint):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.5137140366.79',
            'payload': {'text': 'Edited message text', 'type': 'text'},
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'edited_at': '2022-05-30T08:00:28+00:00',
            'message_type': 'edit',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'edited_message': {
                        'message_id': 79,
                        'from': {
                            'id': 5137140366,
                            'is_bot': True,
                            'first_name': 'MargeBot',
                            'username': 'marge_bot',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'type': 'private',
                        },
                        'date': 1653897597,
                        'edit_date': 1653897628,
                        'text': 'Edited message text',
                    },
                },
            ],
        }

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
async def test_media_too_big(taxi_messenger, mockserver, testpoint):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.12345.42',
            'payload': {'type': 'error', 'error_message': 'media_too_big'},
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'message': {
                        'message_id': 42,
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'type': 'private',
                        },
                        'date': 1648712035,
                        'video': {
                            'file_id': 'FILE_ID_VALUE',
                            'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                            'file_name': 'another_file_name.ext',
                            'duration': 3,
                            'width': 100,
                            'height': 100,
                        },
                        'caption': 'Support hello',
                    },
                },
            ],
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getFile')
    def _get_file(request):
        assert request.json['file_id'] == 'FILE_ID_VALUE'
        return mockserver.make_response(
            '{"ok":false,"error_code":400,"description":"Bad Request: file is too big"}',
            400,
        )

    @mockserver.handler('/file/bot_auth_token/SOME_PATH/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response('Some data', 200)

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
@pytest.mark.config(
    MESSENGER_MEDIA_STORAGE={
        'url_lifetime': 3600,
        'generate_inbound_file_name': True,
    },
)
async def test_generate_file_name(taxi_messenger, mockserver, testpoint):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        file_name = request.json['payload'].pop('file_name')
        assert file_name != 'file_name.ext'
        request.json['payload'].pop('media_id')
        request.json['payload'].pop('url')

        assert request.json == {
            'account': 'support_tg_bot',
            'channel': 'telegram',
            'message_id': 'support_tg_bot.12345.42',
            'payload': {
                'type': 'media',
                'media_type': 'document',
                'caption': 'Support hello',
            },
            'phone_id': 'phid',
            'login_id': 'lid',
            'received_at': '2021-02-20T00:00:00+00:00',
            'service': 'chatterbox',
            'message_type': 'new',
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        assert request.json['timeout'] == 300

        return {
            'ok': True,
            'result': [
                {
                    'update_id': 34243403,
                    'message': {
                        'message_id': 42,
                        'from': {
                            'id': 12345,
                            'is_bot': False,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'language_code': 'ru',
                        },
                        'chat': {
                            'id': 12345,
                            'first_name': 'Maria',
                            'last_name': 'German',
                            'username': 'marge',
                            'type': 'private',
                        },
                        'date': 1648712035,
                        'document': {
                            'file_id': 'FILE_ID_VALUE',
                            'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                            'file_name': 'file_name.ext',
                        },
                        'caption': 'Support hello',
                    },
                },
            ],
        }

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getFile')
    def _get_file(request):
        assert request.json['file_id'] == 'FILE_ID_VALUE'
        return {
            'ok': True,
            'result': {
                'file_id': 'FILE_ID_VALUE',
                'file_unique_id': 'FILE_UNIQUE_ID_VALUE',
                'file_path': 'SOME_PATH/some_file.ext',
            },
        }

    @mockserver.handler('/file/bot_auth_token/SOME_PATH/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response('Some data', 200)

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()


@pytest.mark.now('2021-02-20T00:00:00+00:00')
@pytest.mark.config(
    MESSENGER_ACCOUNTS={
        'support.tg_bot': {
            'description': 'Vip users support',
            'phone': '',
            'type': 'telegram',
        },
    },
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['support.tg_bot'],
            'description': 'chatterbox description',
            'webhooks': {
                'inbound_message': {
                    'qos': {'attempts': 2, 'timeout-ms': 500},
                    'tvm_service': 'service_name',
                    'url': {'$mockserver': '/service_name/v1/message/receive'},
                },
            },
        },
    },
)
async def test_replace_dots(taxi_messenger, mockserver, testpoint, load_json):
    @testpoint('telegram_event_loop_call_subscriber')
    def call_subscriber(_):
        pass

    @mockserver.json_handler('/service_name/v1/message/receive')
    def _service_name_mock(request):
        assert request.json['message_id'] == 'support_tg_bot.1100.42'

    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/getUpdates')
    def _get_updates(request):
        return load_json('get_updates.json')

    async with taxi_messenger.spawn_task('telegram-event-loop'):
        await call_subscriber.wait_call()
