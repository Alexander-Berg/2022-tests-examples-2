import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


ORDER_ID_1 = '8fa174f64a0afbcc2143395bc9f652dd'
ORDER_ID_2 = '8fa1742da0be44d8f51a5bc9f652addd'
ORDER_ID_3 = '8fa174f64a0b4d8488395bc141236ffa'
ORDER_ID_4 = '8fa17184641485bc1aaaccc12d336ffa'
DBID_1 = 'dbid1'
DBID_2 = 'dbid2'
DBID_3 = 'dbid3'
UUID_1 = 'uuid1'
UUID_2 = 'uuid2'
UUID_3 = 'uuid3'
ID_1 = f'{DBID_1}_{UUID_1}'
ID_2 = f'{DBID_2}_{UUID_2}'
ID_3 = f'{DBID_3}_{UUID_3}'


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
}


ASSIGNMENT_REQUEST_1 = {
    ORDER_ID_1: [{'dbid': DBID_1, 'uuid': UUID_1, 'metadata': None}],
    ORDER_ID_2: [
        {'dbid': DBID_2, 'uuid': UUID_2, 'metadata': {'initial_metadata': 2}},
    ],
    ORDER_ID_3: [
        {'dbid': DBID_3, 'uuid': UUID_3, 'metadata': {'initial_metadata': 3}},
    ],
}

SCORING_RESPONSE_1 = {
    'responses': [
        {
            'candidates': [
                {'id': ID_1, 'score': 100, 'metadata': {'new_metadata': 1}},
            ],
        },
        {
            'candidates': [
                {'id': ID_2, 'score': 100, 'metadata': {'new_metadata': 2}},
            ],
        },
        {'candidates': [{'id': ID_3, 'score': 100, 'metadata': None}]},
    ],
}

ASSIGNMENT_RESPONSE_1 = {
    'pending_orders': 3,
    'drivers_assigned': 3,
    'drivers': {
        ORDER_ID_1: {
            'dbid': DBID_1,
            'uuid': UUID_1,
            'metadata': {'new_metadata': 1},
        },
        ORDER_ID_2: {
            'dbid': DBID_2,
            'uuid': UUID_2,
            'metadata': {'new_metadata': 2},
        },
        ORDER_ID_3: {
            'dbid': DBID_3,
            'uuid': UUID_3,
            'metadata': {'initial_metadata': 3},
        },
    },
}


def create_order_meta(order_id, user_id):
    result = copy.deepcopy(data.ORDER_META)
    result['order_id'] = order_id
    result['order']['user_id'] = user_id
    return result


def create_candidate(dbid, uuid, metadata):
    result = copy.deepcopy(RAW_CANDIDATE)
    result['id'] = f'{dbid}_{uuid}'
    result['dbid'] = dbid
    result['uuid'] = uuid
    if metadata is not None:
        result['metadata'] = metadata
    return result


@pytest.mark.parametrize(
    'assignment_request, driver_scoring_response, assignment_response',
    [(ASSIGNMENT_REQUEST_1, SCORING_RESPONSE_1, ASSIGNMENT_RESPONSE_1)],
)
@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
async def test_assignment_by_ordering_result(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        testpoint,
        assignment_request,
        driver_scoring_response,
        assignment_response,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert 'order_id' in request.json
        order_id = request.json['order_id']
        assert order_id in assignment_request
        drivers = assignment_request[order_id]
        response = {'candidates': []}
        for driver in drivers:
            response['candidates'].append(
                create_candidate(
                    driver['dbid'], driver['uuid'], driver['metadata'],
                ),
            )
        return response

    @testpoint('ordering-bulk-response')
    def _ordering_response(request):
        if driver_scoring_response is None:
            return {'change_response': True, 'data': 'fail'}
        return {}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        if driver_scoring_response is not None:
            return driver_scoring_response
        return mockserver.make_response('fail', status=500)

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    for key in assignment_request.keys():
        utils.insert_order(
            pgsql,
            service='taxi',
            user_id='user_id',
            order_id=key,
            zone_id='example',
            classes='{"econom"}',
            agglomeration='example_agglomeration',
            created=datetime.datetime.now(),
            dispatch_status='idle',
            order_meta=json.dumps(create_order_meta(key, 'user_id')),
        )

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    stats = (await assignment_stats.wait_call())['t_data']
    assert stats['pending_orders'] == assignment_response['pending_orders']
    assert (
        stats['dispatched_orders'] == assignment_response['drivers_assigned']
    )

    for key in assignment_request.keys():
        rows = utils.select_named(pgsql, order_id=key)
        assert rows
        order = rows[0]
        if key in assignment_response['drivers']:
            assert order['dispatch_status'] == 'dispatched'

            dispatched_driver = order.get('dispatched_performer')
            correct_dispatched_driver = assignment_response['drivers'][key]
            assert (
                dispatched_driver['dbid'] == correct_dispatched_driver['dbid']
            )
            assert (
                dispatched_driver['uuid'] == correct_dispatched_driver['uuid']
            )
            assert (
                dispatched_driver['metadata']
                == correct_dispatched_driver['metadata']
            )
        else:
            assert order['dispatch_status'] != 'dispatched'
