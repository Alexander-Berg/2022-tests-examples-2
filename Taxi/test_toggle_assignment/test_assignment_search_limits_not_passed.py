import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
async def test_search_limits_not_passed(
        taxi_dispatch_buffer, pgsql, mockserver, testpoint,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        assert 'max_route_distance' not in request.json
        assert 'max_route_time' not in request.json
        assert 'max_distance' not in request.json
        assert 'limit' not in request.json
        return {'candidates': []}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(_):
        return {'responses': [data.SCORING_RESPONSE]}

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    order_meta = copy.deepcopy(data.ORDER_META)
    order_meta['order_id'] = '8fa174f64a0b4d8488395bc9f652addd'

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

    await assignment_stats.wait_call()
