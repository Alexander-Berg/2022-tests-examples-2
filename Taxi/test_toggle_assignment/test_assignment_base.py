import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


def get_order_meta_na_minimalkah():
    order_meta = copy.deepcopy(data.ORDER_META)
    order_meta['order']['request'].pop('offer')
    order_meta.pop('destination')
    return order_meta


@pytest.mark.parametrize(
    'order_meta', [data.ORDER_META, get_order_meta_na_minimalkah()],
)
async def test_base_assignment(
        taxi_dispatch_buffer, pgsql, mockserver, testpoint, order_meta,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=datetime.datetime.now(),
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == 1

    rows = utils.select_named(
        pgsql, order_id='8fa174f64a0b4d8488395bc9f652addd',
    )
    assert rows
    order = rows[0]
    assert order['dispatch_status'] == 'dispatched'

    dispatched_driver = order.get('dispatched_performer')
    assert dispatched_driver == data.CANDIDATE


async def test_toggle_assignment_no_orders(taxi_dispatch_buffer, testpoint):
    @testpoint('no_orders')
    def no_orders(_):
        pass

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    await no_orders.wait_call()


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
@pytest.mark.parametrize('wrong_status', ['dispatched', 'removed'])
async def test_wrong_status(
        taxi_dispatch_buffer, pgsql, testpoint, wrong_status,
):
    @testpoint('no_orders')
    def no_orders(_):
        pass

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        created=datetime.datetime.now(),
        dispatch_status=wrong_status,
        order_meta='{}',
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    await no_orders.wait_call()
