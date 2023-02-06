# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=invalid-name

import typing

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from grocery_payments_plugins import *  # noqa: F403 F401

from . import consts
from . import headers
from . import models


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.fixture(name='grocery_orders')
def mock_grocery_orders(grocery_orders_lib):
    order = grocery_orders_lib.add_order(
        order_id=consts.ORDER_ID,
        country=models.Country.Russia.name,
        region_id=consts.REGION_ID,
    )

    order.update(
        personal_phone_id=headers.PERSONAL_PHONE_ID,
        yandex_uid=headers.YANDEX_UID,
    )

    return grocery_orders_lib


@pytest.fixture
def run_transactions_callback(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            originator=models.InvoiceOriginator.grocery,
            **kwargs,
    ):
        kwargs = {
            'invoice_id': originator.prefix + consts.ORDER_ID,
            'operation_id': 'create:123',
            'operation_status': 'done',
            'notification_type': consts.OPERATION_FINISH,
            'transactions': [],
            **kwargs,
        }

        await stq_runner.grocery_payments_transactions_callback.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def run_payments_fallback_proxy_stq(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            originator=models.InvoiceOriginator.grocery,
            **kwargs,
    ):
        kwargs = {
            'invoice_id': originator.prefix + consts.ORDER_ID,
            'operation_id': 'create:123',
            'operation_status': 'done',
            'notification_type': consts.OPERATION_FINISH,
            'transactions': [],
            **kwargs,
        }

        await stq_runner.grocery_payments_fallback_proxy.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def run_operation_timeout_callback(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            originator=models.InvoiceOriginator.grocery,
            **kwargs,
    ):
        kwargs = {
            'invoice_id': originator.prefix + consts.ORDER_ID,
            'operation_id': 'create:123',
            **kwargs,
        }

        await stq_runner.grocery_payments_operation_timeout.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def run_user_actions_callback(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            originator=models.InvoiceOriginator.grocery,
            **kwargs,
    ):
        kwargs = {
            'invoice_id': originator.prefix + consts.ORDER_ID,
            'operation_id': 'create:123',
            'operation_status': 'done',
            'notification_type': consts.X3DS_NOTIFICATION_TYPE,
            'transactions': [],
            **kwargs,
        }

        await stq_runner.grocery_payments_user_actions_required.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def check_transactions_callback(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert (
            stq.grocery_payments_transactions_callback.times_called
            == times_called
        )
        if times_called == 0:
            return

        args = stq.grocery_payments_transactions_callback.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def check_grocery_invoices_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert stq.grocery_invoices_callback.times_called == times_called
        if times_called == 0:
            return

        args = stq.grocery_invoices_callback.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def check_cashback_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, eta=None, **kwargs):
        assert stq.universal_cashback_processing.times_called == times_called
        if times_called == 0:
            return

        args = stq.universal_cashback_processing.next_call()
        if eta is not None:
            _check_eta(args['eta'], eta)

        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def check_grocery_cashback_reward_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert stq.grocery_cashback_reward.times_called == times_called
        if times_called == 0:
            return

        args = stq.grocery_cashback_reward.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def check_operation_timeout_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, eta=None, **kwargs):
        assert (
            stq.grocery_payments_operation_timeout.times_called == times_called
        )
        if times_called == 0:
            return

        args = stq.grocery_payments_operation_timeout.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        if eta is not None:
            _check_eta(args['eta'], eta)

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def check_eats_billing_callback_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert (
            stq.eats_payments_billing_proxy_callback.times_called
            == times_called
        )
        if times_called == 0:
            return

        args = stq.eats_payments_billing_proxy_callback.next_call()

        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


def _check_eta(lhs, rhs):
    def _replace(value):
        return value.replace('+00:00', '')

    assert _replace(lhs.isoformat()) == _replace(rhs.isoformat())


def _check_kwargs(args, kwargs):
    mock_helpers.assert_dict_contains(args, kwargs)
