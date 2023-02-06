import pytest

from . import consts
from . import helpers
from . import models


IDEMPOTENCY_TOKEN = 'idempotency_token'
STRATEGY = dict(type='null')
REASON_CODE = 'update_pay_strategy'


@pytest.fixture(name='grocery_user_debts_pay_strategy')
def _grocery_user_debts_pay_strategy(taxi_grocery_user_debts):
    async def _inner(status_code=200, **kwargs):
        response = await taxi_grocery_user_debts.post(
            '/internal/debts/v1/set-pay-strategy',
            json={
                'order_id': consts.ORDER_ID,
                'debt_id': consts.DEBT_ID,
                'idempotency_token': IDEMPOTENCY_TOKEN,
                'strategy': STRATEGY,
                **kwargs,
            },
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_debt_collector(
        grocery_user_debts_pay_strategy, debt_collector, default_debt,
):
    debt_collector.by_id.mock_response(version=1)
    debt_collector.update.check(
        id=consts.DEBT_ID,
        service=consts.SERVICE,
        reason=helpers.make_reason(REASON_CODE),
        collection=dict(strategy=consts.DEBT_NULL_STRATEGY),
        version=1,
    )

    await grocery_user_debts_pay_strategy()
    assert debt_collector.update.times_called == 1


async def test_no_debt(grocery_user_debts_pay_strategy):
    await grocery_user_debts_pay_strategy(status_code=404)


async def test_no_debt_in_debt_collector(
        grocery_user_debts_pay_strategy, debt_collector, default_debt,
):
    debt_collector.by_id.response = None

    await grocery_user_debts_pay_strategy(status_code=404)


async def test_canceled(
        grocery_user_debts_pay_strategy, grocery_user_debts_db,
):
    grocery_user_debts_db.upsert(models.Debt(status='canceled'))

    await grocery_user_debts_pay_strategy()
