# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=invalid-name

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from grocery_payments_billing_plugins import *  # noqa: F403 F401

from . import consts
from . import models


@pytest.fixture(name='grocery_orders')
def mock_grocery_orders(grocery_orders_lib):
    grocery_orders_lib.add_order(
        order_id=consts.ORDER_ID,
        cart_id=consts.CART_ID,
        created=consts.NOW,
        due=consts.NOW,
        courier_info={
            'id': 'some-courier-id-123',
            'transport_type': consts.TRANSPORT_TYPE,
            'balance_client_id': consts.BALANCE_CLIENT_ID,
            'eats_courier_id': consts.EATS_COURIER_ID,
            'vat': consts.COURIER_VAT,
        },
        depot={'id': consts.DEPOT_ID, 'city': 'order_city'},
        finish_started=consts.FINISH_STARTED,
        yandex_uid=consts.YANDEX_UID,
        user_info={
            'yandex_uid': consts.YANDEX_UID,
            'personal_phone_id': consts.PERSONAL_PHONE_ID,
            'user_ip': consts.USER_IP,
        },
    )
    return grocery_orders_lib


@pytest.fixture
def run_grocery_payments_billing_tlog_callback(stq_runner):
    async def _inner(expect_fail=False, payment_type='card', **kwargs):
        obj = {
            'info': {
                'order_id': consts.ORDER_ID,
                'country': models.Country.Russia.name,
                'receipt_type': 'payment',
                'receipt_data_type': models.ReceiptDataType.Order.value,
                'items': [],
                'payment_method': {
                    'type': payment_type,
                    'id': 'payment_method_id',
                },
                'operation_id': consts.OPERATION_ID,
                'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
                'terminal_id': consts.TERMINAL_ID,
                'payment_finished': consts.PAYMENT_FINISHED,
                **kwargs,
            },
            'receipt_id': consts.RECEIPT_ID,
        }

        await stq_runner.grocery_payments_billing_tlog_callback.call(
            task_id='task_id', kwargs=obj, expect_fail=expect_fail,
        )

    return _inner


@pytest.fixture
def run_grocery_payments_billing_eats_orders(stq_runner):
    async def _inner(expect_fail=False, **kwargs):
        obj = {
            'order_id': consts.EATS_ORDER_ID,
            'receipt_type': 'payment',
            'items': [],
            'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
            'currency': models.Country.Russia.currency,
            'event_at': consts.PAYMENT_FINISHED,
            'transaction_date': consts.FINISH_STARTED,
            'terminal_id': consts.TERMINAL_ID,
            **kwargs,
        }

        await stq_runner.grocery_payments_billing_eats_orders.call(
            task_id='task_id', kwargs=obj, expect_fail=expect_fail,
        )

    return _inner


@pytest.fixture
def check_eats_payments_billing_proxy_callback(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        stq_queue = stq.eats_payments_billing_proxy_callback
        assert stq_queue.times_called == times_called
        if times_called == 0:
            return

        args = stq_queue.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


def _check_kwargs(kwargs1, kwargs2):
    mock_helpers.assert_dict_contains(kwargs1, kwargs2)
