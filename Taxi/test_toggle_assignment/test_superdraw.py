import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


@pytest.mark.parametrize('is_superdraw_in_progress', [False, True])
async def test_superdraw(
        taxi_dispatch_buffer,
        experiments3,
        pgsql,
        mockserver,
        testpoint,
        is_superdraw_in_progress,
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

    experiments3.add_config(
        name='dispatch_buffer_superdraw_settings',
        consumers=['dispatch_buffer/superdraw_settings'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'enabled': is_superdraw_in_progress},
    )

    await taxi_dispatch_buffer.invalidate_caches(clean_update=True)
    utils.clear_db(pgsql)
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
        order_meta=json.dumps(data.ORDER_META),
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
    if not is_superdraw_in_progress:
        assert order['dispatch_status'] == 'dispatched'
    else:
        assert order['dispatch_status'] == 'idle'
