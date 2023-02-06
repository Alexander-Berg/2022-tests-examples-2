import bson
import pytest


def get_settings(**override):
    return {
        'new_way_enabled': False,
        'fail_on_reject': False,
        'enable_defreeze': False,
        'assign_driver_seconds': 60,
        'old_way_fallback_enabled': False,
        **override,
    }


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(
                        new_way_enabled=True, old_way_fallback_enabled=True,
                    ),
                ),
            ],
        ),
        pytest.param(),
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_lookup_success(taxi_manual_dispatch, load_json, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        manual_dispatch = request_body['update']['$set']['manual_dispatch']
        assert manual_dispatch['status'] == 'ok'
        assert 'errors' not in manual_dispatch
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        return load_json('candidates_response.json')

    response = await taxi_manual_dispatch.post(
        '/v1/lookup', load_json('lookup_request.json'),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'candidate' in response_json
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_lookup_failed_no_position(
        taxi_manual_dispatch, load_json, mockserver,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        manual_dispatch = request_body['update']['$set']['manual_dispatch']
        assert manual_dispatch['status'] == 'failed'
        assert manual_dispatch['errors'] == {'driver_offline': {}}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        result = load_json('candidates_response.json')
        result['candidates'][0]['position'] = [0, 0]
        return result

    response = await taxi_manual_dispatch.post(
        '/v1/lookup', load_json('lookup_request.json'),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'candidate' not in response_json
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_lookup_failed_not_satisfy(
        taxi_manual_dispatch, load_json, mockserver,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        manual_dispatch = request_body['update']['$set']['manual_dispatch']
        assert manual_dispatch['status'] == 'failed'
        assert manual_dispatch['errors'] == {'infra_class': {}}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        result = load_json('candidates_response.json')
        result['candidates'][0]['is_satisfied'] = False
        result['candidates'][0]['reasons'] = {'infra/class': {}}
        return result

    response = await taxi_manual_dispatch.post(
        '/v1/lookup', load_json('lookup_request.json'),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'candidate' not in response_json
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_frozen(taxi_manual_dispatch, load_json, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        manual_dispatch = request_body['update']['$set']['manual_dispatch']
        assert manual_dispatch['status'] == 'pending'
        assert 'errors' not in manual_dispatch
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        result = load_json('candidates_response.json')
        result['candidates'][0]['is_satisfied'] = False
        result['candidates'][0]['reasons'] = {'infra/frozen': {}}
        return result

    response = await taxi_manual_dispatch.post(
        '/v1/lookup', load_json('lookup_request.json'),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'candidate' not in response_json
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0


@pytest.mark.config(
    MANUAL_DISPATCH_LOOKUP_SETTINGS=get_settings(fail_on_reject=True),
    MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True,
)
async def test_reject(taxi_manual_dispatch, load_json, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        manual_dispatch = request_body['update']['$set']['manual_dispatch']
        assert manual_dispatch['status'] == 'failed'
        assert manual_dispatch['errors'] == {'reject': {}}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    lookup_request = load_json('lookup_request.json')
    lookup_request['excluded_ids'] = [
        '100500_0be96feb569f46208f8ca7877cc65c20',
    ]

    response = await taxi_manual_dispatch.post('/v1/lookup', lookup_request)
    assert response.status_code == 200
    response_json = response.json()
    assert 'candidate' not in response_json
    assert _set_order_fields.times_called == 1
    assert start_lookup.times_called == 0
