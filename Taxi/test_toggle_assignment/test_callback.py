import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data

# Generated via `tvmknife unittest service -s 777 -d 2345`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIiQYQqRI:Iexh7KU4lzSbAba'
    '-KJfaPT24hdcWepDmur_AORaT_DZlZvqIi3ITj5t1-POGmLmFrG'
    'oykoa1j2h9MH_VrGTYc5s4TSbwBlUbOhFXJT6FGBDbag1yBpudu'
    '5zX6MiAPlX4uQc1aMGN-1YKl8caAbq8kW7C5-QAgGGfffgAyJL_XfE'
)


def milliseconds_from_time(raw_str: str) -> int:
    delta = datetime.datetime.strptime(
        raw_str, '%H:%M:%S.%f',
    ) - datetime.datetime(1900, 1, 1)
    return int(delta.total_seconds() * 1000)


def assert_callback(db_callback_raw: str, new_callback):
    db_callback = db_callback_raw[1:-1].split(',')  # '(url,'00:00:00.3',1)'
    assert db_callback[0] == new_callback['url']
    assert milliseconds_from_time(db_callback[1]) == new_callback['timeout_ms']
    assert int(db_callback[2]) == new_callback['attempts']


def serialize_callback_to_pg(callback: dict) -> str:
    return (
        f'(\'{callback["url"]}\','
        f'\'{callback["timeout_ms"]} milliseconds\'::interval,'
        f'{callback["attempts"]})'
    )


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False, TVM_ENABLED=True)
@pytest.mark.parametrize('update_callback', [True, False])
async def test_event_status_false(
        taxi_dispatch_buffer, pgsql, mockserver, testpoint, update_callback,
):
    callback_url = mockserver.url(
        'lookup/event?order_id=8fa174f64a0b4d8488395bc9f652addd&version=',
    )
    old_callback = {
        'url': callback_url + '1',
        'timeout_ms': 200,
        'attempts': 2,
    }
    new_callback = {
        'url': callback_url + '2',
        'timeout_ms': 300,
        'attempts': 1,
    }

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @mockserver.json_handler('/lookup/event')
    def _mock_lookup_event(request):
        body = json.loads(request.get_data())
        assert request.headers['Content-Type'] == 'application/json'
        assert (
            request.headers['X-Ya-Service-Ticket']
            == '666_ticket_not_set_in_testsuite'
        )
        assert body.get('status') == 'found'
        assert body.get('candidate') == data.CANDIDATE

        response = {'success': False}
        if update_callback:
            response.update({'callback': new_callback})

        return response

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
        callback=serialize_callback_to_pg(old_callback),
        order_meta=json.dumps(data.ORDER_META),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == 0

    rows = utils.select_named(
        pgsql, order_id='8fa174f64a0b4d8488395bc9f652addd',
    )
    assert rows
    order = rows[0]
    assert order['dispatch_status'] == 'idle'  # rescheduled
    if update_callback:
        assert_callback(order['callback'], new_callback)
    else:
        assert_callback(order['callback'], old_callback)


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
async def test_event_status_true(
        taxi_dispatch_buffer, pgsql, mockserver, testpoint,
):
    callback_url = mockserver.url(
        'lookup/event?order_id=8fa174f64a0b4d8488395bc9f652addd&version=',
    )
    callback = {'url': callback_url + '1', 'timeout_ms': 200, 'attempts': 2}

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @mockserver.json_handler('/lookup/event')
    def _mock_lookup_event(request):
        body = json.loads(request.get_data())
        assert body.get('status') == 'found'
        assert body.get('candidate') == data.CANDIDATE

        return {'success': True, 'callback': callback}

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
        callback=serialize_callback_to_pg(callback),
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
    dispatched_driver = order.get('dispatched_performer')

    assert order['dispatch_status'] == 'dispatched'  # rescheduled
    assert_callback(order['callback'], callback)
    assert dispatched_driver == data.CANDIDATE


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
async def test_not_use_callback_in_background(
        taxi_dispatch_buffer, pgsql, mockserver, testpoint, experiments3,
):
    experiments3.add_config(
        **utils.agglomeration_settings(
            'example_agglomeration',
            {
                'APPLY_ALGORITHM': 'hungarian',
                'APPLY_RESULTS': False,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 60,
                'ORDERS_LIMIT': 0,
                'RUNNING_INTERVAL': 60,
            },
        ),
    )

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
        order_meta=json.dumps(data.ORDER_META),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == 1
    assert stats['dispatched_orders'] == 1
