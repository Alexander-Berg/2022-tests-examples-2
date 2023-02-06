import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_ENABLED_REGISTERING_PIN=True,
    DISPATCH_BUFFER_PIN_TTL={'example_agglomeration': 200},
    DELAYED_SECONDS_TO_DUE_TO_START_LOOKUP=1,
)
async def test_skip_offer(
        taxi_dispatch_buffer, pgsql, mockserver, mocked_time, testpoint,
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
    created = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    due = created + datetime.timedelta(minutes=9)
    order_meta['order']['request']['due'] = due.timestamp()
    order_meta['order']['created'] = created.timestamp()

    mocked_time.set(created)
    await taxi_dispatch_buffer.invalidate_caches()

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        offer_id='offer_f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=created,
        due=due,
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )
    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == 0
