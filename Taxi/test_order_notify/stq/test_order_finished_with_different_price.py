import pytest

from order_notify.stq import order_finished_with_different_price

TRANSLATIONS_CLIENT_MESSAGES = {
    'taxi_payments.card.push.final_price_less': {
        'ru': (
            'Стоимость %(new_price)s %(currency)s'
            ' вместо %(base_price)s %(currency)s, карта'
        ),
    },
    'taxi_payments.sbp.push.final_price_less': {
        'ru': (
            'Стоимость %(new_price)s %(currency)s '
            'вместо %(base_price)s %(currency)s, СБП'
        ),
    },
}
TRANSLATIONS_TARIFFS = {'currency.rub': {'ru': 'руб.'}}


@pytest.mark.parametrize(
    'payment_type,base_price,final_price,expected_message',
    [
        pytest.param(
            'sbp',
            122,
            132,
            'Стоимость 132 руб. вместо 122 руб., СБП',
            id='sbp_success',
        ),
        pytest.param(
            'card',
            122,
            132,
            'Стоимость 132 руб. вместо 122 руб., карта',
            id='card_success',
        ),
        pytest.param('card', 122, 122, '', id='card_success'),
    ],
)
@pytest.mark.config(
    ORDER_NOTIFY_DIFFERENT_ORDER_PRICE_PUSH={
        'enabled': True,
        'push_text_tanker_key': 'taxi_payments.card.push.final_price_less',
    },
    TAXI_PAYMENTS_SBP_NOTIFICATIONS={
        'complete': {
            'enabled': True,
            'text_tanker_key': 'taxi_payments.sbp.push.final_price_less',
        },
    },
)
@pytest.mark.translations(
    client_messages=TRANSLATIONS_CLIENT_MESSAGES, tariff=TRANSLATIONS_TARIFFS,
)
async def test_sbp_transporting_notification(
        stq3_context,
        mockserver,
        payment_type,
        base_price,
        final_price,
        expected_message,
):
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
                    'msg': expected_message,
                    'show_in_foreground': True,
                },
                'repack': {
                    'apns': {
                        'aps': {
                            'content-available': 1,
                            'mutable-content': 1,
                            'sound': {'name': 'default'},
                            'alert': expected_message,
                            'repack_payload': [
                                'id',
                                'msg',
                                'show_in_foreground',
                            ],
                        },
                    },
                    'fcm': {
                        'notification': {'title': expected_message},
                        'repack_payload': ['id', 'msg', 'show_in_foreground'],
                    },
                    'hms': {
                        'notification_title': expected_message,
                        'repack_payload': ['id', 'msg', 'show_in_foreground'],
                    },
                },
            },
        }

        assert request.json == expected_request
        return {}

    await order_finished_with_different_price.task(
        context=stq3_context,
        user_id='user_1',
        locale='ru',
        payment_type=payment_type,
        base_price=base_price,
        final_price=final_price,
        currency='RUB',
    )

    expected_call_count = 1 if expected_message else 0
    assert _ucommunications_handler.times_called == expected_call_count
