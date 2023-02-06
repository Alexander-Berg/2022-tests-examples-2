# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import models


@pytest.fixture(name='grocery_user_debts_setstatus')
def _grocery_user_debts_setstatus(taxi_grocery_user_debts):
    async def _inner(
            status_code=200, debt_id=consts.DEBT_ID, status='cleared',
    ):
        response = await taxi_grocery_user_debts.post(
            '/processing/v1/debts/set-status',
            json={
                'debt': _make_request_debt(debt_id=debt_id, status=status),
                'order': consts.ORDER_INFO,
            },
        )

        assert response.status_code == status_code

    return _inner


async def test_pgsql(
        grocery_user_debts_setstatus, grocery_user_debts_db, default_debt,
):
    await grocery_user_debts_setstatus(status='cleared')

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.status == 'cleared'


async def test_no_debt(grocery_user_debts_setstatus):
    await grocery_user_debts_setstatus(status_code=404)


async def test_canceled(
        grocery_user_debts_setstatus, grocery_user_debts_db, debt_collector,
):
    grocery_user_debts_db.upsert(models.Debt(status='canceled'))

    await grocery_user_debts_setstatus()

    assert debt_collector.pay.times_called == 0


async def test_metric_cleared(
        grocery_user_debts_setstatus,
        taxi_grocery_user_debts_monitor,
        default_debt,
):
    sensor = 'grocery_user_debts_cleared_metrics'

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_user_debts_monitor, sensor=sensor,
    ) as collector:
        await grocery_user_debts_setstatus(status='cleared')

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'originator': models.InvoiceOriginator.grocery.name,
        'country': consts.COUNTRY,
    }


def _make_request_debt(*, debt_id, status):
    return {'debt_id': debt_id, 'status': status}
