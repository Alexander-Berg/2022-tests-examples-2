import datetime
import json

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data

ORDER_ID = '8fa174f64a0b4d8488395bc9f652addd'


async def test_sticky_performer(
        taxi_dispatch_buffer, pgsql, mockserver, testpoint,
):
    candidates = [data.CANDIDATE]

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': candidates}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    order_meta = data.ORDER_META

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id=ORDER_ID,
        zone_id='example',
        classes='{"econom"}',
        order_lookup='ROW(0,1,3)',
        agglomeration='example_agglomeration',
        created=datetime.datetime.now(),
        dispatch_status='idle',
        order_meta=json.dumps(data.ORDER_META),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == 1

    rows = utils.select_named(pgsql, order_id=ORDER_ID)
    assert rows
    order = rows[0]
    assert order['dispatch_status'] == 'dispatched'

    dispatched_driver = order.get('dispatched_performer')
    assert dispatched_driver == data.CANDIDATE

    # Next iteration
    order_meta['lookup'] = {'generation': 0, 'version': 2, 'wave': 3}
    order_meta['order_id'] = ORDER_ID
    order_meta['order']['request'].pop('offer')
    order_meta['order']['user_id'] = 'user_id'

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'updated'

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'not found'
