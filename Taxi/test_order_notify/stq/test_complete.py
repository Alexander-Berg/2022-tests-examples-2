import pytest

from order_notify.notifications.common import CompleteNotifier
from order_notify.payloads import common as payload_logic
from test_order_notify.conftest import BASE_PAYLOAD
from test_order_notify.conftest import TRANSLATIONS_NOTIFY


@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY,
    tariff={
        'currency_sign.rub': {'ru': '₽'},
        'currency.rub': {'ru': 'руб.'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$ $CURRENCY$'},
    },
)
@pytest.mark.parametrize(
    'feedback_code, expected_text',
    [
        pytest.param(200, 'Стоимость заказа 100 ₽', id='feedback exist'),
        pytest.param(
            404,
            'Стоимость заказа 100 ₽ Оцените поездку.',
            id='feedback not exist',
        ),
        pytest.param(500, 'Стоимость заказа 100 ₽', id='feedback error'),
    ],
)
async def test_complete_with_feedback(
        stq3_context,
        mockserver,
        mock_tariff_zones,
        load_json,
        feedback_code,
        expected_text,
):
    @mockserver.json_handler(
        '/passenger-feedback/passenger-feedback/v1/retrieve',
    )
    def _mock_feedback(request):
        if feedback_code == 200:
            return {
                'app_comment': False,
                'call_me': False,
                'choices': {},
                'rating': 5,
            }
        return mockserver.make_response(status=feedback_code)

    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _mock_push(request):
        assert request.json['data']['payload']['text'] == expected_text
        return {}

    locale = 'ru'

    raw_payload = payload_logic.RawPayload(**BASE_PAYLOAD)
    payload = payload_logic.CommonPayload(stq3_context, locale, raw_payload)
    notifier = CompleteNotifier(stq3_context, 'order_id_1', locale, payload)

    await notifier.send_push('user_id_1')

    assert _mock_push.times_called == 1
