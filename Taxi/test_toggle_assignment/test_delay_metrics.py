import datetime
import json

import pytest

from tests_dispatch_buffer import utils

AVERAGE_DELAY_NAME = 'average_delay'


@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_PERIOD_OF_ANALYSIS_OF_ORDERS_DELAYS=120,
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_delay_metrics(taxi_dispatch_buffer, pgsql, testpoint):
    @testpoint(AVERAGE_DELAY_NAME)
    def get_average_delay(data):
        return data

    await taxi_dispatch_buffer.invalidate_caches()
    assert (await get_average_delay.wait_call())['data'] == 60

    now = datetime.datetime.now()
    utils.insert_order(
        pgsql,
        id=6,
        service='taxi',
        user_id='user_id',
        order_id='good_order_1',
        zone_id='example',
        agglomeration='example_agglomeration',
        created=now - datetime.timedelta(seconds=80),
        first_dispatch_run=now - datetime.timedelta(seconds=80),
        last_dispatch_run=now,
        dispatch_status='dispatched',
        classes='{"econom"}',
        order_meta=json.dumps({}),
    )

    await taxi_dispatch_buffer.invalidate_caches()
    assert (await get_average_delay.wait_call())['data'] == 70
