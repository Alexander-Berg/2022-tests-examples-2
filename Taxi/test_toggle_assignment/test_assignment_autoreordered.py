import copy
import datetime
import json

import pytest

from tests_plugins import utils as tp_utils

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_SURGE_TRIGGER={
        '__default__': {
            '__default__': [{'SURGE': 2.0, 'TIME_IN_BUFFER': 1000}],
        },
    },
)
@pytest.mark.now('2021-01-01T12:00:00Z')
@pytest.mark.parametrize(
    'autoreorder_created_dt, autoreorder_decision_ttl, assigned',
    [
        # No autoreoder, candidate skipped due to surge trigger
        (None, 60, 0),
        # autoreorder, surge trigger ignored
        (0, 60, 1),
        # autoreorder ignored due to autoreorder decision ttl
        (100, 60, 0),
        # autoreorder check disabled due to zero autoreorder decision ttl
        (-100, 0, 0),
    ],
)
async def test_surge_trigger_ignored_due_to_autoreorder(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        testpoint,
        taxi_config,
        now,
        autoreorder_created_dt,
        autoreorder_decision_ttl,
        assigned,
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

    order_meta = copy.deepcopy(data.ORDER_META)
    order_meta['order']['request']['surge_price'] = 2.0

    if autoreorder_created_dt is not None:
        order_meta['autoreorder'] = {
            'decisions': [
                {'created': tp_utils.timestamp(now) - autoreorder_created_dt},
            ],
        }

    taxi_config.set(
        DISPATCH_BUFFER_AUTOREORDER_DECISION_TTL=autoreorder_decision_ttl,
    )
    await taxi_dispatch_buffer.invalidate_caches()

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
    assert stats['dispatched_orders'] == assigned
