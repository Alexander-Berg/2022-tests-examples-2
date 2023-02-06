import datetime
import time

import pytest

from testsuite.utils import callinfo

from tests_lookup import agglomeration_settings
from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DRIVER_CAR_NUMBER = 'test_car_1'

LOOKUP_FALLBACK_SETTINGS = {
    '__default__': {
        'enabled': False,
        'min_requests_count': 10,
        'max_error_percent': 25,
        'disable_period_secs': 60,
    },
    'dispatch-buffer': {
        'enabled': True,
        'min_requests_count': 10,
        'max_error_percent': 25,
        'disable_period_secs': 60,
        'disable_period_multiplier': 2,
        'multiplier_appliance_period': 600,
    },
}


@pytest.mark.config(
    DISPATCH_BUFFER_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
    DISPATCH_BUFFER_ENABLED=True,
    DISPATCH_BUFFER_AGGLOMERATIONS={'moscow': ['moscow', 'himki']},
)
async def test_dispatch_buffer_fallback(
        acquire_candidate,
        taxi_lookup,
        mockserver,
        testpoint,
        taxi_config,
        mocked_time,
        experiments3,
):
    experiments3.add_config(
        **agglomeration_settings.make_settings(
            'moscow',
            {
                'ALGORITHMS': ['hungarian'],
                'APPLY_ALGORITHM': 'hungarian',
                'APPLY_RESULTS': True,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 12000,
                'ORDERS_LIMIT': 1000,
                'RUNNING_INTERVAL': 2,
            },
        ),
    )
    await taxi_lookup.invalidate_caches()
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

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _acquire_dispatcher(request):
        nonlocal dispatcher_call_count
        dispatcher_call_count += 1
        if (dispatcher_call_count % 2) == 0:
            candidate = mock_candidates.make_candidates()['candidates'][0]
            candidate['car_number'] = DRIVER_CAR_NUMBER
            return {'candidate': candidate}
        return mockserver.make_response(
            '{"error": {"text": "something-bad-happened"}}', status=500,
        )

    # _check_statistics testpoint is called after a cycle of lookup classes
    # health check. call['data'] contains a dictionary with classes and their
    # states: True means class is healty, False - unhealthy and disabled
    async def wait_testpoint(expect_enabled):
        call = await fire_fallback()
        # call['data'] should contain all classes, which are initialized
        # in the Fallback::Fallback. Here only 'buffer' class may fail,
        # others ('graph' and 'tracker' ATM) are absent in the config
        # LOOKUP_FALLBACK_SETTINGS and therefore always returns True (enabled)
        assert call['data']['dispatch-buffer'] == expect_enabled

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
        {'LOOKUP_FALLBACK_SETTINGS': LOOKUP_FALLBACK_SETTINGS},
    )
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = now_time.timestamp()
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
        await wait_testpoint(True)
        await acquire_candidate(
            order, expect_fail=dispatcher_call_count % 2 == 0,
        )
        await _acquire_dispatcher.wait_call()

    # generating 10 bad calls - done
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _order_search.wait_call(timeout=1)

    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _acquire_dispatcher.wait_call(timeout=1)

    # wait for statistics recheck, buffer-dispatch should be disabled now
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

    # Test exponential period
    # generating 10 bad calls - begin ()
    for _i in range(10):
        await acquire_candidate(
            order, expect_fail=dispatcher_call_count % 2 == 0,
        )
        await _acquire_dispatcher.wait_call()
    # generating 10 bad calls - done
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _order_search.wait_call(timeout=1)

    # wait for statistics recheck, buffer-dispatch should be disabled now
    await validate_calls(order, False)

    # still should be disabled after 100 seconds
    await fire_fallback()
    now_time += datetime.timedelta(seconds=100)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    await validate_calls(order, False)

    # should be re-enabled after 60 more seconds
    now_time += datetime.timedelta(seconds=60)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    await validate_calls(order, True)

    # multiplier_appliance_period should expire after 1000 more seconds
    now_time += datetime.timedelta(seconds=1000)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    await validate_calls(order, True)

    # generating 10 bad calls - begin ()
    await taxi_lookup.run_periodic_task('FallbackMonitor')
    for _i in range(10):
        await acquire_candidate(
            order, expect_fail=dispatcher_call_count % 2 == 0,
        )
        await _acquire_dispatcher.wait_call()
    # generating 10 bad calls - done
    with pytest.raises(callinfo.CallQueueTimeoutError):
        await _order_search.wait_call(timeout=1)

    # still should be disabled after 10 seconds
    await fire_fallback()
    now_time += datetime.timedelta(seconds=10)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    await validate_calls(order, False)

    # should be re-enabled after 60 more seconds
    now_time += datetime.timedelta(seconds=60)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=False)
    await validate_calls(order, True)


@pytest.mark.config(
    DISPATCH_BUFFER_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
    DISPATCH_BUFFER_ENABLED=True,
    DISPATCH_BUFFER_AGGLOMERATIONS={
        'abidjan': ['abidjan'],
        'moscow': ['lyberci', 'himki', 'moscow'],
    },
    LOOKUP_DISPATCH_EXTERNAL_STATISTICS={
        '__default__': [],
        'dispatch-buffer': [
            {'name': 'fallback'},
            {
                'name': 'fallback-created',
                'delayed_check': {
                    'expiration_time': 100,
                    'unchecked_time': 130,
                },
            },
        ],
    },
)
async def test_agglomeration_fallback(
        acquire_candidate,
        taxi_lookup,
        mockserver,
        testpoint,
        taxi_config,
        statistics,
        mocked_time,
        experiments3,
):
    experiments3.add_config(
        name='dispatch_buffer_agglomeration_settings',
        consumers=['lookup_dispatch/agglomeration_settings'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'abidjan',
                'value': {
                    'ALGORITHMS': ['greedy', 'hungarian'],
                    'APPLY_ALGORITHM': 'hungarian',
                    'APPLY_RESULTS': False,
                    'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                    'ENABLED': True,
                    'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 120,
                    'ORDERS_LIMIT': 1000,
                    'RUNNING_INTERVAL': 6,
                },
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': 'abidjan',
                                    'arg_name': 'agglomeration',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
            },
            {
                'title': 'moscow',
                'value': {
                    'ALGORITHMS': ['greedy', 'hungarian'],
                    'APPLY_ALGORITHM': 'hungarian',
                    'APPLY_RESULTS': True,
                    'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                    'ENABLED': True,
                    'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 5000,
                    'ORDERS_LIMIT': 1000,
                    'RUNNING_INTERVAL': 2,
                },
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': 'moscow',
                                    'arg_name': 'agglomeration',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
            },
        ],
        default_value={},
    )
    await taxi_lookup.invalidate_caches()

    @testpoint('check-statistics')
    def _check_statistics(data):
        return

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _acquire_dispatcher(request):
        return {'message': 'created'}
        # candidate = mock_candidates.make_candidates()['candidates'][0]
        # return {'candidate': candidate}

    # _check_statistics testpoint is called after a cycle of lookup classes
    # health check. call['data'] contains a dictionary with classes and their
    # states: True means class is healty, False - unhealthy and disabled
    async def wait_testpoint(expect_enabled):
        await taxi_lookup.run_periodic_task('FallbackMonitor')
        call = await _check_statistics.wait_call()
        # call['data'] should contain all classes, which are initialized
        # in the Fallback::Fallback. Here only 'buffer' class may fail,
        # others ('graph' and 'tracker' ATM) are absent in the config
        # LOOKUP_FALLBACK_SETTINGS and therefore always returns True (enabled)
        assert call['data']['dispatch-buffer'] == expect_enabled

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
        {'LOOKUP_FALLBACK_SETTINGS': LOOKUP_FALLBACK_SETTINGS},
    )
    statistics.fallbacks = []
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = now_time.timestamp()
    order['order']['nz'] = 'himki'

    await wait_testpoint(True)
    assert not _acquire_dispatcher.has_calls and not _order_search.has_calls

    # detect buffer start
    await validate_calls(order, True, True)

    # use fallback-created for 'moscow' agglomeration
    # first starts don't apply fallback-created
    # because we have just detected start
    statistics.fallbacks = [
        'lookup-classes.dispatch-buffer.'
        'agglomerations.moscow.fallback-created',
    ]
    now_time += datetime.timedelta(seconds=1)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, True)

    now_time += datetime.timedelta(seconds=80)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, True)

    # unchecked_time exceeded, start apply fallback-created
    now_time += datetime.timedelta(seconds=80)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, False)

    # after expiration_time buffer ban continues
    now_time += datetime.timedelta(seconds=500)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, False)

    # reenabling 'moscow'
    statistics.fallbacks = []
    now_time += datetime.timedelta(seconds=20)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, True)

    # use fallback for 'moscow' agglomeration
    statistics.fallbacks = [
        'lookup-classes.dispatch-buffer.agglomerations.moscow.fallback',
    ]
    now_time += datetime.timedelta(seconds=20)
    mocked_time.set(now_time)
    await taxi_lookup.tests_control(invalidate_caches=True)
    await validate_calls(order, True, False)


@pytest.mark.config(
    DISPATCH_BUFFER_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
    DISPATCH_BUFFER_ENABLED=True,
    LOOKUP_MULTIOFFER_SETTINGS={
        'moscow': {'enabled': True, 'zones': ['lyberci', 'himki', 'moscow']},
    },
)
@pytest.mark.experiments3(filename='agglomeration_settings.json')
async def test_agglomeration_capture(
        acquire_candidate,
        taxi_lookup,
        mockserver,
        testpoint,
        taxi_config,
        statistics,
):
    acquire_result = 'found'

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        assert False, 'should not be called'

    @mockserver.json_handler('/dispatch-buffer/performer-for-order')
    def _acquire_dispatcher(request):
        nonlocal acquire_result
        if acquire_result == 'delayed':
            return mockserver.make_response(json={}, status=200)
        if acquire_result == '500':
            return mockserver.make_response('failure', status=500)
        candidate = mock_candidates.make_candidates()['candidates'][0]
        return {'candidate': candidate}

    order = lookup_params.create_params(generation=1, version=1, wave=1)
    order['order']['created'] = time.time()
    order['order']['nearest_zone'] = 'himki'

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
        candidate = await acquire_candidate(order, expect_fail=True)

    # don't check handler statistics
    filtered_statistics = dict(
        filter(
            lambda x: x[0].startswith('lookup-classes'),
            capture.statistics.items(),
        ),
    )
    assert filtered_statistics == {
        'lookup-classes.multioffer.agglomerations.moscow.bad_class': 4,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.found': 2,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.delayed': 1,
        'lookup-classes.dispatch-buffer.agglomerations.moscow.server_error': 1,
    }
