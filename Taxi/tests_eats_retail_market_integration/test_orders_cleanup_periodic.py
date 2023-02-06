import pytest

PERIODIC_NAME = 'orders-cleanup-periodic'


@pytest.mark.parametrize(
    'orders_threshold, expected_orders',
    [
        (10, ['1', '2', '3', '4', '5', '6', '7', '8', '9']),
        (3, ['1', '2', '3', '7', '8', '9']),
        (1, ['1', '7', '9']),
    ],
)
@pytest.mark.pgsql('eats_retail_market_integration', files=['fill_orders.sql'])
async def test_orders_cleanup(
        taxi_eats_retail_market_integration,
        pgsql,
        taxi_config,
        testpoint,
        orders_threshold,
        expected_orders,
):
    taxi_config.set_values(
        {
            'EATS_RETAIL_MARKET_INTEGRATION_ORDERS_CLEANUP': {
                'orders_threshold': orders_threshold,
            },
            'EATS_RETAIL_MARKET_INTEGRATION_PERIODICS': {
                PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 60},
            },
        },
    )

    @testpoint('orders-cleanup-periodic-finished')
    def task_testpoint(param):
        pass

    await taxi_eats_retail_market_integration.run_distlock_task(PERIODIC_NAME)
    assert task_testpoint.times_called == 1

    assert _sql_get_orders(pgsql) == expected_orders


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _sql_get_orders(pgsql):
    cursor = pgsql['eats_retail_market_integration'].cursor()
    cursor.execute(
        """
        select order_nr
        from eats_retail_market_integration.orders
        order by order_nr
        """,
    )
    return [row[0] for row in list(cursor)]
