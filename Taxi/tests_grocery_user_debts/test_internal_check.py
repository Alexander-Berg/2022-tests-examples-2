import pytest

from . import consts
from . import models


@pytest.fixture(name='grocery_user_debts_check')
def _grocery_user_debts_check(taxi_grocery_user_debts):
    async def _inner(order_id=consts.ORDER_ID, status_code=200):
        response = await taxi_grocery_user_debts.post(
            '/internal/debts/v1/check', json={'order_id': order_id},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_exists(grocery_user_debts_check, default_debt):
    response = await grocery_user_debts_check(order_id=default_debt.order_id)

    assert response['debt_exists']


async def test_not_exists(grocery_user_debts_check):
    response = await grocery_user_debts_check()

    assert not response['debt_exists']


@pytest.mark.parametrize('debt_status', models.DebtStatus.values)
async def test_filter_by_status(
        grocery_user_debts_check, grocery_user_debts_db, debt_status,
):
    expect = {
        models.DebtStatus.init: True,
        models.DebtStatus.canceled: False,
        models.DebtStatus.cleared: False,
        models.DebtStatus.forgiven: False,
    }
    assert debt_status in expect, 'Unknown debt_status: ' + debt_status

    grocery_user_debts_db.upsert(
        models.Debt(status=debt_status, order_id=consts.ORDER_ID),
    )

    response = await grocery_user_debts_check()

    assert response['debt_exists'] == expect[debt_status]
