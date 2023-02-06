import datetime
import json
import time

import bson
import pytest

from testsuite.utils import callinfo

from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DRIVER_CAR_NUMBER = 'test_car_1'
DRIVER_UUID = 'test_uuid_1'


def create_order_data(order_id, generation=1, version=1, wave=1):
    order = lookup_params.create_params(
        generation=generation, version=version, wave=wave,
    )
    order['_id'] = order_id
    assert order['order']['nz'] == 'moscow'
    order['order']['created'] = time.time()
    return order


def create_params(
        order, generation=1, version=1, wave=1, lookup_mode='dispatch-buffer',
):
    return {
        'order_id': order['_id'],
        'generation': generation,
        'version': version,
        'wave': wave,
        'lookup_mode': lookup_mode,
    }


def create_event_data():
    candidate = mock_candidates.make_candidates()['candidates'][0]
    candidate['uuid'] = DRIVER_UUID
    candidate['car_number'] = DRIVER_CAR_NUMBER
    return {'status': 'found', 'candidate': candidate}


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True,
    LOOKUP_CURRENT_DISPATCH_STORING_ENABLED=True,
    DISPATCH_BUFFER_ENABLED=True,
    LOOKUP_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 500},
        '/v2/event': {'attempts': 2, 'timeout-ms': 700},
    },
)
@pytest.mark.pgsql('lookup', queries=['DELETE FROM lookup.order'])
async def test_basic_happy_path(
        acquire_candidate, taxi_lookup, mockserver, pgsql, testpoint,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        if test_step != 'insert':
            assert False, 'should not be called'

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _dispatch_buffer(request):
        if test_step != 'empty':
            assert False, 'dispatcher should not be called: %s' % test_step
        body = json.loads(request.get_data())
        callback = body['callback']
        assert (callback['attempts'], callback['timeout_ms']) == (2, 700)
        expected_url = (
            '/v2/event?order_id='
            + body['order_id']
            + '&generation=1&version=3&wave=2'
            + '&lookup_mode=dispatch-buffer'
        )
        assert expected_url and callback['url'].endswith(expected_url)
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'wait'}, status=200,
        )

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/update')
    def meta_update(request):
        body = json.loads(request.get_data())
        assert body['metadata']['lookup']['mode'] == 'dispatch-buffer'
        return mockserver.make_response()

    @testpoint('current-dispatch-updated')
    def _current_dispatch_updated(data):
        return

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        if test_step != 'insert':
            assert False, 'freeze should not be called: %s' % test_step
        return {'freezed': True}

    order = create_order_data(
        '3780592dbb89366da23e625a1d7f3__3', version=3, wave=2,
    )
    event_data = create_event_data()
    params = create_params(order, version=3, wave=2)

    test_step = 'empty'
    candidate = await acquire_candidate(order)
    assert not candidate
    testpoint_disp_updated = await _current_dispatch_updated.wait_call()
    # /freeze should not be called, no candidate yet
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _freeze.wait_call(timeout=1)
    assert testpoint_disp_updated['data']['id'] == order['_id']
    assert (
        testpoint_disp_updated['data']['current_dispatch'] == 'dispatch-buffer'
    )
    # TODO: check the contents of lookup.order

    test_step = 'insert'
    await taxi_lookup.post('/v2/event', params=params, json=event_data)
    await order_core_event.wait_call(timeout=1)
    await meta_update.wait_call(timeout=1)


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True,
    DISPATCH_BUFFER_ENABLED=True,
    LOOKUP_CURRENT_DISPATCH_STORING_ENABLED=True,
)
@pytest.mark.pgsql('lookup', queries=['DELETE FROM lookup.order'])
async def test_version_mismatch(
        acquire_candidate, taxi_lookup, mockserver, pgsql, testpoint,
):
    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _dispatch_buffer(request):
        if test_step != 'empty':
            assert False, 'dispatcher should not be called: %s' % test_step
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'wait'}, status=200,
        )

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        if test_step == 'invalid-insert':
            return {'freezed': False}
        if test_step != 'insert':
            assert False, 'freeze should not be called: %s' % test_step
        return {'freezed': True}

    order = create_order_data('3780592dbb89366da23e625a1d7f3__4')
    event_data = create_event_data()
    params = create_params(order)

    test_step = 'empty'

    # should create lookup.order row with version.wave=1.1
    candidate = await acquire_candidate(order)
    assert not candidate
    # /freeze should not be called, no candidate yet
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _freeze.wait_call(timeout=1)

    test_step = 'invalid-insert'

    params.update({'generation': 1, 'version': 1, 'wave': 2})
    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (response.status_code, body.get('success'), body.get('error')) == (
        200,
        False,
        'invalid_order',
    )
    assert 'mismatch' in body.get('message')

    params.update({'generation': 1, 'version': 2, 'wave': 1})
    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (response.status_code, body.get('success'), body.get('error')) == (
        200,
        False,
        'invalid_order',
    )
    assert 'mismatch' in body.get('message')

    params.update({'generation': 2, 'version': 1, 'wave': 1})
    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (response.status_code, body.get('success'), body.get('error')) == (
        200,
        False,
        'invalid_order',
    )
    assert 'mismatch' in body.get('message')

    params.update({'generation': 1, 'version': 3, 'wave': 3})
    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (response.status_code, body.get('success'), body.get('error')) == (
        200,
        False,
        'freeze failed',
    )

    test_step = 'empty'

    candidate = await acquire_candidate(order)
    assert not candidate

    test_step = 'insert'

    params.update({'generation': 1, 'version': 3, 'wave': 3})
    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (response.status_code, body.get('success')) == (200, True)


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True,
    DISPATCH_BUFFER_ENABLED=True,
    LOOKUP_CLIENT_QOS={
        '__default__': {'attempts': 3, 'timeout-ms': 500},
        '/v2/event': {'attempts': 1, 'timeout-ms': 600},
    },
)
async def test_new_event_happy_path(
        order_core, stq_runner, taxi_lookup, mockserver, mocked_time,
):
    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _dispatch_buffer(request):
        body = json.loads(request.get_data())
        callback = body['callback']
        assert (callback['attempts'], callback['timeout_ms']) == (1, 600)
        expected_url = (
            '/v2/event?order_id='
            + body['order_id']
            + '&generation=1&version=11&wave=3'
            + '&lookup_mode=dispatch-buffer'
        )
        assert expected_url and callback['url'].endswith(expected_url)
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'retained'}, status=200,
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        assert (
            body['extra_update']['$push']['aliases']['id']
            == body['extra_update']['$push']['candidates']['alias_id']
        )
        body['extra_update']['$push']['aliases']['id'] = None
        body['extra_update']['$push']['candidates']['alias_id'] = None
        body['extra_update']['$push']['candidates']['created'] = None
        body['extra_update']['$push']['candidates']['driver_eta'] = None
        body['extra_update']['$push']['candidates']['dbcar_id'] = None
        assert body == {
            'fields': [],
            'extra_update': {
                '$inc': {'lookup.version': 1},
                '$push': {
                    'aliases': {
                        'due': datetime.datetime(2021, 7, 14, 8, 58, 36),
                        'due_optimistic': None,
                        'generation': 1,
                        'id': None,
                    },
                    'candidates': {
                        'adjusted_point': {
                            'avg_speed': 35,
                            'direction': 214,
                            'geopoint': [37.8954151234, 55.4183979995],
                            'time': 1533817820,
                        },
                        'alias_id': None,
                        'ar': 1,
                        'autoaccept': None,
                        'car_color': 'Red',
                        'car_color_code': 'red_code',
                        'car_model': 'BMW X2',
                        'car_number': DRIVER_CAR_NUMBER,
                        'ci': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                        'cr': 1,
                        'created': None,
                        'driver_eta': None,
                        'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                        'dbcar_id': None,
                        'discount': {},
                        'dist': 125,
                        'dp_values': {'c': 0},
                        'driver_classes': ['econom', 'business'],
                        'driver_id': '12345_' + DRIVER_UUID,
                        'driver_license': (
                            'number-67666d1b64314ff4a8d82ee89cd9d111'
                        ),
                        'driver_license_personal_id': (
                            '67666d1b64314ff4a8d82ee89cd9d111'
                        ),
                        'driver_metrics': {
                            'activity': 100,
                            'activity_blocking': {
                                'activity_threshold': 30,
                                'duration_sec': 3600,
                            },
                            'activity_prediction': {'c': 0},
                            'dispatch': None,
                            'id': None,
                            'properties': None,
                            'type': 'fallback',
                        },
                        'driver_points': 100,
                        'first_name': 'Maxim',
                        'gprs_time': 20.0,
                        'hiring_date': None,
                        'hiring_type': 'type',
                        'is': True,
                        'line_dist': 26292,
                        'metrica_device_id': '112233',
                        'name': 'Urev Maxim Dmitrievich',
                        'order_allowed_classes': ['econom'],
                        'paid_supply': False,
                        'phone': 'number-+799999999',
                        'phone_personal_id': '+799999999',
                        'point': [37.642907, 55.735141],
                        'rd': True,
                        'tags': ['tag0', 'tag1', 'tag2', 'tag3'],
                        'tariff_class': 'econom',
                        'tariff_currency': 'RUB',
                        'tariff_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                        'taximeter_version': '9.07 (1234)',
                        'time': 18,
                        'udid': '5dcbf13eb8e3f87968f01111',
                        'z': [],
                        'push_on_driver_arriving_send_at_eta': None,
                        'push_on_driver_arriving_sent': None,
                    },
                },
                '$set': {'lookup.state.wave': 3},
            },
            'filter': {'lookup.version': 11, 'status': 'pending'},
        }

        return mockserver.make_response('', 200)

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/update')
    def _meta_update(request):
        body = json.loads(request.get_data())
        assert body['metadata']['lookup']['mode'] == 'dispatch-buffer'
        return mockserver.make_response()

    event_data = create_event_data()
    order = create_order_data('78bd637369c82cb687f6a8651b5cda8d')
    params = create_params(order, version=11, wave=3)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)

    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )
    assert not order_core.driver_found

    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (
        response.status_code,
        body.get('success'),
        body.get('message'),
    ) == (200, True, None)
    assert order_core_event.has_calls
    await _meta_update.wait_call(timeout=1)


@pytest.mark.config(
    DISPATCH_BUFFER_AGGLOMERATIONS={
        'abidjan': ['abidjan'],
        'kazan_airport': ['kazan_airport'],
        'moscow': ['lyberci', 'himki', 'moscow'],
    },
)
async def test_v2_event_stats(
        taxi_lookup, mockserver, mocked_time, statistics,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def _order_core_event(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        return {'freezed': True}

    event_data = create_event_data()
    order = create_order_data('78bd637369c82cb687f6a8651b5cda8d')
    params = create_params(order, version=11, wave=3)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)

    async with statistics.capture(taxi_lookup) as capture:
        for _ in range(2):
            response = await taxi_lookup.post(
                'v2/event', params=params, json=event_data,
            )
            body = response.json()
            assert (
                response.status_code,
                body.get('success'),
                body.get('message'),
            ) == (200, True, None)

    # don't check handler statistics
    filtered_statistics = dict(
        filter(
            lambda x: x[0].startswith('lookup-classes'),
            capture.statistics.items(),
        ),
    )
    assert filtered_statistics == {
        'lookup-classes.dispatch-buffer.agglomerations.moscow.found': 2,
    }


@pytest.mark.config(
    LOOKUP_PGAAS_CALLBACKS_ENABLE=True, DISPATCH_BUFFER_ENABLED=True,
)
@pytest.mark.experiments3(
    name='lookup_v2_event',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={'enabled': True},
)
async def test_v2_event_409(taxi_lookup, mockserver, mocked_time, statistics):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def _order_core_event(request):
        return mockserver.make_response('', 409)

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        return {'freezed': True}

    event_data = create_event_data()
    order = create_order_data('78bd637369c82cb687f6a8651b5cda8d')
    params = create_params(order, version=11, wave=3)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)

    async with statistics.capture(taxi_lookup) as capture:
        response = await taxi_lookup.post(
            'v2/event', params=params, json=event_data,
        )
        body = response.json()
        assert (
            response.status_code,
            body.get('success'),
            body.get('message'),
        ) == (200, True, None)

    # don't check handler statistics
    filtered_statistics = dict(
        filter(
            lambda x: x[0].startswith('lookup-classes'),
            capture.statistics.items(),
        ),
    )
    assert filtered_statistics == {}


@pytest.mark.config(LOOKUP_PGAAS_CALLBACKS_ENABLE=True)
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
async def test_event_validation(
        order_core, stq_runner, taxi_lookup, mockserver, mocked_time,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json['order']['request'] is not None
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

    event_data = create_event_data()
    order = create_order_data('78bd637369c82cb687f6a8651b5cda8d')
    params = create_params(
        order, version=11, wave=3, lookup_mode='united-dispatch',
    )

    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (
        response.status_code,
        body.get('success'),
        body.get('message'),
    ) == (200, True, None)
    assert order_core_event.has_calls
    assert order_satisfy.has_calls


@pytest.mark.config(LOOKUP_PGAAS_CALLBACKS_ENABLE=True)
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
                'whitelisted_filters': [],
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
async def test_event_validation_failure(
        order_core, stq_runner, taxi_lookup, mockserver, mocked_time,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/driver-freeze/freeze')
    def _freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def defreeze(request):
        return {}

    @mockserver.json_handler('/candidates/order-satisfy')
    def order_satisfy(request):
        assert request.json['order']['request'] is not None
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

    event_data = create_event_data()
    order = create_order_data('78bd637369c82cb687f6a8651b5cda8d')
    params = create_params(
        order, version=11, wave=3, lookup_mode='united-dispatch',
    )

    response = await taxi_lookup.post(
        'v2/event', params=params, json=event_data,
    )
    body = response.json()
    assert (response.status_code, body.get('success')) == (200, False)
    assert not order_core_event.has_calls
    assert order_satisfy.has_calls
    await defreeze.wait_call(timeout=1)
