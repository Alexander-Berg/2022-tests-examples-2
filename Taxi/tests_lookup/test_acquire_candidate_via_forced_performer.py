import json

import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


@pytest.mark.config(
    LOOKUP_FORCED_PERFORMER_SETTINGS={
        '__default__': {
            'fallback_not_satisfied': False,
            'whitelisted_filters': ['infra/class', 'infra/route_info'],
            'fallback_events': [],
        },
    },
)
async def test_forced_performer_base(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        body = json.loads(request.get_data())
        assert body['driver_ids'] == [{'dbid': 'dbid0', 'uuid': 'uuid0'}]
        assert body.get('excluded_ids') is None
        assert body.get('excluded_car_numbers') is None
        data = {
            'candidates': [
                {
                    'uuid': 'uuid0',
                    'dbid': 'dbid0',
                    'unique_driver_id': 'unique_driver_id',
                    'license': 'license',
                    'license_id': 'license_id',
                    'classes': ['cargo'],
                    'position': [37.642907, 55.735141],
                    'route_info': {'distance': 1147, 'time': 165},
                    'car_number': 'NUMBER',
                    'reasons': {'infra/route_info': [], 'infra/class': []},
                },
            ],
        }
        return mockserver.make_response(status=200, json=data)

    order = lookup_params.create_params()
    order['order']['request']['lookup_extra'] = {
        'performer_id': 'dbid0_uuid0',
        'intent': 'default',
    }
    order['order']['request']['dispatch_type'] = 'forced_performer'
    candidate = await acquire_candidate(order)

    await order_satisfy.wait_call(timeout=1)
    assert candidate['db_id'] == 'dbid0'
    assert candidate['udid'] == 'unique_driver_id'
    assert candidate['driver_id'] == '12345_uuid0'
    assert candidate['autoaccept'] == {'enabled': True}


@pytest.mark.config(
    LOOKUP_FORCED_PERFORMER_SETTINGS={
        '__default__': {
            'fallback_not_satisfied': True,
            'whitelisted_filters': ['infra/class'],
            'fallback_events': [],
        },
    },
)
async def test_forced_performer_not_satisfied(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        body = json.loads(request.get_data())
        assert body['driver_ids'] == [{'dbid': 'dbid0', 'uuid': 'uuid0'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid0',
                    'dbid': 'dbid0',
                    'unique_driver_id': 'unique_driver_id',
                    'license': 'license',
                    'license_id': 'license_id',
                    'classes': ['cargo'],
                    'position': [37.642907, 55.735141],
                    'route_info': {'distance': 1147, 'time': 165},
                    'car_number': 'NUMBER',
                    'reasons': {'infra/route_info': [], 'infra/class': []},
                },
            ],
        }
        return mockserver.make_response(status=200, json=data)

    order = lookup_params.create_params()
    order['order']['request']['lookup_extra'] = {
        'performer_id': 'dbid0_uuid0',
        'intent': 'default',
    }
    order['order']['request']['dispatch_type'] = 'forced_performer'
    candidate = await acquire_candidate(order)
    await order_satisfy.wait_call(timeout=1)
    assert candidate['db_id'] != 'dbid0'
    assert candidate['driver_id'] != '12345_uuid0'


@pytest.mark.config(
    LOOKUP_FORCED_PERFORMER_SETTINGS={
        '__default__': {
            'fallback_not_satisfied': False,
            'whitelisted_filters': [],
            'fallback_events': ['reject'],
        },
    },
)
async def test_forced_performer_assigned_and_reject(
        acquire_candidate, mockserver,
):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        body = json.loads(request.get_data())
        assert body['driver_ids'] == [{'dbid': 'dbid0', 'uuid': 'uuid0'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid0',
                    'dbid': 'dbid0',
                    'unique_driver_id': 'unique_driver_id',
                    'license': 'license',
                    'license_id': 'license_id',
                    'classes': ['cargo'],
                    'position': [37.642907, 55.735141],
                    'route_info': {'distance': 1147, 'time': 165},
                    'car_number': 'NUMBER',
                },
            ],
        }
        return mockserver.make_response(status=200, json=data)

    order = lookup_params.create_params()
    order['order']['request']['lookup_extra'] = {
        'performer_id': 'dbid0_uuid0',
        'intent': 'default',
    }
    order['order']['request']['dispatch_type'] = 'forced_performer'
    order['candidates'] = [
        {'car_number': 'NUMBER', 'driver_license_personal_id': 'pesonal_id1'},
    ]
    order['order_info'] = {'statistics': {'status_updates': [{'q': 'reject'}]}}
    candidate = await acquire_candidate(order)
    await order_satisfy.wait_call(timeout=1)
    assert candidate['db_id'] != 'dbid0'
    assert candidate['driver_id'] != '12345_uuid0'


@pytest.mark.config(
    LOOKUP_FORCED_PERFORMER_SETTINGS={
        '__default__': {
            'fallback_not_satisfied': False,
            'whitelisted_filters': [],
            'fallback_events': [],
            'fallback_before_due': 600,
            'fallback_after_created': 600,
        },
    },
)
@pytest.mark.now('2021-01-01T16:30:00.00Z')
@pytest.mark.parametrize('order_type', ['created', 'due'])
async def test_forced_performer_duration_fallback(
        order_core, stq_runner, mockserver, order_type,
):
    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        assert False, 'Should not be called'

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mock_candidates.make_candidates()

    order = lookup_params.create_params()
    order['order']['request']['lookup_extra'] = {
        'performer_id': 'dbid0_uuid0',
        'intent': 'default',
    }
    order['order']['request']['dispatch_type'] = 'forced_performer'
    if order_type == 'created':
        order['order']['created'] = 1609517600  # now - 1000
    if order_type == 'due':
        order['order']['request']['is_delayed'] = True
        order['order']['request']['due'] = 1609518900  # now + 300

    order_core.set_get_fields_response(order)
    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )
    await order_search.wait_call(timeout=1)
