import json

from tests_lookup import lookup_params


async def test_requirements(acquire_candidate, mockserver):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def metadata_for_order(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def manual_dispatch(request):
        body = json.loads(request.get_data())
        assert body['requirements'] == {
            'some_req': [1, 2, 3],
            'childchair': [1],
        }
        return mockserver.make_response(status=200, json={})

    order = lookup_params.create_params(
        generation=1, version=1, tariffs=['cargo'],
    )
    order['manual_dispatch'] = {'a': 'b'}
    order['order']['request']['requirements'] = {
        'some_req': [1, 2, 3],
        'childchair_submoscow': [1],
        'creditcard': True,
    }
    candidate = await acquire_candidate(order)
    assert not candidate

    await metadata_for_order.wait_call(timeout=1)
    await manual_dispatch.wait_call(timeout=1)
