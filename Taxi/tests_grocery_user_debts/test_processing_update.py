import datetime

import pytest

from . import consts
from . import helpers
from . import models

ITEMS = [
    helpers.make_payment_items(
        [
            helpers.make_item('item-1', '100'),
            helpers.make_item('item-2', '200'),
        ],
    ),
]


@pytest.fixture(name='grocery_user_debts_update')
def _grocery_user_debts_update(taxi_grocery_user_debts):
    async def _inner(
            status_code=200, operation_type='update', debt=None, **kwargs,
    ):
        response = await taxi_grocery_user_debts.post(
            '/processing/v1/debts/update',
            json={
                'debt': debt or _make_request_debt(),
                'order': consts.ORDER_INFO,
                'operation': helpers.make_operation(operation_type),
                **kwargs,
            },
        )

        assert response.status_code == status_code

    return _inner


async def test_debt_collector(
        grocery_user_debts_update, debt_collector, default_debt,
):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)

    debt_collector.by_id.mock_response(version=1)
    debt_collector.update.check(
        id=consts.DEBT_ID,
        items_by_payment_type=helpers.to_debt_collector_items(
            request_debt['items'],
        ),
        service=consts.SERVICE,
        reason=helpers.make_reason(),
        version=1,
    )

    await grocery_user_debts_update(debt=request_debt)

    assert debt_collector.update.times_called == 1


@pytest.mark.parametrize(
    'operation_type, state',
    [('remove', 'refund_money'), ('update', 'hold_money')],
)
async def test_processing(
        grocery_user_debts_update,
        default_debt,
        processing,
        operation_type,
        state,
):
    token = f'{consts.ORDER_ID}-{state}-{consts.OPERATION_ID}-{operation_type}'

    processing.processing.check(
        order_id=consts.ORDER_ID,
        reason='setstate',
        state=state,
        payload=dict(
            operation_id=consts.OPERATION_ID, operation_type=operation_type,
        ),
        headers={'X-Idempotency-Token': token},
    )

    await grocery_user_debts_update(operation_type=operation_type)

    assert processing.processing.times_called == 1


async def test_pgsql(grocery_user_debts_update, grocery_user_debts_db):
    debt = models.Debt(debt_id=consts.DEBT_ID)
    grocery_user_debts_db.upsert(debt)

    await grocery_user_debts_update()

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.priority == consts.OPERATION_PRIORITY
    assert updated_debt.status == 'init'


async def test_no_debt(grocery_user_debts_update):
    await grocery_user_debts_update(status_code=500)


async def test_canceled(
        grocery_user_debts_update,
        grocery_user_debts_db,
        debt_collector,
        processing,
):
    grocery_user_debts_db.upsert(models.Debt(status='canceled'))

    await grocery_user_debts_update()

    assert debt_collector.update.times_called == 0
    assert processing.debts.times_called == 0


async def test_cleared(grocery_user_debts_update, grocery_user_debts_db):
    debt = models.Debt(debt_id=consts.DEBT_ID, status='cleared')
    grocery_user_debts_db.upsert(debt)

    await grocery_user_debts_update()

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.priority == consts.OPERATION_PRIORITY
    assert updated_debt.status == 'init'


@pytest.mark.parametrize('priority', [1, 2, 3])
async def test_priority(
        grocery_user_debts_update,
        grocery_user_debts_db,
        debt_collector,
        priority,
):
    debt = models.Debt(debt_id=consts.DEBT_ID, priority=2)
    grocery_user_debts_db.upsert(debt)

    early_exit = priority <= debt.priority

    await grocery_user_debts_update(
        operation=helpers.make_operation(priority=priority),
    )

    assert debt_collector.update.times_called == int(not early_exit)


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('max_delta', [10, -10, 0, 0.5, 1])
async def test_debt_strategy(
        grocery_user_debts_update, debt_collector, default_debt, max_delta,
):
    delta_threshold = 1
    time_table = [
        consts.NOW_DT + datetime.timedelta(minutes=max_delta - 20),
        consts.NOW_DT + datetime.timedelta(minutes=max_delta),
        consts.NOW_DT + datetime.timedelta(minutes=max_delta - 10),
    ]
    time_table_extra = [
        consts.NOW_DT + datetime.timedelta(minutes=delta_threshold),
    ]
    if max_delta >= delta_threshold:
        time_table_extra.clear()

    debt_collector.by_id.mock_response(
        collection=helpers.make_time_table_strategy(
            time_table, installed_at=consts.NOW,
        ),
    )
    debt_collector.update.check(
        collection=helpers.make_time_table_strategy(
            time_table + time_table_extra,
        ),
    )

    await grocery_user_debts_update()

    assert debt_collector.update.times_called == 1


async def test_resolve_conflict(
        grocery_user_debts_update, debt_collector, default_debt,
):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)

    debt_collector.by_id.mock_response(
        items_by_payment_type=helpers.to_debt_collector_items(
            request_debt['items'],
        ),
    )
    debt_collector.update.status_code = 409

    await grocery_user_debts_update()

    assert debt_collector.update.times_called == 1


async def test_to_many_updates(
        grocery_user_debts_update, debt_collector, default_debt,
):
    debt_collector.update.status_code = 400
    debt_collector.update.mock_response(message='Too many updates')

    await grocery_user_debts_update(status_code=409)

    assert debt_collector.update.times_called == 1


@pytest.mark.parametrize(
    'debt_items, expected_status',
    [
        (None, None),
        ([], 'cleared'),
        ([helpers.make_payment_items([])], 'cleared'),
        (ITEMS, 'init'),
    ],
)
async def test_update_status(
        grocery_user_debts_update,
        grocery_user_debts_db,
        default_debt,
        debt_items,
        expected_status,
):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID, items=debt_items)

    await grocery_user_debts_update(debt=request_debt)

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.status == (expected_status or default_debt.status)


def _make_request_debt(*, debt_id=consts.DEBT_ID, **kwargs):
    return {
        'debt_id': debt_id,
        'idempotency_token': consts.DEBT_IDEMPOTENCY_TOKEN,
        'items': ITEMS,
        'reason_code': consts.DEBT_REASON_CODE,
        **kwargs,
    }
