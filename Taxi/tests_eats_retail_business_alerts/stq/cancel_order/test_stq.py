import pytest

from tests_eats_retail_business_alerts import models
from tests_eats_retail_business_alerts.stq.cancel_order import constants

ORDER_NR = '1'


async def test_unknown_order_retries_limit(
        stq_runner, sql, update_taxi_config,
):
    unknown_order = '999'

    await stq_runner.eats_retail_business_alerts_cancel_order.call(
        task_id='1',
        kwargs={
            'order_nr': unknown_order,
            'cancelled_by': constants.CANCELLED_BY,
        },
    )

    max_retries_on_not_ready = 2
    update_taxi_config(
        'EATS_RETAIL_BUSINESS_ALERTS_STQ_PROCESSING',
        {
            '__default__': {
                'max_retries_on_not_ready': max_retries_on_not_ready,
            },
        },
    )

    for i in range(max_retries_on_not_ready):
        await stq_runner.eats_retail_business_alerts_cancel_order.call(
            task_id='1',
            kwargs={
                'order_nr': unknown_order,
                'cancelled_by': constants.CANCELLED_BY,
            },
            expect_fail=False,
            exec_tries=i,
        )

    # should succeed because of the retry limit
    await stq_runner.eats_retail_business_alerts_cancel_order.call(
        task_id='1',
        kwargs={
            'order_nr': unknown_order,
            'cancelled_by': constants.CANCELLED_BY,
        },
        expect_fail=False,
        exec_tries=max_retries_on_not_ready,
    )

    assert not sql.load_all(models.PlaceOrder)


@pytest.mark.pgsql('eats_retail_business_alerts', files=['init_place.sql'])
async def test_stq_error_limit(stq_runner, testpoint, update_taxi_config):
    max_retries_on_error = 2
    update_taxi_config(
        'EATS_RETAIL_BUSINESS_ALERTS_STQ_PROCESSING',
        {'__default__': {'max_retries_on_error': max_retries_on_error}},
    )

    @testpoint(
        'eats-retail-business-alerts_stq_cancel_order::failure-injector',
    )
    def task_testpoint(_):
        return {'inject': True}

    for i in range(max_retries_on_error):
        await stq_runner.eats_retail_business_alerts_cancel_order.call(
            task_id='1',
            kwargs={
                'order_nr': ORDER_NR,
                'cancelled_by': constants.CANCELLED_BY,
            },
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_retail_business_alerts_cancel_order.call(
        task_id='1',
        kwargs={'order_nr': ORDER_NR, 'cancelled_by': constants.CANCELLED_BY},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
