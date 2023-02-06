import pytest

from order_notify.stq.sbp import unsuccessful_payment_notification

TRANSLATIONS_CLIENT_MESSAGES = {
    'order_notify.sbp.unsuccessful_payment.push.text': {
        'ru': 'Оплата не прошла',
    },
}


@pytest.mark.parametrize(
    'expected_message', [pytest.param('Оплата не прошла')],
)
@pytest.mark.config(
    TAXI_PAYMENTS_SBP_NOTIFICATIONS={
        'unsuccessful_payment': {
            'enabled': True,
            'text_tanker_key': (
                'order_notify.sbp.unsuccessful_payment.push.text'
            ),
        },
    },
)
@pytest.mark.translations(client_messages=TRANSLATIONS_CLIENT_MESSAGES)
async def test_sbp_unsuccessful_payment_notification(
        stq3_context, mockserver, expected_message,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        assert request.json['data']['payload']['msg'] == expected_message
        return {}

    await unsuccessful_payment_notification.task(
        context=stq3_context,
        user_id='user_1',
        locale='ru',
        hold_amount=100,
        currency='RUB',
    )
    assert _ucommunications_handler.times_called == 1
