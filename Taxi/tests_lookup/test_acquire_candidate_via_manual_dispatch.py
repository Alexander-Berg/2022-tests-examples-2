import json

from tests_lookup import lookup_params


async def test_manual_dispatch(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
        body = json.loads(request.get_data())
        assert body['manual_dispatch'] == {'a': 'b'}
        data = {
            'candidate': {
                'uuid': 'uuid',
                'dbid': 'dbid',
                'unique_driver_id': 'unique_driver_id',
                'license': 'license',
                'license_id': 'license_id',
                'classes': ['cargo'],
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
        generation=1, version=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {'a': 'b'}
    candidate = await acquire_candidate(order)

    await metadata_for_order.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)

    assert candidate['db_id'] == 'dbid'
    assert candidate['udid'] == 'unique_driver_id'
    assert candidate['driver_id'] == '12345_uuid'


async def test_manual_dispatch_not_found(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
        return mockserver.make_response(status=200, json={})

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {}
    candidate = await acquire_candidate(order)
    assert not candidate

    await metadata_for_order.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)


async def test_manual_dispatch_defreeze(acquire_candidate, mockserver):
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

    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
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
        generation=1, version=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {}
    await acquire_candidate(order, expect_fail=True)

    await metadata_for_order.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
    await parks_profile_list.wait_call(timeout=1)
    await defreeze.wait_call(timeout=1)


async def test_manual_dispatch_mirror(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
        return mockserver.make_response(status=200, json={})

    order = lookup_params.create_params(
        generation=1, version=1, wave=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {'mirror_only': True}
    candidate = await acquire_candidate(order)
    assert not candidate

    await metadata_for_order.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)
    await order_search.wait_call(timeout=1)


async def test_manual_dispatch_bad_class(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
        return mockserver.make_response(
            status=200, json={'message': 'irrelevant'},
        )

    order = lookup_params.create_params(
        generation=1, version=1, wave=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {}

    candidate = await acquire_candidate(order)
    assert not candidate

    await metadata_for_order.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)
    await order_search.wait_call(timeout=1)
