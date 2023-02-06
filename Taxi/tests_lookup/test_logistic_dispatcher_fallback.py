import datetime
import time

import pytest

from testsuite.utils import callinfo

from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DRIVER_CAR_NUMBER = 'test_car_1'


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
async def test_fallback(
        acquire_candidate,
        taxi_lookup,
        mockserver,
        testpoint,
        taxi_config,
        mocked_time,
):
    dispatcher_call_count = 0
    # expect_enabled = True

    @testpoint('check-statistics')
    def _check_statistics(data):
        return

    async def fire_fallback():
        await taxi_lookup.run_periodic_task('FallbackMonitor')
        call = await _check_statistics.wait_call()
        return call

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def _acquire_dispatcher(request):
        nonlocal dispatcher_call_count
        dispatcher_call_count += 1
        if (dispatcher_call_count % 2) == 0:
            candidate = mock_candidates.make_candidates()['candidates'][0]
            candidate['car_number'] = DRIVER_CAR_NUMBER
            data = {'candidates': [candidate]}
            return mockserver.make_response(status=200, json=data)
        return mockserver.make_response(
            '{"error": {"text": "something-bad-happened"}}', status=500,
        )

    # _check_statistics testpoint is called after a cycle of lookup classes
    # health check. call['data'] contains a dictionary with classes and their
    # states: True means class is healty, False - unhealthy and disabled
    async def wait_testpoint(expect_enabled):
        call = await fire_fallback()
        assert call['data']['logistic-dispatcher'] == expect_enabled

    async def validate_calls(order, expect_enabled):
        _check_statistics.flush()
        # still should be disabled
        await wait_testpoint(expect_enabled)
        # call 'lookup_contractor'
        await acquire_candidate(
            order,
            expect_fail=expect_enabled and dispatcher_call_count % 2 == 0,
        )
        if expect_enabled:
            await _acquire_dispatcher.wait_call()
        else:
            await _order_search.wait_call()
        with pytest.raises(callinfo.CallQueueTimeoutError):
            if expect_enabled:
                await _order_search.wait_call(timeout=1)
            else:
                await _acquire_dispatcher.wait_call(timeout=1)

    now_time = datetime.datetime(2019, 8, 18, 12, tzinfo=datetime.timezone.utc)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)

    # Wait for CheckHealth to start new statistics epoch
    await wait_testpoint(True)

    taxi_config.set_values(
        {
            'LOOKUP_FALLBACK_SETTINGS': {
                '__default__': {
                    'enabled': False,
                    'min_requests_count': 10,
                    'max_error_percent': 25,
                    'disable_period_secs': 60,
                },
                'logistic-dispatcher': {
                    'enabled': True,
                    'min_requests_count': 10,
                    'max_error_percent': 25,
                    'disable_period_secs': 60,
                },
            },
        },
    )
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    order['order']['nz'] = 'himki'

    await wait_testpoint(True)
    assert not _acquire_dispatcher.has_calls and not _order_search.has_calls

    # initiate 2 failed calls (50%)
    for _i in range(4):
        await wait_testpoint(True)
        await acquire_candidate(
            order, expect_fail=dispatcher_call_count % 2 == 0,
        )
        await _acquire_dispatcher.wait_call()
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _order_search.wait_call(timeout=1)

    # initiate 3 more failed calls (50%)
    await wait_testpoint(True)
    # generating 10 bad calls - begin ()
    for _i in range(6):
        await acquire_candidate(
            order, expect_fail=dispatcher_call_count % 2 == 0,
        )
        await _acquire_dispatcher.wait_call()
    # generating 10 bad calls - done
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _order_search.wait_call(timeout=1)

    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _acquire_dispatcher.wait_call(timeout=1)

    # wait for statistics recheck, should be disabled now
    await validate_calls(order, False)

    # still should be disabled after 20 seconds
    await fire_fallback()
    now_time += datetime.timedelta(seconds=20)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    await validate_calls(order, False)

    # should be re-enabled after 60 more seconds
    _check_statistics.flush()
    await fire_fallback()
    now_time += datetime.timedelta(seconds=60)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    _check_statistics.flush()
    await fire_fallback()
    await validate_calls(order, True)


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
async def test_service_fallback(
        acquire_candidate,
        taxi_lookup,
        mockserver,
        testpoint,
        taxi_config,
        statistics,
        mocked_time,
):
    @testpoint('check-statistics')
    def _check_statistics(data):
        return

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def _acquire_dispatcher(request):
        candidate = mock_candidates.make_candidates()['candidates'][0]
        data = {'candidates': [candidate]}
        return mockserver.make_response(status=200, json=data)

    # _check_statistics testpoint is called after a cycle of lookup classes
    # health check. call['data'] contains a dictionary with classes and their
    # states: True means class is healty, False - unhealthy and disabled
    async def wait_testpoint(expect_enabled):
        await taxi_lookup.run_periodic_task('FallbackMonitor')
        call = await _check_statistics.wait_call()
        assert call['data']['logistic-dispatcher'] == expect_enabled

    async def validate_calls(order, service_enabled, moscow_enabled):
        # still should be disabled
        await wait_testpoint(service_enabled)
        # call 'lookup_contractor'
        await acquire_candidate(order)
        if moscow_enabled:
            await _acquire_dispatcher.wait_call()
        else:
            await _order_search.wait_call()
        with pytest.raises(callinfo.CallQueueTimeoutError):
            if moscow_enabled:
                await _order_search.wait_call(timeout=1)
            else:
                await _acquire_dispatcher.wait_call(timeout=1)

    # to ensure we start new internal statistics epoch
    now_time = datetime.datetime(2019, 8, 18, 14, tzinfo=datetime.timezone.utc)

    taxi_config.set_values(
        {
            'LOOKUP_FALLBACK_SETTINGS': {
                '__default__': {
                    'enabled': False,
                    'min_requests_count': 10,
                    'max_error_percent': 25,
                    'disable_period_secs': 60,
                },
                'logistic-dispatcher': {
                    'enabled': True,
                    'min_requests_count': 10,
                    'max_error_percent': 25,
                    'disable_period_secs': 60,
                },
            },
        },
    )
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    order['order']['created'] = now_time.timestamp()
    order['order']['nz'] = 'himki'

    await wait_testpoint(True)
    assert not _acquire_dispatcher.has_calls and not _order_search.has_calls

    await validate_calls(order, True, True)

    statistics.fallbacks = ['lookup-classes.logistic-dispatcher.fallback']
    now_time += datetime.timedelta(seconds=20)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, False)

    statistics.fallbacks = []
    now_time += datetime.timedelta(seconds=20)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, True)


@pytest.mark.config(
    LOOKUP_DISPATCH_SETTINGS={
        '__default__': {'enabled': True},
        'logistic-dispatcher': {'enabled': True, 'statistics': True},
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
async def test_capture(acquire_candidate, taxi_lookup, mockserver, statistics):
    acquire_result = 'found'

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        assert False, 'should not be called'

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def _acquire_dispatcher(request):
        nonlocal acquire_result
        if acquire_result == 'delayed':
            return mockserver.make_response(json={}, status=200)
        if acquire_result == '500':
            return mockserver.make_response('failure', status=500)
        candidate = mock_candidates.make_candidates()['candidates'][0]
        data = {'candidates': [candidate]}
        return mockserver.make_response(status=200, json=data)

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    order['order']['created'] = time.time()
    order['order']['nz'] = 'himki'

    assert not _acquire_dispatcher.has_calls and not _order_search.has_calls

    async with statistics.capture(taxi_lookup) as capture:
        # two 'found' responses are expected
        candidate = await acquire_candidate(order)
        assert candidate

        candidate = await acquire_candidate(order)
        assert candidate
        # one 'delayed' response
        acquire_result = 'delayed'
        candidate = await acquire_candidate(order)
        assert not candidate
        # and one 'misbehaviour' response - it does not go to statistics
        acquire_result = '500'
        await acquire_candidate(order, expect_fail=True)

    # don't check handler statistics
    filtered_statistics = dict(
        filter(
            lambda x: x[0].startswith('lookup-classes'),
            capture.statistics.items(),
        ),
    )
    assert filtered_statistics == {
        'lookup-classes.logistic-dispatcher.found': 2,
        'lookup-classes.logistic-dispatcher.delayed': 1,
        'lookup-classes.logistic-dispatcher.server_error': 1,
    }


@pytest.mark.config(
    LOOKUP_DISPATCH_SETTINGS={
        '__default__': {'enabled': False},
        'logistic-dispatcher': {
            'enabled': True,
            'fallback': True,
            'fallback_wait_seconds': 600,
        },
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
async def test_fallback_wait_seconds(
        acquire_candidate, mockserver, mocked_time,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/logistic-dispatcher/driver-for-order')
    def _acquire_dispatcher(request):
        candidate = mock_candidates.make_candidates()['candidates'][0]
        data = {'candidates': [candidate]}
        return mockserver.make_response(status=200, json=data)

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['request']['dispatch_type'] = 'logistic-dispatcher'
    created = datetime.datetime(2019, 8, 18, 14, tzinfo=datetime.timezone.utc)
    order['order']['created'] = created.timestamp()
    order['order']['nz'] = 'himki'

    mocked_time.set(created + datetime.timedelta(seconds=500))
    candidate = await acquire_candidate(order)
    assert candidate
    assert _acquire_dispatcher.has_calls and not _order_search.has_calls

    mocked_time.set(created + datetime.timedelta(seconds=601))
    candidate = await acquire_candidate(order)
    assert not candidate
    assert _order_search.has_calls
