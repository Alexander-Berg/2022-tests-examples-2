import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


ORDER_ID_1 = '8fa174f64a0afbcc2143395bc9f652dd'
ORDER_ID_2 = '8fa1742da0be44d8f51a5bc9f652addd'
ORDER_ID_3 = '8fa174f64a0b4d8488395bc141236ffa'
DBID_1 = 'dbid1'
DBID_2 = 'dbid2'
DBID_3 = 'dbid3'
UUID_1 = 'uuid1'
UUID_2 = 'uuid2'
UUID_3 = 'uuid3'


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
    'metadata': {'reposition_check_required': True},
}


ASSIGNMENT_REQUEST_1 = {
    ORDER_ID_1: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'repo_check': False},
        {'dbid': DBID_2, 'uuid': UUID_2, 'repo_check': True},
        {'dbid': DBID_3, 'uuid': UUID_3, 'repo_check': True},
    ],
    ORDER_ID_2: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'repo_check': True},
        {'dbid': DBID_2, 'uuid': UUID_2, 'repo_check': False},
        {'dbid': DBID_3, 'uuid': UUID_3, 'repo_check': True},
    ],
    ORDER_ID_3: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'repo_check': True},
        {'dbid': DBID_2, 'uuid': UUID_2, 'repo_check': True},
        {'dbid': DBID_3, 'uuid': UUID_3, 'repo_check': False},
    ],
}

ASSIGNMENT_RESPONSE_1 = {
    'pending_orders': 3,
    'drivers_assigned': 2,
    'drivers': {
        ORDER_ID_2: {'dbid': DBID_2, 'uuid': UUID_2},
        ORDER_ID_3: {'dbid': DBID_3, 'uuid': UUID_3},
    },
}

ASSIGNMENT_REQUEST_2 = {
    ORDER_ID_1: [{'dbid': DBID_1, 'uuid': UUID_1, 'repo_check': False}],
    ORDER_ID_2: [{'dbid': DBID_1, 'uuid': UUID_1, 'repo_check': False}],
}

ASSIGNMENT_RESPONSE_2 = {
    'pending_orders': 2,
    'drivers_assigned': 1,
    'drivers': {ORDER_ID_2: {'dbid': DBID_1, 'uuid': UUID_1}},
}


def create_order_meta(order_id, user_id):
    result = copy.deepcopy(data.ORDER_META)
    result['order_id'] = order_id
    result['order']['user_id'] = user_id
    return result


def create_candidate(dbid, uuid, repo_check):
    result = copy.deepcopy(RAW_CANDIDATE)
    result['id'] = f'{dbid}_{uuid}'
    result['dbid'] = dbid
    result['uuid'] = uuid
    result['metadata']['reposition_check_required'] = repo_check
    return result


V2_SCORING_RESULT_1 = {
    'responses': [
        {
            'search': {'retention_score': 100},
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'metadata': {'reposition_check_required': False},
                    'score': 185.3334,
                },
            ],
        },
        {
            'candidates': [
                {
                    'id': 'dbid2_uuid2',
                    'metadata': {'reposition_check_required': False},
                    'score': 185.3334,
                },
            ],
            'search': {'retention_score': 100},
        },
        {
            'candidates': [
                {
                    'id': 'dbid3_uuid3',
                    'metadata': {'reposition_check_required': False},
                    'score': 185.3334,
                },
            ],
            'search': {'retention_score': 200},
        },
    ],
}


V2_SCORING_RESULT_2 = {
    'responses': [
        {
            'search': {'retention_score': 100},
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'metadata': {'reposition_check_required': False},
                    'score': 70,
                },
            ],
        },
        {
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'metadata': {'reposition_check_required': False},
                    'score': 80,
                },
            ],
            'search': {},
        },
    ],
}


@pytest.mark.parametrize(
    'assignment_request, scoring_result, assignment_response',
    [
        (ASSIGNMENT_REQUEST_1, V2_SCORING_RESULT_1, ASSIGNMENT_RESPONSE_1),
        (ASSIGNMENT_REQUEST_2, V2_SCORING_RESULT_2, ASSIGNMENT_RESPONSE_2),
    ],
)
@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_single_candidate_vs_retention_v2_handle(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        testpoint,
        assignment_request,
        scoring_result,
        assignment_response,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        order_id = request.json['order_id']
        drivers = assignment_request[order_id]
        response = {'candidates': []}
        for driver in drivers:
            response['candidates'].append(
                create_candidate(
                    driver['dbid'], driver['uuid'], driver['repo_check'],
                ),
            )
        return response

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring(request):
        for req in request.json['requests']:
            assert 'buffer_info' in req['search']
        return scoring_result

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    for key in assignment_request.keys():
        utils.insert_order(
            pgsql,
            service='taxi',
            user_id=f'user_of_{key}',
            order_id=key,
            zone_id='example',
            classes='{"econom"}',
            agglomeration='example_agglomeration',
            created=datetime.datetime.now(),
            dispatch_status='idle',
            order_meta=json.dumps(create_order_meta(key, f'user_of_{key}')),
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
        else:
            assert order['dispatch_status'] != 'dispatched'
            assert order['is_retained']
