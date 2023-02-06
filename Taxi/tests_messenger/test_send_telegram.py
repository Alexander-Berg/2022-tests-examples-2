import aiohttp

import pytest

X_IDEMPOTENCY_TOKEN = 'token'
NOW = '2021-02-25T00:00:00+03:00'


async def _media_upload(taxi_messenger, media_type):
    form = aiohttp.FormData()
    form.add_field(name='content', value=b'file binary \x00 data')
    form.add_field(name='media_type', value=media_type)
    form.add_field(name='content_file_name', value='some_file.ext')
    form.add_field(name='service', value='chatterbox')
    response = await taxi_messenger.post('/v1/media/upload', data=form)
    media_id = response.json()['media_id']
    return media_id


@pytest.mark.now(NOW)
async def test_ok(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        request_data = request.json
        assert request_data == {'chat_id': 12345, 'text': 'Hello!'}
        return load_json('telegram_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 200
    message_id = response.json().pop('message_id')
    assert message_id


@pytest.mark.now(NOW)
async def test_unknown_personal(taxi_messenger):
    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'phone_id': 'unknown'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    MESSENGER_ACCOUNTS={
        'support_tg_bot': {
            'description': 'Vip users support',
            'phone': '',
            'type': 'telegram',
            'telegram': {'users_ttl': 1},
        },
    },
)
@pytest.mark.now(NOW)
async def test_expired(taxi_messenger):
    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )
    assert response.status_code == 400


@pytest.mark.now(NOW)
async def test_login_id_send(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        request_data = request.json
        assert request_data == {'chat_id': 12345, 'text': 'Hello!'}
        return load_json('telegram_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
        },
    )

    assert response.status_code == 200
    message_id = response.json().pop('message_id')
    assert message_id


@pytest.mark.now(NOW)
async def test_request_phone_number(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'text': 'Share your phone!',
            'reply_markup': {
                'keyboard': [
                    [{'request_contact': True, 'text': 'Take my phone'}],
                ],
                'one_time_keyboard': True,
                'resize_keyboard': True,
            },
        }

        return load_json('telegram_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {
                'button_text': 'Take my phone',
                'text': 'Share your phone!',
                'type': 'request_phone_number',
            },
        },
    )
    assert response.status_code == 200
    message_id = response.json().pop('message_id')
    assert message_id


@pytest.mark.now(NOW)
async def test_photo(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendPhoto')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'caption': 'Some caption',
            'photo': 'https://avatars.mds.yandex.net/mock.jpg',
        }

        return load_json('telegram_response.json')

    media_id = await _media_upload(taxi_messenger, 'image')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': media_id,
                'media_type': 'image',
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.now(NOW)
async def test_video(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendVideo')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'caption': 'Some caption',
            'video': 'https://avatars.mds.yandex.net/mock.jpg',
        }

        return load_json('telegram_response.json')

    media_id = await _media_upload(taxi_messenger, 'video')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': media_id,
                'media_type': 'video',
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.now(NOW)
async def test_audio(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendAudio')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'caption': 'Some caption',
            'audio': 'https://avatars.mds.yandex.net/mock.jpg',
        }

        return load_json('telegram_response.json')

    media_id = await _media_upload(taxi_messenger, 'audio')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': media_id,
                'media_type': 'audio',
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.now(NOW)
async def test_document(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendDocument')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'caption': 'Some caption',
            'document': 'https://avatars.mds.yandex.net/mock.jpg',
        }

        return load_json('telegram_response.json')

    media_id = await _media_upload(taxi_messenger, 'document')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': media_id,
                'media_type': 'document',
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.now(NOW)
async def test_sticker(taxi_messenger, mockserver, load_json):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendSticker')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'sticker': 'https://avatars.mds.yandex.net/mock.jpg',
        }

        return load_json('telegram_response.json')

    media_id = await _media_upload(taxi_messenger, 'image')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {
                'type': 'media',
                'caption': 'Some caption',
                'media_id': media_id,
                'media_type': 'sticker',
            },
        },
    )
    assert response.status_code == 200


@pytest.mark.now(NOW)
async def test_list(taxi_messenger, mockserver, load_json, mongodb):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        assert request.json == {
            'chat_id': 12345,
            'text': 'Hello list',
            'reply_markup': {
                'inline_keyboard': [
                    [
                        {'callback_data': '1', 'text': 'title 11'},
                        {'callback_data': '2', 'text': 'title 22'},
                    ],
                    [{'callback_data': '3', 'text': 'title 21'}],
                ],
            },
        }

        return load_json('telegram_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'login_id': 'lid'},
            'payload': {'text': 'Hello list', 'type': 'text'},
            'allowed_replies': {
                'type': 'list',
                'title': 'List title',
                'header': 'Header',
                'footer': 'Footer',
                'sections': [
                    {
                        'header': 'Section 1',
                        'items': [
                            {
                                'id': '1',
                                'text': 'title 11',
                                'description': 'description 11',
                            },
                            {
                                'id': '2',
                                'text': 'title 22',
                                'description': 'description 22',
                            },
                        ],
                    },
                    {
                        'header': 'Section 2',
                        'items': [
                            {
                                'id': '3',
                                'text': 'title 21',
                                'description': 'description 21',
                            },
                        ],
                    },
                ],
            },
        },
    )
    assert response.status_code == 200

    message_id = response.json().pop('message_id')
    assert message_id


@pytest.mark.now(NOW)
async def test_message_id(taxi_messenger, mockserver, load_json, mongodb):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        request_data = request.json
        assert request_data == {'chat_id': 12345, 'text': 'Hello!'}
        return load_json('telegram_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
            'service_message_id': '1234',
        },
    )
    assert response.status_code == 200
    message_id = response.json().pop('message_id')
    assert message_id == '19'


@pytest.mark.now(NOW)
async def test_blocked(taxi_messenger, mockserver):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        return mockserver.make_response(
            '{"ok":false,"error_code":403,"description":"Forbidden: bot was blocked by the user"}',
            403,
        )

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
            'service_message_id': '1234',
        },
    )
    assert response.status_code == 400


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'message_id,message_id_in_send,code',
    [
        ('5', '5', 200),
        ('bot1.678.6', '6', 200),
        ('abc1', None, 400),
        ('123.', None, 400),
    ],
)
async def test_reply_to(
        taxi_messenger,
        mockserver,
        load_json,
        message_id,
        message_id_in_send,
        code,
):
    @mockserver.json_handler('/telegram-bot-api/bot_auth_token/sendMessage')
    def _send_message(request):
        reply_to_message_id = request.json.pop('reply_to_message_id')
        assert str(reply_to_message_id) == message_id_in_send
        return load_json('telegram_response.json')

    response = await taxi_messenger.post(
        'v1/send',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'chatterbox',
            'account': 'support_tg_bot',
            'client': {'phone_id': 'phid'},
            'payload': {'text': 'Hello!', 'type': 'text'},
            'reply_to': message_id,
        },
    )
    assert response.status_code == code
