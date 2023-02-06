import pytest

from order_notify.stq import ordercommit_unavailable_by_credit_card


TRANSLATIONS_CLIENT_MESSAGES = {
    'ordercommit.plugins.card_check.card_unavaliable': {
        'ru': 'Оплата по карте невозможна',
    },
}


@pytest.mark.translations(client_messages=TRANSLATIONS_CLIENT_MESSAGES)
async def test_ordercommit_unavailable(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        expected_request = {
            'confirm': True,
            'intent': 'unknown',
            'ttl': 600,
            'user': 'user_1',
            'locale': 'ru',
            'data': {
                'payload': {
                    'id': '00000000000040008000000000000000',
                    'msg': 'Оплата по карте невозможна',
                    'show_in_foreground': True,
                },
                'repack': {
                    'apns': {
                        'aps': {
                            'content-available': 1,
                            'mutable-content': 1,
                            'sound': {'name': 'default'},
                            'alert': 'Оплата по карте невозможна',
                            'repack_payload': [
                                'id',
                                'msg',
                                'show_in_foreground',
                            ],
                        },
                    },
                    'fcm': {
                        'notification': {
                            'title': 'Оплата по карте невозможна',
                        },
                        'repack_payload': ['id', 'msg', 'show_in_foreground'],
                    },
                    'hms': {
                        'notification_title': 'Оплата по карте невозможна',
                        'repack_payload': ['id', 'msg', 'show_in_foreground'],
                    },
                },
            },
        }

        assert request.json == expected_request
        return {}

    await ordercommit_unavailable_by_credit_card.task(
        context=stq3_context, user_id='user_1', locale='ru',
    )
    assert _ucommunications_handler.times_called == 1
