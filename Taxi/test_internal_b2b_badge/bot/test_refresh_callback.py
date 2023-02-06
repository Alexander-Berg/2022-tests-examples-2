import pathlib

import pytest

from internal_b2b_badge.badge_bot.static import messages


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_refresh_good_user(
        web_app_client, web_app, mock_badgepay_payment_tokens, patch,
):
    @patch('aiogram.Bot.edit_message_media')
    async def _edit_message_media(chat_id, message_id, media, reply_markup):
        assert chat_id == 42
        assert message_id == 57
        assert media.caption == messages.START_MESSAGE % 'good_boy'
        assert media.file.file.read() == b'good_boy_token'

    msg = {
        'update_id': 286466272,
        'callback_query': {
            'id': '759901736079411451',
            'from': {
                'id': 176928410,
                'is_bot': False,
                'first_name': 'Good',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'language_code': 'en',
            },
            'message': {
                'message_id': 57,
                'from': {
                    'id': 2109910506,
                    'is_bot': True,
                    'first_name': 'YandexBadgeBotTest',
                    'username': 'YandexBadgeTestBot',
                },
                'chat': {
                    'id': 42,
                    'first_name': 'Good',
                    'last_name': 'Boy',
                    'username': 'tg_good_boy',
                    'type': 'private',
                },
                'date': 1638883615,
                'text': (
                    'Прости, что-то пошло не так. Попробуй обновить позже.'
                ),
                'reply_markup': {
                    'inline_keyboard': [
                        [{'text': '🔄', 'callback_data': 'refresh_callback'}],
                    ],
                },
            },
            'chat_instance': '8562472849135428406',
            'data': 'refresh_callback',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_refresh_good_user_user_then_troubles_to_get_qr(
        web_app_client, web_app, mock_badgepay_payment_tokens, patch,
):
    @patch('aiogram.Bot.edit_message_media')
    async def _edit_message_media(chat_id, message_id, media, reply_markup):
        assert chat_id == 42
        assert message_id == 57
        assert media.caption == messages.TROUBLES_WITH_BADGE
        dir_path = str(
            pathlib.Path(__file__)
            .parent.resolve()
            .parent.resolve()
            .parent.resolve(),
        )
        path = f'{dir_path}/internal_b2b_badge/badge_bot/static/error.png'
        with open(path, 'rb') as er_file:
            assert media.file.file.read() == er_file.read()

    msg = {
        'update_id': 286466272,
        'callback_query': {
            'id': '759901736079411451',
            'from': {
                'id': 176928410,
                'is_bot': False,
                'first_name': 'Good',
                'last_name': 'Boy',
                'username': 'tg_boy_who_crash_badgepay',
                'language_code': 'en',
            },
            'message': {
                'message_id': 57,
                'from': {
                    'id': 2109910506,
                    'is_bot': True,
                    'first_name': 'YandexBadgeBotTest',
                    'username': 'YandexBadgeTestBot',
                },
                'chat': {
                    'id': 42,
                    'first_name': 'Good',
                    'last_name': 'Boy',
                    'username': 'tg_boy_who_crash_badgepay',
                    'type': 'private',
                },
                'date': 1638883615,
                'text': (
                    'Прости, что-то пошло не так. Попробуй обновить позже.'
                ),
                'reply_markup': {
                    'inline_keyboard': [
                        [{'text': '🔄', 'callback_data': 'refresh_callback'}],
                    ],
                },
            },
            'chat_instance': '8562472849135428406',
            'data': 'refresh_callback',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200
