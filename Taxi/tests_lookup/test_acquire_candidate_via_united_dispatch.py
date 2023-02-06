import json

import pytest

from tests_lookup import lookup_params


@pytest.mark.experiments3(
    name='lookup_result_validation',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {
                'accept_not_satisfied': False,
                'fallback_not_satisfied': True,
                'whitelisted_filters': ['infra/route_info', 'infra/class'],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': False,
        'fallback_not_satisfied': True,
        'whitelisted_filters': ['infra/route_info', 'infra/class'],
    },
)
async def test_united_dispatch(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json['driver_ids'] == [{'dbid': 'dbid', 'uuid': 'uuid'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid',
                    'dbid': 'dbid',
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

    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['delivery'],
                'position': [37.642907, 55.735141],
                'route_info': {'distance': 1147, 'time': 165},
                'car_number': 'NUMBER',
            },
        }
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                'unique_driver_id',
                'NUMBER',
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'united-dispatch'
    candidate = await acquire_candidate(order)

    await united_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await order_satisfy.wait_call(timeout=1)

    assert candidate['db_id'] == 'dbid'
    assert candidate['udid'] == 'unique_driver_id'
    assert candidate['driver_id'] == '12345_uuid'


async def test_united_dispatch_not_found(acquire_candidate, mockserver):
    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        return mockserver.make_response(status=200, json={})

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'united-dispatch'
    candidate = await acquire_candidate(order)
    assert not candidate

    await united_dispatch.wait_call(timeout=1)


@pytest.mark.experiments3(
    name='lookup_result_validation',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {
                'accept_not_satisfied': True,
                'fallback_not_satisfied': True,
                'whitelisted_filters': [],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': True,
        'fallback_not_satisfied': True,
        'whitelisted_filters': [],
    },
)
async def test_united_dispatch_defreeze(acquire_candidate, mockserver):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_profile_list(request):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': 'error'},
        )

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        assert request.json['driver_ids'] == [{'dbid': 'dbid', 'uuid': 'uuid'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid',
                    'dbid': 'dbid',
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

    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['delivery'],
                'position': [37.642907, 55.735141],
                'route_info': {'distance': 1147, 'time': 165},
                'car_number': 'NUMBER',
            },
        }
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                'unique_driver_id',
                'NUMBER',
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def defreeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                'unique_driver_id',
                'NUMBER',
        ):
            return mockserver.make_response(
                status=200, json={'code': '200', 'message': 'OK'},
            )
        return mockserver.make_response(status=400)

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'united-dispatch'
    await acquire_candidate(order, expect_fail=True)

    await united_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await parks_profile_list.wait_call(timeout=1)
    await defreeze.wait_call(timeout=1)


@pytest.mark.config(
    LOOKUP_DISPATCH_SETTINGS={
        '__default__': {'enabled': True},
        'united-dispatch': {'enabled': False},
    },
)
async def test_united_dispatch_fallback(acquire_candidate, mockserver):
    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['delivery'],
                'position': [37.642907, 55.735141],
                'route_info': {'distance': 1147, 'time': 165},
                'car_number': 'NUMBER',
            },
        }
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['source'] = 'cargo_dispatch'
    candidate = await acquire_candidate(order)

    await freeze.wait_call(timeout=1)
    assert not united_dispatch.has_calls

    assert candidate


@pytest.mark.experiments3(
    name='lookup_result_validation',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {
                'accept_not_satisfied': False,
                'fallback_not_satisfied': False,
                'whitelisted_filters': ['infra/class'],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': False,
        'fallback_not_satisfied': False,
        'whitelisted_filters': ['infra/class'],
    },
)
async def test_united_dispatch_conflict(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json['driver_ids'] == [{'dbid': 'dbid', 'uuid': 'uuid'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid',
                    'dbid': 'dbid',
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

    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['delivery'],
                'position': [37.642907, 55.735141],
                'route_info': {'distance': 1147, 'time': 165},
                'car_number': 'NUMBER',
            },
        }
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                'unique_driver_id',
                'NUMBER',
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def defreeze(request):
        return {}

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'united-dispatch'
    candidate = await acquire_candidate(order)
    assert not candidate

    await order_satisfy.wait_call(timeout=1)
    await united_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await defreeze.wait_call(timeout=1)


@pytest.mark.experiments3(
    name='lookup_result_validation',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {
                'accept_not_satisfied': False,
                'fallback_not_satisfied': True,
                'whitelisted_filters': ['infra/class'],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': False,
        'fallback_not_satisfied': True,
        'whitelisted_filters': ['infra/class'],
    },
)
async def test_united_dispatch_satisfy_fallback(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json['driver_ids'] == [{'dbid': 'dbid', 'uuid': 'uuid'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid',
                    'dbid': 'dbid',
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

    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['delivery'],
                'position': [37.642907, 55.735141],
                'route_info': {'distance': 1147, 'time': 165},
                'car_number': 'NUMBER',
            },
        }
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def defreeze(request):
        return {}

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'united-dispatch'
    candidate = await acquire_candidate(order)
    assert candidate is not None

    await order_satisfy.wait_call(timeout=1)
    await united_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await defreeze.wait_call(timeout=1)


@pytest.mark.experiments3(
    name='lookup_result_validation',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {
                'accept_not_satisfied': True,
                'fallback_not_satisfied': True,
                'whitelisted_filters': ['infra/class'],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': True,
        'fallback_not_satisfied': True,
        'whitelisted_filters': ['infra/class'],
    },
)
async def test_united_dispatch_accept_not_satisfied(
        acquire_candidate, mockserver,
):
    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json['driver_ids'] == [{'dbid': 'dbid', 'uuid': 'uuid'}]
        data = {
            'candidates': [
                {
                    'uuid': 'uuid',
                    'dbid': 'dbid',
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

    @mockserver.json_handler('/united-dispatch/performer-for-order')
    def united_dispatch(request):
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['delivery'],
                'position': [37.642907, 55.735141],
                'route_info': {'distance': 1147, 'time': 165},
                'car_number': 'NUMBER',
            },
        }
        return mockserver.make_response(status=200, json=data)

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                'unique_driver_id',
                'NUMBER',
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def defreeze(request):
        assert False, 'Shoudnot be called'

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'united-dispatch'
    candidate = await acquire_candidate(order)

    await order_satisfy.wait_call(timeout=1)
    await united_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    assert not defreeze.has_calls

    assert candidate['db_id'] == 'dbid'
    assert candidate['udid'] == 'unique_driver_id'
    assert candidate['driver_id'] == '12345_uuid'
