import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


def create_order_meta(order_id, user_id, lookup_ttl):
    result = copy.deepcopy(data.ORDER_META)
    result['order_id'] = order_id
    result['order']['user_id'] = user_id
    result['dispatch_check_in'] = {
        'check_in_time': 1628790759.429515593,
        'pickup_line': 'pickup_line_0',
    }
    result['order']['request']['lookup_ttl'] = lookup_ttl
    return result


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_ENABLED_REGISTERING_PIN=True,
    DISPATCH_BUFFER_PIN_TTL={'example_agglomeration': 200},
    DELAYED_SECONDS_TO_DUE_TO_START_LOOKUP=22 * 60,
)
async def test_skip_offer(taxi_dispatch_buffer, pgsql, mockserver, testpoint):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @testpoint('no_orders')
    def no_orders(_):
        pass

    order_meta = data.ORDER_META.copy()
    due = datetime.datetime.now() + datetime.timedelta(minutes=20)
    order_meta['order']['request']['due'] = due.timestamp()
    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id_1',
        offer_id='offer_f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=datetime.datetime.now(),
        due=due,
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )
    order_meta = data.ORDER_META.copy()
    created = datetime.datetime.now() - datetime.timedelta(minutes=2)
    order_meta['order']['created'] = created.timestamp()
    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id_2',
        offer_id='offer_f64a0b4d8488395bc9f652adde',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=created,
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    await no_orders.wait_call()


@pytest.mark.now('2021-08-12T17:53:39+0000')
@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=False,
    DISPATCH_BUFFER_AGGLOMERATIONS={
        'domodedovo_check_in': ['moscow', 'himki'],
    },
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'pickup_line_0': {
            'enabled': True,
            'terminal_id': 'terminal_C',
            'allowed_tariffs': ['econom'],
            'pickup_points': [],
        },
    },
)
@pytest.mark.parametrize(
    'lookup_ttl_enabled, fetched_orders', [(True, 1), (False, 0)],
)
async def test_skip_staled_check_in(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        taxi_config,
        lookup_ttl_enabled,
        fetched_orders,
        experiments3,
):
    taxi_config.set(LOOKUP_ENABLE_LOOKUP_TTL_FOR_STALE=lookup_ttl_enabled)
    experiments3.add_config(
        **utils.agglomeration_settings(
            'domodedovo_check_in',
            {
                'ALGORITHMS': ['hungarian'],
                'APPLY_ALGORITHM': 'hungarian',
                'APPLY_RESULTS': True,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 0,
                'ORDERS_LIMIT': 1000,
                'RUNNING_INTERVAL': 2,
                'TERMINALS': ['terminal_C'],
            },
        ),
    )

    orders = [
        {'order_id': 'order_id_1', 'lookup_ttl': 0},
        {'order_id': 'order_id_2', 'lookup_ttl': 60},
    ]
    for order in orders:
        utils.insert_order(
            pgsql,
            service='check_in',
            user_id='user_id',
            order_id=order['order_id'],
            zone_id='example',
            classes='{"econom"}',
            agglomeration='domodedovo_check_in',
            created=datetime.datetime.now(),
            dispatch_status='idle',
            order_meta=json.dumps(
                create_order_meta(
                    order['order_id'], 'user_id', order['lookup_ttl'],
                ),
            ),
        )

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.json['order_id'] == 'order_id_2'
        return {'candidates': []}

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    assert _mock_order_search.times_called == fetched_orders
