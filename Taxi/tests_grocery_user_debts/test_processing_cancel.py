import pytest

from . import consts
from . import helpers
from . import models


@pytest.fixture(name='grocery_user_debts_cancel')
def _grocery_user_debts_cancel(taxi_grocery_user_debts):
    async def _inner(status_code=200, debt=None, **kwargs):
        response = await taxi_grocery_user_debts.post(
            '/processing/v1/debts/cancel',
            json={
                'debt': debt or _make_request_debt(),
                'order': consts.ORDER_INFO,
                **kwargs,
            },
        )

        assert response.status_code == status_code

    return _inner


async def test_debt_collector(
        grocery_user_debts_cancel, debt_collector, default_debt,
):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)

    debt_collector.by_id.mock_response(version=1)
    debt_collector.pay.check(
        id=consts.DEBT_ID,
        items_by_payment_type=helpers.to_debt_collector_items([]),
        service=consts.SERVICE,
        reason=helpers.make_reason(),
        version=1,
    )

    await grocery_user_debts_cancel(debt=request_debt)
    assert debt_collector.update.times_called == 1


async def test_pgsql(grocery_user_debts_cancel, grocery_user_debts_db):
    debt = models.Debt(debt_id=consts.DEBT_ID)
    grocery_user_debts_db.upsert(debt)

    await grocery_user_debts_cancel()

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.status == 'canceled'
    assert updated_debt.priority == debt.priority


async def test_no_debt(grocery_user_debts_cancel, grocery_user_debts_db):
    await grocery_user_debts_cancel(status_code=404)

    debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert debt.status == 'canceled'


async def test_canceled(
        grocery_user_debts_cancel, grocery_user_debts_db, debt_collector,
):
    grocery_user_debts_db.upsert(models.Debt(status='canceled'))

    await grocery_user_debts_cancel()
    assert debt_collector.update.times_called == 0


def _make_request_debt(*, debt_id=consts.DEBT_ID):
    return {
        'debt_id': debt_id,
        'idempotency_token': consts.DEBT_IDEMPOTENCY_TOKEN,
        'reason_code': consts.DEBT_REASON_CODE,
    }
