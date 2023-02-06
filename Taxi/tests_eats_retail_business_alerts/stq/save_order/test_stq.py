import pytest

from tests_eats_retail_business_alerts import models
from tests_eats_retail_business_alerts.stq.save_order import constants

ORDER_NR = '1'


async def test_unknown_place(stq_runner, sql):
    brand_id = sql.save(models.Brand())
    region_id = sql.save(models.Region())
    unknown_place = models.Place(brand_id=brand_id, region_id=region_id)

    await stq_runner.eats_retail_business_alerts_save_order.call(
        task_id='1',
        kwargs={'place_id': unknown_place.place_id, 'order_nr': ORDER_NR},
    )

    assert not sql.load_all(models.PlaceOrder)


@pytest.mark.pgsql('eats_retail_business_alerts', files=['init_place.sql'])
async def test_stq_error_limit(stq_runner, testpoint, update_taxi_config):
    max_retries_on_error = 2
    update_taxi_config(
        'EATS_RETAIL_BUSINESS_ALERTS_STQ_PROCESSING',
        {'__default__': {'max_retries_on_error': max_retries_on_error}},
    )

    @testpoint('eats-retail-business-alerts_stq_save_order::failure-injector')
    def task_testpoint(_):
        return {'inject': True}

    for i in range(max_retries_on_error):
        await stq_runner.eats_retail_business_alerts_save_order.call(
            task_id='1',
            kwargs={'place_id': constants.PLACE_ID, 'order_nr': ORDER_NR},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_retail_business_alerts_save_order.call(
        task_id='1',
        kwargs={'place_id': constants.PLACE_ID, 'order_nr': ORDER_NR},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls
