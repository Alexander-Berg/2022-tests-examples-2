# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers

from . import models

SENSOR_ERROR = 'grocery_payments_billing_error_metrics'


async def test_billing_tlog_callback(
        grocery_orders,
        grocery_cart,
        run_grocery_payments_billing_tlog_callback,
        taxi_grocery_payments_billing_monitor,
):

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_billing_monitor, sensor=SENSOR_ERROR,
    ) as collector:
        await run_grocery_payments_billing_tlog_callback(expect_fail=True)

    metric = collector.get_single_collected_metric()

    assert metric.labels == {
        'sensor': SENSOR_ERROR,
        'error_code': 'depot_not_found',
        'country': models.Country.Russia.name,
    }


async def test_billing_eats_orders(
        grocery_orders,
        grocery_cart,
        run_grocery_payments_billing_eats_orders,
        taxi_grocery_payments_billing_monitor,
):

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_billing_monitor, sensor=SENSOR_ERROR,
    ) as collector:
        await run_grocery_payments_billing_eats_orders(expect_fail=True)

    metric = collector.get_single_collected_metric()

    assert metric.labels == {
        'sensor': SENSOR_ERROR,
        'error_code': 'empty_items_list',
        'country': models.Country.Russia.name,
    }
