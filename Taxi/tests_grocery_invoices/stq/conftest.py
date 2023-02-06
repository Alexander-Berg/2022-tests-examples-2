# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
import copy

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from grocery_invoices_plugins import *  # noqa: F403 F401

from tests_grocery_invoices import consts
from tests_grocery_invoices import models

ERROR_CANNOT_FIND_TASK = 'Cannot find task with id: {}'


@pytest.fixture
def run_grocery_invoices_callback(stq_runner):
    async def _inner(
            expect_fail=False,
            exec_tries=1,
            task_created=None,
            task_id=consts.TASK_ID,
            **kwargs,
    ):
        obj = {
            'info': {
                'order_id': consts.ORDER_ID,
                'country': models.Country.Russia.name,
                'receipt_type': 'payment',
                'receipt_data_type': 'order',
                'items': [],
                'payment_method': consts.DEFAULT_PAYMENT_METHOD,
                'operation_id': consts.OPERATION_ID,
                'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
                'terminal_id': consts.TERMINAL_ID,
                'payment_finished': consts.PAYMENT_FINISHED,
                **kwargs,
            },
            'task_created': task_created or consts.NOW,
        }

        await stq_runner.grocery_invoices_callback.call(
            task_id=task_id,
            kwargs=obj,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def run_grocery_invoices_receipt_polling(stq_runner):
    async def _inner(
            expect_fail=False,
            exec_tries=1,
            polling_id=consts.EXTERNAL_PAYMENT_ID,
            params=None,
            send_billing_event=True,
            task_created=None,
            task_id=consts.TASK_ID,
            **kwargs,
    ):
        obj = {
            'info': {
                'order_id': consts.ORDER_ID,
                'country': models.Country.Russia.name,
                'receipt_type': 'payment',
                'receipt_data_type': 'order',
                'items': [],
                'payment_method': consts.DEFAULT_PAYMENT_METHOD,
                'operation_id': consts.OPERATION_ID,
                'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
                'terminal_id': consts.TERMINAL_ID,
                'payment_finished': consts.PAYMENT_FINISHED,
                **kwargs,
            },
            'polling_id': polling_id,
            'params': params or {},
            'task_created': task_created or consts.NOW,
            'send_billing_event': send_billing_event,
        }

        await stq_runner.grocery_invoices_receipt_polling.call(
            task_id=task_id,
            kwargs=obj,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def run_grocery_invoices_receipt_pushing(stq_runner):
    async def _inner(receipts, expect_fail=False):
        obj = {'receipts': receipts}

        await stq_runner.grocery_invoices_receipt_pushing.call(
            task_id='task_id', kwargs=obj, expect_fail=expect_fail,
        )

    return _inner


@pytest.fixture
def check_receipt_polling_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        if times_called is not None:
            assert (
                stq.grocery_invoices_receipt_polling.times_called
                == times_called
            )
        if times_called == 0:
            return

        if kwargs:
            if stq_event_id is None:
                args = stq.grocery_invoices_receipt_polling.next_call()
                _check_kwargs(args['kwargs'], kwargs)
            else:
                args = _find_task_args(
                    stq.grocery_invoices_receipt_polling, stq_event_id,
                )
                _check_kwargs(args['kwargs'], kwargs)

    return _inner


# pylint: disable=invalid-name
@pytest.fixture
def check_billing_tlog_callback_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert (
            stq.grocery_payments_billing_tlog_callback.times_called
            == times_called
        )
        if times_called == 0:
            return

        if stq_event_id is None:
            args = stq.grocery_payments_billing_tlog_callback.next_call()
            _check_kwargs(args['kwargs'], kwargs)
        else:
            args = _find_task_args(
                stq.grocery_payments_billing_tlog_callback, stq_event_id,
            )
            _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def default_fns_receipt(grocery_invoices_db, selfemployed):
    receipt = models.Receipt(
        receipt_id=selfemployed.receipt_id, receipt_source=consts.FNS_SOURCE,
    )
    grocery_invoices_db.insert(receipt)
    return receipt


@pytest.fixture
def default_isr_receipt(grocery_invoices_db):
    receipt = models.Receipt(
        payload=dict(
            country=models.Country.Israel.name,
            receipt_uuid='receipt_uuid',
            external_id='external_id',
        ),
    )
    grocery_invoices_db.insert(receipt)
    return receipt


def _find_task_args(stq_queue, stq_event_id):
    for _ in range(100):
        args = stq_queue.next_call()
        if args['id'] == stq_event_id:
            return args

    assert False, ERROR_CANNOT_FIND_TASK.format(stq_event_id)
    return None


def _check_kwargs(args, kwargs):
    mock_helpers.assert_dict_contains(args, kwargs)


@pytest.fixture
def prepare_no_courier_tasks(grocery_invoices_db, grocery_invoices_configs):
    def _do(tasks):
        grocery_invoices_configs.eats_receipts_service(consts.EATS_RECEIPTS)

        for task in tasks:
            grocery_invoices_db.insert_task(task)

        task = tasks[0]

        junk = copy.deepcopy(task)
        junk.args['order_id'] = 'other_order_id'
        junk.order_id = 'other_order_id'
        junk.task_id = 'junk_task1'
        junk.status = 'pending_cancel'

        grocery_invoices_db.insert_task(junk)

        junk = copy.deepcopy(task)
        junk.status = 'success'
        junk.task_id = 'junk_task2'

        grocery_invoices_db.insert_task(junk)

    return _do


@pytest.fixture(name='grocery_depots', autouse=True)
def mock_grocery_depots(grocery_depots):
    class Context:
        def add_depot(self, legacy_depot_id, **kwargs):
            grocery_depots.add_depot(
                int(legacy_depot_id),
                legacy_depot_id=legacy_depot_id,
                **kwargs,
            )

        def clear_depots(self):
            grocery_depots.clear_depots()

    context = Context()
    context.add_depot(legacy_depot_id=consts.DEPOT_ID, tin=consts.GROCERY_TIN)

    return context
