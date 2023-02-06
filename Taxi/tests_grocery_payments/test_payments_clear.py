import datetime

import pytest

from . import consts
from . import models
from . import pytest_marks


COUNTRY = models.Country.Russia


@pytest.fixture(name='grocery_payments_clear')
def _grocery_payments_cancel(taxi_grocery_payments):
    async def _inner(country=COUNTRY, **kwargs):
        return await taxi_grocery_payments.post(
            '/payments/v1/clear',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                **kwargs,
            },
        )

    return _inner


@pytest.mark.now(consts.NOW)
async def test_basic(grocery_payments_clear, transactions):
    transactions.clear.check(id=consts.ORDER_ID, clear_eta=consts.NOW)

    response = await grocery_payments_clear()
    assert response.status_code == 200

    assert transactions.clear.times_called == 1

    assert response.json() == {}


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_clear, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.clear.check(id=invoice_id)

    response = await grocery_payments_clear(originator=originator.request_name)
    assert response.status_code == 200

    assert transactions.clear.times_called == 1

    assert response.json() == {}


@pytest.mark.parametrize('status_code', [404, 409, 500])
async def test_clear_errors(grocery_payments_clear, transactions, status_code):
    transactions.clear.status_code = status_code

    response = await grocery_payments_clear()
    assert response.status_code == status_code

    assert transactions.clear.times_called == 1


@pytest_marks.INVOICE_ORIGINATORS
async def test_debt_clear(
        grocery_payments_clear, transactions, grocery_user_debts, originator,
):
    invoice_id = originator.prefix + consts.ORDER_ID

    grocery_user_debts.clear.check(
        debt=dict(
            debt_id=invoice_id, idempotency_token='clear', reason_code='clear',
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
    )

    response = await grocery_payments_clear(originator=originator.request_name)
    assert response.status_code == 200

    assert grocery_user_debts.clear.times_called == 1


async def test_debt_after_error(
        grocery_payments_clear, transactions, grocery_user_debts,
):
    transactions.clear.status_code = 404

    response = await grocery_payments_clear()
    assert response.status_code == 404

    assert grocery_user_debts.clear.times_called == 0


@pytest.mark.now(consts.NOW)
async def test_deferred(
        grocery_payments_clear, grocery_payments_configs, transactions,
):
    delta_minutes = 5
    clear_eta = consts.NOW_DT + datetime.timedelta(minutes=delta_minutes)

    grocery_payments_configs.deferred_invoice_clear(delta_minutes)

    transactions.clear.check(clear_eta=clear_eta.isoformat())

    response = await grocery_payments_clear()
    assert response.status_code == 200

    assert transactions.clear.times_called == 1
