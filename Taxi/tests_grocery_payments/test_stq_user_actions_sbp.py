import pytest

from . import consts
from . import helpers
from . import models

CREATE_OPERATION_ID = f'{consts.OPERATION_CREATE}:{consts.OPERATION_ID}'

PURCHASE_TOKEN = 'some_token_123'

SBP_LINK = 'https://some.ru'

DEFAULT_OPERATION = helpers.make_operation(
    id=CREATE_OPERATION_ID, status='processing',
)

WEBVIEW_NOTIFICATION_FLOW = 'webview_notification'

WEBVIEW_NOTIFICATION_PAYLOAD = {
    'flow': WEBVIEW_NOTIFICATION_FLOW,
    'payment_form': SBP_LINK,
    'purchase_token': PURCHASE_TOKEN,
    'type': 'sbp',
}


async def test_tracking_update(
        run_user_actions_callback,
        grocery_orders,
        grocery_cart,
        transactions,
        grocery_payments_tracking,
        grocery_payments_configs,
):
    grocery_payments_configs.set_sbp_flow(flow=WEBVIEW_NOTIFICATION_FLOW)

    operation_id = CREATE_OPERATION_ID

    transaction = helpers.make_transaction(
        external_payment_id=PURCHASE_TOKEN,
        payment_type=models.PaymentType.sbp.value,
        operation_id=operation_id,
        status='hold_pending',
        payment_url=SBP_LINK,
    )

    transactions.retrieve.mock_response(
        operations=[DEFAULT_OPERATION], transactions=[transaction],
    )

    grocery_payments_tracking.update.check(
        order_id=consts.ORDER_ID, payload=WEBVIEW_NOTIFICATION_PAYLOAD,
    )

    await run_user_actions_callback(
        operation_id=operation_id,
        notification_type=consts.SBP_NOTIFICATION_TYPE,
    )

    assert grocery_payments_tracking.update.times_called == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'preferred_bank, payment_url, expected_payment_url',
    [
        (None, SBP_LINK, SBP_LINK),
        ('bank_unknown', SBP_LINK, SBP_LINK),
        ('bank', 'https://some.ru', 'bank_schema://some.ru'),
        ('bank', 'http://some.ru', 'bank_schema://some.ru'),
    ],
)
async def test_webview_notification(
        run_user_actions_callback,
        grocery_orders,
        grocery_cart,
        transactions,
        grocery_payments_tracking,
        grocery_payments_configs,
        grocery_payments_methods,
        preferred_bank,
        payment_url,
        expected_payment_url,
):
    flow = 'webview_notification'
    payment_type = models.PaymentType.sbp.value

    operation_id = CREATE_OPERATION_ID

    banks = [models.SbpBankInfo(bank_name=f'bank', schema='bank_schema')]

    grocery_payments_configs.set_sbp_flow(flow=flow)
    grocery_payments_methods.set_sbp_banks(banks)

    transaction = helpers.make_transaction(
        external_payment_id=PURCHASE_TOKEN,
        payment_type=payment_type,
        operation_id=operation_id,
        status='hold_pending',
        payment_url=payment_url,
    )

    transactions.retrieve.mock_response(
        operations=[DEFAULT_OPERATION], transactions=[transaction],
    )

    grocery_cart.set_payment_method(
        dict(
            type=payment_type,
            id='sbp_qr',
            meta=dict(sbp=dict(bank=preferred_bank)),
        ),
    )

    grocery_payments_tracking.update.check(
        order_id=consts.ORDER_ID,
        payload={
            'type': 'sbp',
            'flow': flow,
            'purchase_token': PURCHASE_TOKEN,
            'payment_form': expected_payment_url,
        },
    )

    await run_user_actions_callback(
        operation_id=operation_id,
        notification_type=consts.SBP_NOTIFICATION_TYPE,
    )

    assert grocery_payments_tracking.update.times_called == 1
