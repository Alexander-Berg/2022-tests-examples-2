import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


ORDER_ID_1 = '8fa174f64a0afbcc2143395bc9f652dd'
ORDER_ID_2 = '8fa1742da0be44d8f51a5bc9f652addd'
DBID_1 = 'dbid1'
DBID_2 = 'dbid2'
UUID_1 = 'uuid1'
UUID_2 = 'uuid2'
ASSIGNMENT_REQUEST = {
    ORDER_ID_1: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'route_time': 100},
        {'dbid': DBID_2, 'uuid': UUID_2, 'route_time': 300},
    ],
    ORDER_ID_2: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'route_time': 200},
        {'dbid': DBID_2, 'uuid': UUID_2, 'route_time': 300},
    ],
}

RAW_CANDIDATE = {
    'car_number': 'some_number',
    'classes': ['econom'],
    'unique_driver_id': 'some_id',
    'position': [37.622647, 55.756032],
    'profile': {'grades': {'g_econom': 1, 'g_minivan': 1}},
    'route_info': {'distance': 15000, 'time': 200, 'approximate': False},
    'license_id': 'license_id',
    'status': {'driver': 'free'},
    'chain_info': {
        'destination': [55.0, 35.0],
        'left_dist': 100,
        'left_time': 10,
        'order_id': 'some_order_id',
    },
    'metadata': {'reposition_check_required': False},
}


def create_order_meta(order_id, user_id):
    result = copy.deepcopy(data.ORDER_META)
    result['order_id'] = order_id
    result['order']['user_id'] = user_id
    result['dispatch_check_in'] = {
        'check_in_time': 1588064400,
        'pickup_line': 'pickup_line_0',
    }
    return result


def create_candidate(dbid, uuid, route_time):
    result = copy.deepcopy(RAW_CANDIDATE)
    result['id'] = f'{dbid}_{uuid}'
    result['dbid'] = dbid
    result['uuid'] = uuid
    result['route_info']['time'] = route_time
    return result


@pytest.mark.now('2020-04-28T12:00:00+03:00')
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
async def test_assignment_check_in(
        taxi_dispatch_buffer, pgsql, mockserver, experiments3,
):
    experiments3.add_config(
        **utils.agglomeration_settings(
            'domodedovo_check_in',
            {
                'ALGORITHMS': ['hungarian'],
                'APPLY_ALGORITHM': 'hungarian',
                'APPLY_RESULTS': True,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 12000,
                'ORDERS_LIMIT': 1000,
                'RUNNING_INTERVAL': 2,
                'TERMINALS': ['terminal_C'],
            },
        ),
    )

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert 'dispatch_check_in' in request.json
        order_id = request.json['order_id']
        assert order_id in ASSIGNMENT_REQUEST
        drivers = ASSIGNMENT_REQUEST[order_id]
        response = {'candidates': []}
        for driver in drivers:
            response['candidates'].append(
                create_candidate(
                    driver['dbid'], driver['uuid'], driver['route_time'],
                ),
            )
        return response

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        assert 'dispatch_check_in' in request.json['requests'][0]['search']
        assert request.json['intent'] == 'dispatch-check-in'
        return mockserver.make_response('fail', status=500)

    for key in ASSIGNMENT_REQUEST:
        utils.insert_order(
            pgsql,
            service='check_in',
            user_id='user_id',
            order_id=key,
            zone_id='example',
            classes='{"econom"}',
            agglomeration='domodedovo_check_in',
            created=datetime.datetime.now(),
            dispatch_status='idle',
            order_meta=json.dumps(create_order_meta(key, 'user_id')),
        )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    rows = utils.select_named(pgsql)
    assert rows[0]['draw_cnt'] == 1
    assert rows[0]['dispatch_status'] == 'dispatched'

    assert rows[1]['draw_cnt'] == 1
    assert rows[1]['dispatch_status'] == 'dispatched'
