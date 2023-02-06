import logging

import pytest


MODULES = [
    'internal_b2b_badge.badge_bot.start_command',
    'internal_b2b_badge.badge_bot.refresh_callback',
    'internal_b2b_badge.badge_bot.another_msg_handler',
]

HANDLERS = list(map(lambda x: x.rpartition('.')[2], MODULES))


async def bad_handler(*args, **kwargs):
    assert False, 'BAD HANDLER'


async def good_handler(*args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info('GOOD HANDLER')


class FakeModule:
    def __init__(self, catched_handler):
        for handler in HANDLERS:
            self.__setattr__(
                handler,
                good_handler if handler == catched_handler else bad_handler,
            )


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_start_command(
        web_app_client, web_app, monkeypatch,
):  # pylint: disable=W0621
    fake_module = FakeModule('start_command')
    for module in MODULES:
        monkeypatch.setattr(module, fake_module)
    web_app['context'].tg_bot.tg_dp.message_handlers.handlers = []
    await web_app['context'].tg_bot.on_startup()

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Good',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'language_code': 'ru',
            },
            'chat': {
                'id': 57,
                'first_name': 'Good',
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
async def test_some_text(
        web_app_client, web_app, monkeypatch,
):  # pylint: disable=W0621
    fake_module = FakeModule('another_msg_handler')
    for module in MODULES:
        monkeypatch.setattr(module, fake_module)
    web_app['context'].tg_bot.tg_dp.message_handlers.handlers = []
    await web_app['context'].tg_bot.on_startup()

    msg = {
        'update_id': 12345678,
        'message': {
            'message_id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Good',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'language_code': 'ru',
            },
            'chat': {
                'id': 57,
                'first_name': 'Good',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'type': 'private',
            },
            'date': 1638400104,
            'text': 'не понимаю как пользоваться этой штукой',
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200


@pytest.mark.pgsql('internal_b2b', files=('internal_b2b.sql',))
async def test_refresh_callback(
        web_app_client, web_app, monkeypatch,
):  # pylint: disable=W0621
    fake_module = FakeModule('refresh_callback')
    for module in MODULES:
        monkeypatch.setattr(module, fake_module)
    web_app['context'].tg_bot.tg_dp.message_handlers.handlers = []
    await web_app['context'].tg_bot.on_startup()

    msg = {
        'update_id': 12345678,
        'callback_query': {
            'id': 57,
            'from': {
                'id': 57,
                'is_bot': False,
                'first_name': 'Good',
                'last_name': 'Boy',
                'username': 'tg_good_boy',
                'language_code': 'ru',
            },
            'data': 'refresh_callback',
            'message': {
                'message_id': 57,
                'from': {
                    'id': 57,
                    'is_bot': False,
                    'first_name': 'Good',
                    'last_name': 'Boy',
                    'username': 'tg_good_boy',
                    'language_code': 'ru',
                },
                'chat': {
                    'id': 57,
                    'first_name': 'Good',
                    'last_name': 'Boy',
                    'username': 'tg_good_boy',
                    'type': 'private',
                },
                'date': 1638400104,
                'text': 'не понимаю как пользоваться этой штукой',
            },
        },
    }

    resp = await web_app_client.post('/webhook', json=msg)
    assert resp.status == 200
