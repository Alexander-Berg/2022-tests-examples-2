from typing import Any
from typing import Dict

import pytest

from order_notify.stq import order_client_notification
from test_order_notify.conftest import BASE_PAYLOAD
from test_order_notify.conftest import TRANSLATIONS_NOTIFY

EXPECTED_INTENTS = ['taxi_cancel_by_user', 'taxi_cancel_by_user_extra']


@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY,
    tariff={
        'currency_sign.rub': {'ru': '₽'},
        'currency.rub': {'ru': 'руб.'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$ $CURRENCY$'},
    },
)
@pytest.mark.parametrize(
    'payload_ext, is_extra_expected',
    [
        pytest.param(
            {'need_extra_early_hold_notification': True},
            False,
            id='not_early_hold',
        ),
        pytest.param(
            {
                'is_early_hold': True,
                'need_extra_early_hold_notification': False,
            },
            False,
            id='not_need_extra_early_hold',
        ),
        pytest.param(
            {
                'is_early_hold': True,
                'need_extra_early_hold_notification': True,
            },
            False,
            id='cancel_by_user',
        ),
        pytest.param(
            {
                'is_early_hold': True,
                'is_cancelled_by_early_hold': True,
                'need_extra_early_hold_notification': True,
            },
            True,
            id='cancel_by_early_hold',
        ),
    ],
)
async def test_cancel_by_user_extra(
        stq3_context,
        mockserver,
        mock_tariff_zones,
        load_json,
        payload_ext,
        is_extra_expected,
):
    expected_intents = EXPECTED_INTENTS.copy()
    if not is_extra_expected:
        expected_intents[1:] = []

    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _mock_push(request):
        assert request.json['intent'] == expected_intents.pop(0)
        return {}

    payload_doc: Dict[str, Any] = {**BASE_PAYLOAD, **payload_ext}

    await order_client_notification.task(
        stq3_context,
        order_id='order_id_1',
        event_key='handle_cancel_by_user',
        user_id='user_id_1',
        phone_id='phone_id_1',
        locale='ru',
        payload_doc=payload_doc,
    )

    assert _mock_push.times_called == 1 + int(is_extra_expected)
    assert not expected_intents
