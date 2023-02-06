import pathlib

import pytest

from internal_b2b_badge.badge_bot.static import messages


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_start_good_user(
        web_app_client, web_app, mock_badgepay_payment_tokens, patch,
):
    @patch('aiogram.Bot.send_photo')
    async def _send_photo(chat_id, photo, caption, reply_markup):
        assert chat_id == 57
        assert caption == messages.START_MESSAGE % 'good_boy'
        assert photo.file.read() == b'good_boy_token'

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Yandex',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'language_code': 'ru',
            },
            'chat': {
                'id': 57,
                'first_name': 'Yandex',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_start_good_user_then_troubles_to_get_qr(
        web_app_client, web_app, mock_badgepay_payment_tokens, patch,
):
    @patch('aiogram.Bot.send_photo')
    async def _send_photo(chat_id, photo, caption, reply_markup):
        assert chat_id == 57
        assert caption == messages.TROUBLES_WITH_BADGE
        dir_path = str(
            pathlib.Path(__file__)
            .parent.resolve()
            .parent.resolve()
            .parent.resolve(),
        )
        path = f'{dir_path}/internal_b2b_badge/badge_bot/static/error.png'
        with open(path, 'rb') as er_file:
            assert photo.file.read() == er_file.read()

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Yandex',
                'last_name': 'Boy',
                'username': 'tg_boy_who_crash_badgepay',
                'language_code': 'ru',
            },
            'chat': {
                'id': 57,
                'first_name': 'Yandex',
                'last_name': 'Boy',
                'username': 'tg_boy_who_crash_badgepay',
                'type': 'private',
            },
            'date': 1638400104,
            'text': '/start',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200
