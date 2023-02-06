import pytest

from internal_b2b_badge.badge_bot.static import messages


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_deleted_user(web_app_client, web_app, patch):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text):
        assert chat_id == 42
        assert text == messages.IS_DELETED

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Deleted',
                'last_name': 'Boy',
                'username': 'tg_deleted_boy',
                'language_code': 'ru',
            },
            'chat': {
                'id': 42,
                'first_name': 'Deleted',
                'last_name': 'Boy',
                'username': 'tg_deleted_boy',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_dismissed_user(web_app_client, web_app, patch):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text):
        assert chat_id == 42
        assert text == messages.IS_DISMISSED

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Dismissed',
                'last_name': 'Boy',
                'username': 'tg_dismissed_boy',
                'language_code': 'ru',
            },
            'chat': {
                'id': 42,
                'first_name': 'Dismissed',
                'last_name': 'Boy',
                'username': 'tg_dismissed_boy',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_twins_user(web_app_client, web_app, patch):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text):
        assert chat_id == 42
        assert text == messages.CANT_FOUND_ON_STAFF

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Twin',
                'last_name': 'Boy',
                'username': 'twins_tg',
                'language_code': 'ru',
            },
            'chat': {
                'id': 42,
                'first_name': 'Twin',
                'last_name': 'Boy',
                'username': 'twins_tg',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_enemy_user(web_app_client, web_app, patch):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text):
        assert chat_id == 42
        assert text == messages.CANT_FOUND_ON_STAFF

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Ya ne',
                'last_name': 'Iz Yandex',
                'username': 'tg_sber_bot',
                'language_code': 'ru',
            },
            'chat': {
                'id': 42,
                'first_name': 'Ya ne',
                'last_name': 'Iz Yandex',
                'username': 'tg_sber_bot',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_noname_user(web_app_client, web_app, patch):
    @patch('aiogram.Bot.send_message')
    async def _send_message(chat_id, text):
        assert chat_id == 42
        assert text == messages.CANT_FOUND_ON_STAFF

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Ya ne',
                'last_name': 'Iz Yandex',
                'language_code': 'ru',
            },
            'chat': {
                'id': 42,
                'first_name': 'Ya ne',
                'last_name': 'Iz Yandex',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200
