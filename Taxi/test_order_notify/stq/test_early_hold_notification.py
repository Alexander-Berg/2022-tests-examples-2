import pytest

from order_notify.stq import early_hold_notification


TRANSLATIONS_CLIENT_MESSAGES = {
    'order_notify.early_hold.push.text': {
        'ru': 'Мы заморозили %(hold_amount)s %(currency)s на вашей карте',
    },
}
TRANSLATIONS_TARIFFS = {'currency_sign.rub': {'ru': '₽'}}


@pytest.mark.parametrize(
    'expected_message', [pytest.param('Мы заморозили 100 ₽ на вашей карте')],
)
@pytest.mark.config(ORDER_NOTIFY_EARLY_HOLD_NOTIFICATION_ENABLED=True)
@pytest.mark.translations(
    client_messages=TRANSLATIONS_CLIENT_MESSAGES, tariff=TRANSLATIONS_TARIFFS,
)
async def test_early_hold_notification(
        stq3_context, mockserver, expected_message,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _ucommunications_handler(request):
        assert request.json['data']['payload']['msg'] == expected_message
        return {}

    await early_hold_notification.task(
        context=stq3_context,
        user_id='user_1',
        locale='ru',
        hold_amount=100,
        currency='RUB',
    )
    assert _ucommunications_handler.times_called == 1
