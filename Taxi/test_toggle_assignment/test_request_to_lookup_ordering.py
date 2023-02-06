import copy
import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


ORDER_ID_1 = '8ba174f64a0afbcc2143395bc9f652dd'
ORDER_ID_2 = '8aa1742da0be44d8f51a5bc9f652addd'
ORDER_ID_3 = '8da174f64a0b4d8488395bc141236ffa'
ORDER_ID_4 = '8fc17184641485bc1aaaccc12d336ffa'
ORDER_ID_5 = '8ea17931184641484a5bc1aeaaccd6ef'
DBID_1 = 'dbid1'
DBID_2 = 'dbid2'
DBID_3 = 'dbid3'
UUID_1 = 'uuid1'
UUID_2 = 'uuid2'
UUID_3 = 'uuid3'


ASSIGNMENT_REQUEST = {
    ORDER_ID_1: [{'dbid': DBID_1, 'uuid': UUID_1, 'route_time': 100}],
    ORDER_ID_2: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'route_time': 200},
        {'dbid': DBID_2, 'uuid': UUID_2, 'route_time': 300},
    ],
    ORDER_ID_3: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'route_time': 200},
        {'dbid': DBID_2, 'uuid': UUID_2, 'route_time': 300},
        {'dbid': DBID_3, 'uuid': UUID_3, 'route_time': 200},
    ],
    ORDER_ID_4: [{'dbid': DBID_3, 'uuid': UUID_3, 'route_time': 100}],
    ORDER_ID_5: [
        {'dbid': DBID_1, 'uuid': UUID_1, 'route_time': 400},
        {'dbid': DBID_3, 'uuid': UUID_3, 'route_time': 200},
    ],
}


def _create_order_meta(order_id, user_id):
    result = copy.deepcopy(data.ORDER_META)
    result['order_id'] = order_id
    result['order']['user_id'] = user_id
    result['metadata'] = {}
    result['extra_key'] = 'foo'
    return result


def _create_candidate(dbid, uuid, route_time):
    result = copy.deepcopy(data.CANDIDATE)
    result['id'] = f'{dbid}_{uuid}'
    result['dbid'] = dbid
    result['uuid'] = uuid
    result['route_info']['time'] = route_time
    return result


def _reduce_candidates(candidates):
    result = []
    for candidate in candidates:
        result.append(candidate['id'])
    result.sort()
    return result


def _reduce_request(request):
    assert 'requests' in request
    requests_arr = request['requests']
    result = {}
    for request_val in requests_arr:
        result.update(
            {
                request_val['search']['order_id']: _reduce_candidates(
                    request_val['candidates'],
                ),
            },
        )
    return result


def _compare_requests(lhs, rhs):
    assert sorted(lhs, key=lambda d: max(d.keys())) == sorted(
        rhs, key=lambda d: max(d.keys()),
    )


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=False)
@pytest.mark.parametrize(
    'candidates_limit_in_scoring_request, request_path',
    [
        (0, 'request_to_lookup_ordering_0.json'),
        (1, 'request_to_lookup_ordering_1.json'),
        (3, 'request_to_lookup_ordering_3.json'),
        (6, 'request_to_lookup_ordering_6.json'),
    ],
)
async def test_assignment_by_ordering_result(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        testpoint,
        taxi_config,
        load_json,
        candidates_limit_in_scoring_request,
        request_path,
):
    request_storage = []

    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert 'order_id' in request.json
        assert 'callback' not in request.json
        assert 'metadata' in request.json
        assert request.json['extra_key'] == 'foo'
        order_id = request.json['order_id']
        assert order_id in ASSIGNMENT_REQUEST
        drivers = ASSIGNMENT_REQUEST[order_id]
        response = {'candidates': []}
        for driver in drivers:
            response['candidates'].append(
                _create_candidate(
                    driver['dbid'], driver['uuid'], driver['route_time'],
                ),
            )
        return response

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        request_storage.append(_reduce_request(request.json))
        return mockserver.make_response(json={'responses': []})

    @testpoint('assignment_stats')
    def assignment_stats(t_data):
        return t_data

    for key in ASSIGNMENT_REQUEST:
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
            order_meta=json.dumps(_create_order_meta(key, 'user_id')),
        )

    taxi_config.set_values(
        {
            'DISPATCH_BUFFER_CANDIDATES_LIMIT_IN_SCORING_REQUEST': (
                candidates_limit_in_scoring_request
            ),
        },
    )
    await taxi_dispatch_buffer.invalidate_caches()

    await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')
    await assignment_stats.wait_call()

    _compare_requests(request_storage, load_json(request_path))
