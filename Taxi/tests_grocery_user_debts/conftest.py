# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=invalid-name

import typing

from grocery_mocks.utils import stq as stq_helpers
import pytest

from grocery_user_debts_plugins import *  # noqa: F403 F401

from . import consts
from . import models


@pytest.fixture
def default_debt(grocery_user_debts_db):
    debt = models.Debt(
        debt_id=consts.DEBT_ID,
        priority=0,
        order_id=consts.ORDER_ID,
        invoice_id=consts.INVOICE_ID,
    )
    grocery_user_debts_db.upsert(debt)
    return debt


@pytest.fixture(name='grocery_orders')
def mock_grocery_orders(grocery_orders_lib):
    grocery_orders_lib.add_order(
        order_id=consts.ORDER_ID, country=consts.COUNTRY,
    )
    grocery_orders_lib.order['user_info'].update(
        yandex_uid=consts.YANDEX_UID,
        personal_phone_id=consts.PERSONAL_PHONE_ID,
    )

    return grocery_orders_lib


@pytest.fixture
def run_transactions_callback(mockserver, stq_runner):
    async def _inner(
            task_id: str = 'task_id',
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            **kwargs,
    ):
        kwargs = {
            'invoice_id': consts.INVOICE_ID,
            'operation_id': consts.DEBT_OPERATION_ID,
            'operation_status': 'done',
            'notification_type': 'operation_finish',
            'transactions': [],
            **kwargs,
        }

        await stq_runner.grocery_user_debts_transactions_callback.call(
            task_id=task_id,
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def check_grocery_payments_transactions_callback(stq):
    def _inner(**kwargs):
        return stq_helpers.created_events(
            stq.grocery_payments_transactions_callback,
        ).check_event(**kwargs)

    return _inner
