import time

import pytest

from tests_lookup import agglomeration_settings
from tests_lookup import airport_config
from tests_lookup import lookup_params
from tests_lookup import mock_candidates


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True, DISPATCH_BUFFER_ENABLED=True,
)
async def test_dispatch_buffer_200(acquire_candidate, mockserver, testpoint):
    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        body = request.json
        assert 'order_id' in body
        assert 'order' in body
        assert 'request' in body['order']
        assert 'callback' in body
        assert 'lookup' in body
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        assert False, 'should not be called'

    order = lookup_params.create_params(generation=1, version=7, wave=1)
    assert order['order']['nz'] == 'moscow'
    order['order']['created'] = time.time()

    candidate = await acquire_candidate(order)
    assert candidate

    await dispatch_buffer.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True,
    DISPATCH_BUFFER_ENABLED=True,
    LOOKUP_FEATURE_SWITCHES={'require_new_search_for_freeze': True},
)
async def test_dispatch_buffer_failed_freeze(
        acquire_candidate, mockserver, testpoint,
):
    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': False}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        assert False, 'should not be called'

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def _order_core_event(request):
        assert False, 'should not be called'

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def order_core_set_fields(request):
        pass

    order = lookup_params.create_params(generation=1, version=7, wave=1)
    assert order['order']['nz'] == 'moscow'
    order['order']['created'] = time.time()

    candidate = await acquire_candidate(order)
    assert not candidate

    await order_core_set_fields.wait_call(timeout=1)
    await dispatch_buffer.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True,
    DISPATCH_BUFFER_ENABLED=True,
    LOOKUP_FEATURE_SWITCHES={'require_new_search_for_fetch': True},
)
async def test_dispatch_buffer_failed_fetch(
        acquire_candidate, mockserver, testpoint,
):
    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _personal_license_retrieve(request):
        return {}

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        return mockserver.make_response(
            status=200, json={'code': '200', 'message': 'OK'},
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def _order_core_event(request):
        assert False, 'should not be called'

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def order_core_set_fields(request):
        pass

    order = lookup_params.create_params(generation=1, version=7, wave=1)
    assert order['order']['nz'] == 'moscow'
    order['order']['created'] = time.time()

    candidate = await acquire_candidate(order)
    assert not candidate

    await order_core_set_fields.wait_call(timeout=1)
    await dispatch_buffer.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True, DISPATCH_BUFFER_ENABLED=True,
)
async def test_dispatch_buffer_200_not_found(
        acquire_candidate, taxi_lookup, mockserver, testpoint, statistics,
):
    messages = [
        'created',
        'updated',
        'delayed_with_undersupply',
        'delayed',
        'retained',
        'trash',
    ]
    message = ''

    def get_message():
        nonlocal message
        return message

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _dispatch_buffer(request):
        response = {'message': get_message()}
        return response

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    assert order['order']['nz'] == 'moscow'
    order['order']['created'] = time.time()

    async with statistics.capture(taxi_lookup) as capture:
        for message in messages:
            candidate = await acquire_candidate(order)
            assert not candidate

    # don't check handler statistics
    filtered_statistics = dict(
        filter(
            lambda x: x[0].startswith('lookup-classes'),
            capture.statistics.items(),
        ),
    )
    assert filtered_statistics == {
        'lookup-classes.dispatch-buffer.agglomerations.moscow.delayed': 2,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.created': 1,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.updated': 1,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.undersupply': 1,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.retained': 1,
    }


@pytest.mark.parametrize('message', ['retained', 'delayed'])
@pytest.mark.config(DISPATCH_BUFFER_ENABLED=True)
async def test_dispatch_buffer_fallback(
        acquire_candidate, mockserver, message,
):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {'message': message}
        return response

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = time.time() - 130

    candidate = await acquire_candidate(order)
    assert not candidate

    assert dispatch_buffer.has_calls
    assert (message == 'retained') != order_search.has_calls


@pytest.mark.config(DISPATCH_BUFFER_ENABLED=True)
async def test_dispatch_buffer_irrelevant(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {'message': 'irrelevant'}
        return response

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = time.time() - 10

    candidate = await acquire_candidate(order)
    assert not candidate

    assert dispatch_buffer.has_calls
    assert order_search.has_calls


@pytest.mark.parametrize('code', [400, 401, 403, 429])
@pytest.mark.config(DISPATCH_BUFFER_ENABLED=True)
async def test_dispatch_buffer_4xx(acquire_candidate, mockserver, code):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        return mockserver.make_response(
            '', code, content_type='application/json',
        )

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = time.time() - 10

    candidate = await acquire_candidate(order)
    assert not candidate

    assert dispatch_buffer.has_calls
    assert order_search.has_calls


@pytest.mark.parametrize('message', ['retained', 'delayed'])
@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=True,
    DISPATCH_AIRPORT_ZONES=airport_config.make_airport_config(),
)
async def test_dispatch_buffer_is_delayed(
        acquire_candidate, mockserver, message,
):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {'message': message}
        return response

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = time.time() - 10
    order['order']['request']['due'] = time.time() + 100
    order['order']['request']['is_delayed'] = True

    candidate = await acquire_candidate(order)
    assert not candidate

    assert dispatch_buffer.has_calls
    assert (message == 'retained') != order_search.has_calls


@pytest.mark.parametrize('message', ['retained', 'delayed'])
@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=True,
    DISPATCH_AIRPORT_ZONES=airport_config.make_airport_config(),
    LOOKUP_ENABLE_LOOKUP_TTL_FOR_STALE=True,
    LOOKUP_BUFFER_ORDER_STALE={
        'enabled': True,
        'max_stale_period_sec': 60,
        'stale_period_factor': 0.05,
        'period_without_stale_sec': 600,
    },
)
async def test_dispatch_buffer_lookup_ttl_staled(
        acquire_candidate, mockserver, message,
):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {'message': message}
        return response

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = time.time() - 981
    order['order']['request']['lookup_ttl'] = 1000

    candidate = await acquire_candidate(order)
    assert not candidate

    assert dispatch_buffer.has_calls
    assert (message == 'retained') != order_search.has_calls


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=True,
    DISPATCH_AIRPORT_ZONES=airport_config.make_airport_config(),
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_dispatch_buffer_airport(
        acquire_candidate, mockserver, testpoint,
):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    def new_params(
            airport=False, queue_zone_id=None, order_id='airport-order-id',
    ):
        params = lookup_params.create_params(generation=1, version=1, wave=1)
        assert params['order']['nz'] == 'moscow'
        params['order']['created'] = time.time()
        params['_id'] = order_id
        if airport:
            params['order']['request']['source']['object_type'] = 'аэропорт'
        if queue_zone_id:
            params['order']['request']['source_geoareas'] = ['kazan_airport']
            params['order']['nz'] = 'kazan_airport'
            params['order']['request']['source']['geopoint'] = [5, 5]
        return params

    params = new_params(
        order_id='airport-order-id-1', queue_zone_id=True, airport=False,
    )

    candidate = await acquire_candidate(params)
    assert not candidate

    assert order_search.has_calls
    assert not dispatch_buffer.has_calls

    order_search.flush()
    params = new_params(order_id='airport-order-id-2', airport=True)

    candidate = await acquire_candidate(params)
    assert candidate
    assert not order_search.has_calls
    assert dispatch_buffer.has_calls


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=False, DISPATCH_BUFFER_ENABLED=True,
)
async def test_dispatch_buffer_apply_result(acquire_candidate, mockserver):
    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        assert False, 'should not be called'
        return mockserver.make_response()

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    order = lookup_params.create_params(generation=1, version=7, wave=1)
    order['order']['nz'] = 'abidjan'
    order['order']['created'] = time.time()

    candidate = await acquire_candidate(order)
    assert not candidate

    await order_search.wait_call(timeout=1)
    assert not dispatch_buffer.has_calls
    assert not freeze.has_calls


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=True,
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
    LOOKUP_PARAM_ENRICHERS=['dispatch_check_in'],
)
async def test_dispatch_buffer_check_in(
        acquire_candidate, mockserver, experiments3,
):
    experiments3.add_config(
        **agglomeration_settings.make_settings(
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

    check_in = {'check_in_time': 1628790759.55, 'pickup_line': 'pickup_line_0'}

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def dispatch_buffer(request):
        assert request.json['dispatch_check_in'] == check_in
        return mockserver.make_response()

    order = lookup_params.create_params(generation=1, version=7, wave=1)
    order['order']['created'] = time.time()
    order['dispatch_check_in'] = check_in

    candidate = await acquire_candidate(order)
    assert candidate
    await dispatch_buffer.wait_call(timeout=1)
