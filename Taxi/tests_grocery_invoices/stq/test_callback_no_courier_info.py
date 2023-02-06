import copy
import datetime

import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models
from tests_grocery_invoices import pytest_marks

TWO_DAYS_AGO_DT = consts.NOW_DT - datetime.timedelta(days=2)
COUNTRY = models.Country.Russia

RECEIPT_PRODUCT_ITEMS = helpers.make_product_receipt(COUNTRY)
RECEIPT_DELIVERY_ITEMS = helpers.make_delivery_receipt(COUNTRY)
RECEIPT_TIPS_ITEMS = helpers.make_tips_receipt(COUNTRY)
RECEIPT_ITEMS = [
    *RECEIPT_PRODUCT_ITEMS,
    *RECEIPT_DELIVERY_ITEMS,
    *RECEIPT_TIPS_ITEMS,
]
CART_ITEMS = helpers.make_cart_items(COUNTRY)


def _create_receipt_pg_task(
        task_id, receipt_type, status, items, created=consts.NOW_DT,
):
    return helpers.create_receipt_pg_task(
        task_id=task_id,
        task_type='invoice_callback',
        receipt_type=receipt_type,
        status=status,
        created=created,
        items=items,
    )


@pytest.fixture
def _run_stq(run_grocery_invoices_callback):
    async def _do(items=None, **kwargs):
        items = items or RECEIPT_ITEMS

        await run_grocery_invoices_callback(
            items=models.items_to_json(items), **kwargs,
        )

    return _do


@pytest.fixture
def _run_test(
        run_grocery_invoices_callback,
        grocery_cart,
        grocery_orders,
        prepare_no_courier_tasks,
        _run_stq,
):
    async def _inner(
            task_id,
            tasks,
            expect_fail=False,
            order_status=None,
            prepare_cart=True,
    ):
        prepare_no_courier_tasks(tasks)

        if prepare_cart:
            grocery_cart.set_cart_data(cart_id=consts.CART_ID)
            grocery_cart.set_items_v2(CART_ITEMS)

        if order_status is not None:
            grocery_orders.order.update(status=order_status)

        grocery_orders.order.update(courier_info=None)

        await _run_stq(task_id=task_id, expect_fail=expect_fail)

    return _inner


# Проверяем условия перехода чека из статуса failed -> pending_cancel
# Для такого перехода (failed -> pending_cancel) одним из условий
# является факт того, что все остальные чеки
# по заказу находятся в статусах (failed|pending_cancel|canceled)
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'paired_task_status, expected_status, reschedule',
    [
        ('failed', 'pending_cancel', True),
        ('pending_cancel', 'pending_cancel', True),
        ('canceled', 'pending_cancel', True),
        ('in_process', 'failed', False),
    ],
)
async def test_failed_with_other_statuses(
        grocery_invoices_db,
        _run_test,
        stq,
        paired_task_status,
        expected_status,
        reschedule,
):
    payment = _create_receipt_pg_task(
        task_id=consts.TASK_ID,
        receipt_type='payment',
        status='failed',
        created=TWO_DAYS_AGO_DT,
        items=RECEIPT_ITEMS,
    )

    refund = _create_receipt_pg_task(
        task_id=consts.PAIRED_TASK_ID,
        receipt_type='refund',
        status=paired_task_status,
        items=RECEIPT_ITEMS,
    )

    await _run_test(
        task_id=payment.task_id,
        tasks=[payment, refund],
        expect_fail=(not reschedule),
        order_status='canceled',
    )

    assert stq.grocery_invoices_callback.times_called == int(reschedule)

    db_task = grocery_invoices_db.load_task(payment.task_id)

    assert db_task.status == expected_status


# Одним из условий перехода failed -> pending_cancel
# является - сумма всех чеков (поэлементно) должна давать 0
# assert (payment - refund) == 0
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'refund_tasks',
    [
        [{'status': 'failed', 'items': RECEIPT_ITEMS}],
        [{'status': 'pending_cancel', 'items': RECEIPT_ITEMS}],
        [{'status': 'canceled', 'items': RECEIPT_ITEMS}],
        [
            {'status': 'failed', 'items': RECEIPT_PRODUCT_ITEMS},
            {'status': 'pending_cancel', 'items': RECEIPT_DELIVERY_ITEMS},
            {'status': 'canceled', 'items': RECEIPT_TIPS_ITEMS},
        ],
    ],
)
@pytest.mark.parametrize(
    'extra_task, expected_status',
    [(True, 'failed'), (False, 'pending_cancel')],
)
async def test_failed_tasks_sum(
        grocery_invoices_db,
        _run_test,
        stq,
        refund_tasks,
        extra_task,
        expected_status,
):
    payment = _create_receipt_pg_task(
        task_id=consts.TASK_ID,
        receipt_type='payment',
        status='failed',
        created=TWO_DAYS_AGO_DT,
        items=RECEIPT_ITEMS,
    )

    tasks = [payment]

    for refund_task in refund_tasks:
        tasks.append(
            _create_receipt_pg_task(
                task_id=consts.PAIRED_TASK_ID + str(len(tasks)),
                receipt_type='refund',
                status=refund_task['status'],
                items=refund_task['items'],
            ),
        )

    if extra_task:
        extra = copy.deepcopy(payment)
        extra.task_id = consts.TASK_ID + 'extra'
        tasks.append(extra)

    await _run_test(
        task_id=payment.task_id,
        tasks=tasks,
        expect_fail=extra_task,
        order_status='canceled',
    )

    assert stq.grocery_invoices_callback.times_called == int(not extra_task)

    db_task = grocery_invoices_db.load_task(payment.task_id)

    assert db_task.status == expected_status


# Одним из условий перехода failed -> pending_cancel
# является факт, что заказа отменен
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'paired_task_status', ['failed', 'pending_cancel', 'canceled'],
)
@pytest.mark.parametrize(
    'order_status, expected_status, reschedule',
    [('closed', 'failed', False), ('canceled', 'pending_cancel', True)],
)
async def test_order_not_canceled(
        grocery_invoices_db,
        _run_test,
        stq,
        paired_task_status,
        order_status,
        expected_status,
        reschedule,
):
    payment = _create_receipt_pg_task(
        task_id=consts.TASK_ID,
        receipt_type='payment',
        status='failed',
        created=TWO_DAYS_AGO_DT,
        items=RECEIPT_ITEMS,
    )

    refund = _create_receipt_pg_task(
        task_id=consts.PAIRED_TASK_ID,
        receipt_type='refund',
        status=paired_task_status,
        items=RECEIPT_ITEMS,
    )

    await _run_test(
        task_id=payment.task_id,
        tasks=[payment, refund],
        order_status=order_status,
        expect_fail=(not reschedule),
    )

    assert stq.grocery_invoices_callback.times_called == int(reschedule)

    db_task = grocery_invoices_db.load_task(payment.task_id)

    assert db_task.status == expected_status


# Одним из условий перехода failed -> pending_cancel
# является время ожидания чека
# (grocery_receipts_polling_policy.error_after_seconds)
# смотри значение POLICY_ERROR_AFTER_SECONDS
@pytest_marks.MARK_NOW
@pytest.mark.parametrize('paired_task_status', ['failed', 'pending_cancel'])
@pytest.mark.parametrize(
    'task_created, expected_status, reschedule',
    [
        (TWO_DAYS_AGO_DT, 'pending_cancel', True),
        (consts.NOW_DT, 'failed', False),
    ],
)
async def test_task_not_old_enough(
        grocery_invoices_db,
        _run_test,
        stq,
        paired_task_status,
        task_created,
        expected_status,
        reschedule,
):
    payment = _create_receipt_pg_task(
        task_id=consts.TASK_ID,
        receipt_type='payment',
        status='failed',
        items=RECEIPT_ITEMS,
        created=task_created,
    )

    refund = _create_receipt_pg_task(
        task_id=consts.PAIRED_TASK_ID,
        receipt_type='refund',
        status=paired_task_status,
        items=RECEIPT_ITEMS,
    )

    await _run_test(
        task_id=payment.task_id,
        tasks=[payment, refund],
        expect_fail=(not reschedule),
        order_status='canceled',
    )

    assert stq.grocery_invoices_callback.times_called == int(reschedule)

    db_task = grocery_invoices_db.load_task(payment.task_id)

    assert db_task.status == expected_status


# Тестируем переход из статуса pending_cancel -> canceled
# Для такого перехода (pending_cancel -> canceled) одним из условий
# является факт того, что все остальные чеки
# по заказу находятся в статусах (pending_cancel|canceled)
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'paired_task_status, expected_status, reschedule',
    [
        ('failed', 'pending_cancel', True),
        ('in_process', 'pending_cancel', True),
        ('pending_cancel', 'canceled', False),
        ('canceled', 'canceled', False),
    ],
)
async def test_pending_cancel_with_other_statuses(
        grocery_invoices_db,
        _run_test,
        stq,
        paired_task_status,
        expected_status,
        reschedule,
):
    payment = _create_receipt_pg_task(
        task_id=consts.TASK_ID,
        receipt_type='payment',
        status='pending_cancel',
        created=TWO_DAYS_AGO_DT,
        items=RECEIPT_ITEMS,
    )

    refund = _create_receipt_pg_task(
        task_id=consts.PAIRED_TASK_ID,
        receipt_type='refund',
        status=paired_task_status,
        items=RECEIPT_ITEMS,
    )

    await _run_test(
        task_id=payment.task_id, tasks=[payment, refund], prepare_cart=False,
    )

    assert stq.grocery_invoices_callback.times_called == int(reschedule)

    db_task = grocery_invoices_db.load_task(payment.task_id)

    assert db_task.status == expected_status


# Одним из условий перехода pending_cancel -> canceled
# является - сумма всех чеков (поэлементно) должна давать 0
# assert (payment - refund) == 0
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'refund_tasks',
    [
        [{'status': 'pending_cancel', 'items': RECEIPT_ITEMS}],
        [{'status': 'canceled', 'items': RECEIPT_ITEMS}],
        [
            {'status': 'pending_cancel', 'items': RECEIPT_PRODUCT_ITEMS},
            {
                'status': 'canceled',
                'items': [*RECEIPT_DELIVERY_ITEMS, *RECEIPT_TIPS_ITEMS],
            },
        ],
    ],
)
@pytest.mark.parametrize(
    'extra_task, expected_status',
    [(True, 'pending_cancel'), (False, 'canceled')],
)
async def test_pending_cancel_tasks_sum(
        grocery_invoices_db,
        _run_test,
        stq,
        refund_tasks,
        extra_task,
        expected_status,
):
    payment = _create_receipt_pg_task(
        task_id=consts.TASK_ID,
        receipt_type='payment',
        status='pending_cancel',
        created=TWO_DAYS_AGO_DT,
        items=RECEIPT_ITEMS,
    )

    tasks = [payment]

    for refund_task in refund_tasks:
        tasks.append(
            _create_receipt_pg_task(
                task_id=consts.PAIRED_TASK_ID + str(len(tasks)),
                receipt_type='refund',
                status=refund_task['status'],
                items=refund_task['items'],
            ),
        )

    if extra_task:
        extra = copy.deepcopy(payment)
        extra.task_id = consts.TASK_ID + 'extra'
        tasks.append(extra)

    await _run_test(task_id=payment.task_id, tasks=tasks, prepare_cart=False)

    assert stq.grocery_invoices_callback.times_called == int(extra_task)

    db_task = grocery_invoices_db.load_task(payment.task_id)

    assert db_task.status == expected_status
