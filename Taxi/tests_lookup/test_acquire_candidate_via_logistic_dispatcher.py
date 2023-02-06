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
                'accept_not_satisfied': True,
                'fallback_not_satisfied': False,
                'whitelisted_filters': [],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': True,
        'fallback_not_satisfied': False,
        'whitelisted_filters': [],
    },
)
async def test_logistic_dispatcher(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def logistic_dispatcher(request):
        data = {
            'candidates': [
                {
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
            ],
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
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    candidate = await acquire_candidate(order)

    await metadata_for_order.wait_call(timeout=1)
    await logistic_dispatcher.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)

    assert candidate['db_id'] == 'dbid'
    assert candidate['udid'] == 'unique_driver_id'
    assert candidate['driver_id'] == '12345_uuid'


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
                'fallback_not_satisfied': False,
                'whitelisted_filters': [],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': True,
        'fallback_not_satisfied': False,
        'whitelisted_filters': [],
    },
)
async def test_logistic_dispatcher_not_found(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def logistic_dispatcher(request):
        return mockserver.make_response(status=200, json={})

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['econom'],
    )
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    candidate = await acquire_candidate(order)
    assert not candidate

    await metadata_for_order.wait_call(timeout=1)
    await logistic_dispatcher.wait_call(timeout=1)


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
                'fallback_not_satisfied': False,
                'whitelisted_filters': [],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': True,
        'fallback_not_satisfied': False,
        'whitelisted_filters': [],
    },
)
async def test_logistic_dispatcher_defreeze(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def parks_profile_list(request):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': 'error'},
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def logistic_dispatcher(request):
        data = {
            'candidates': [
                {
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
            ],
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
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    await acquire_candidate(order, expect_fail=True)

    await metadata_for_order.wait_call(timeout=1)
    await logistic_dispatcher.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await parks_profile_list.wait_call(timeout=1)
    await defreeze.wait_call(timeout=1)


@pytest.mark.config(
    LOOKUP_DISPATCH_SETTINGS={
        '__default__': {'enabled': True},
        'logistic-dispatcher': {'enabled': False},
    },
)
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
                'fallback_not_satisfied': False,
                'whitelisted_filters': [],
            },
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={
        'accept_not_satisfied': True,
        'fallback_not_satisfied': False,
        'whitelisted_filters': [],
    },
)
async def test_logistic_dispatcher_fallback(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def logistic_dispatcher(request):
        data = {
            'candidates': [
                {
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
            ],
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

    await metadata_for_order.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    assert not logistic_dispatcher.has_calls

    assert candidate
