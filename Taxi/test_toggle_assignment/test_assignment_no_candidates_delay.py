import datetime

import pytest

from tests_dispatch_buffer import utils


@pytest.mark.now('2020-03-16T17:10:35+0300')
@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize('order_search_response_code', [200, 500])
async def test_assignment_no_candidates_delay(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        testpoint,
        mocked_time,
        order_search_response_code,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        if order_search_response_code == 200:
            return {'candidates': []}
        return mockserver.make_response(
            'fail', status=order_search_response_code,
        )

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 2
    assert stats['dispatched_orders'] == 0

    expectations = {
        'order_id_1': {'draw_cnt': 0},
        'order_id_2': {'draw_cnt': 3, 'draw_cnt_no_candidates': 8},
        'order_id_3': {'draw_cnt': 3, 'draw_cnt_no_candidates': 13},
    }
    if order_search_response_code == 200:
        expectations['order_id_2'][
            'next_dispatch_run'
        ] = mocked_time.now() + datetime.timedelta(seconds=5)
        expectations['order_id_3'][
            'next_dispatch_run'
        ] = mocked_time.now() + datetime.timedelta(seconds=10)

    for order_id, fields in expectations.items():
        rows = utils.select_named(pgsql, order_id=order_id)
        assert rows
        order = rows[0]
        for field_name, value in fields.items():
            if isinstance(order[field_name], datetime.datetime):
                assert (
                    order[field_name]
                    .astimezone(datetime.timezone.utc)
                    .replace(tzinfo=None)
                    == value
                )
            else:
                assert order[field_name] == value
