import datetime

import pytest

from . import consts
from . import models

ACTUAL_DEBTS_DT = consts.NOW_DT - datetime.timedelta(days=1)

MARK_ACTUAL_DEBTS_DT = pytest.mark.config(
    GROCERY_USER_DEBTS_ACTUAL_DEBTS_DT=ACTUAL_DEBTS_DT.isoformat(),
)


@pytest.fixture(name='grocery_user_debts_list')
def _grocery_user_debts_list(taxi_grocery_user_debts):
    async def _inner(*, debt_ids=None, status_code=200):
        body = {}

        if debt_ids is not None:
            body['debt_ids'] = debt_ids

        response = await taxi_grocery_user_debts.post(
            '/internal/debts/v1/list', json=body,
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@MARK_ACTUAL_DEBTS_DT
async def test_exists(grocery_user_debts_list, grocery_user_debts_db):
    debt = models.Debt()
    grocery_user_debts_db.upsert(debt)

    response = await grocery_user_debts_list()

    assert response['debts'] == [
        {
            'order_id': debt.order_id,
            'debt_id': debt.debt_id,
            'debt_status': debt.status,
        },
    ]


async def test_empty(grocery_user_debts_list):
    response = await grocery_user_debts_list()

    assert not response['debts']


@MARK_ACTUAL_DEBTS_DT
@pytest.mark.parametrize('debt_status', models.DebtStatus.values)
async def test_filter_by_status(
        grocery_user_debts_list, grocery_user_debts_db, debt_status,
):
    expect = {
        models.DebtStatus.init: True,
        models.DebtStatus.canceled: False,
        models.DebtStatus.cleared: False,
        models.DebtStatus.forgiven: False,
    }
    assert debt_status in expect, 'Unknown debt_status: ' + debt_status

    grocery_user_debts_db.upsert(models.Debt(status=debt_status))

    response = await grocery_user_debts_list()
    response_debts = response['debts']

    assert len(response_debts) == int(expect[debt_status])


@MARK_ACTUAL_DEBTS_DT
async def test_filter_by_created(
        grocery_user_debts_list, grocery_user_debts_db,
):
    grocery_user_debts_db.upsert(
        models.Debt(
            debt_id='1', created=ACTUAL_DEBTS_DT - datetime.timedelta(days=1),
        ),
        models.Debt(
            debt_id='2', created=ACTUAL_DEBTS_DT + datetime.timedelta(days=1),
        ),
    )

    response = await grocery_user_debts_list()
    response_debts = response['debts']

    assert len(response_debts) == 1
    assert response_debts[0]['debt_id'] == '2'


async def test_by_debt_ids(grocery_user_debts_list, grocery_user_debts_db):
    grocery_user_debts_db.upsert(
        models.Debt(debt_id='1'),
        models.Debt(debt_id='2'),
        models.Debt(debt_id='3'),
    )

    request_debt_ids = ['1', '3']

    response = await grocery_user_debts_list(debt_ids=request_debt_ids)
    response_debt_ids = [it['debt_id'] for it in response['debts']]

    assert set(request_debt_ids) == set(response_debt_ids)
