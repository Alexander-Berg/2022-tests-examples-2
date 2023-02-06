import datetime
import json

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


async def test_version_changed(taxi_dispatch_buffer, pgsql, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(_):
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    async def _mock_driver_scoring_bulk(_):
        order_meta = data.ORDER_META
        order_meta['order_id'] = '8fa174f64a0b4d8488395bc9f652addd'
        order_meta['order']['user_id'] = 'user_id'
        order_meta['lookup'] = {'generation': 0, 'version': 1, 'wave': 4}

        # Need to update order during dispatch task
        response = await taxi_dispatch_buffer.post(
            'performer-for-order', json=order_meta,
        )
        assert response.status_code == 200
        resp_json = response.json()
        assert resp_json['message'] == 'updated'

        return mockserver.make_response('expected fail', status=500)

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        offer_id='offer_f64a0b4d8488395bc9f652addd',
        agglomeration='example_agglomeration',
        zone_id='example',
        classes='{"econom"}',
        order_lookup='ROW(0,1,3)',
        created=datetime.datetime.now(),
        dispatch_status='idle',
        order_meta=json.dumps(data.ORDER_META),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    assert _mock_driver_scoring_bulk.has_calls

    rows = utils.select_named(
        pgsql, order_id='8fa174f64a0b4d8488395bc9f652addd',
    )
    assert rows[0]['draw_cnt'] == 1
    assert rows[0]['dispatch_status'] == 'idle'
    assert rows[0]['version'] == 1
