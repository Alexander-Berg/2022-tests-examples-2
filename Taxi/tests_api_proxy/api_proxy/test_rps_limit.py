import asyncio

import pytest

API_PROXY_SERVICE = 'api-proxy-resource-limiter'

SET_TESTSUITE_TIMEOUTS = pytest.mark.config(
    STATISTICS_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    STATISTICS_RPS_LIMITER_PER_LIMITER_SETTINGS={
        '__default__': {'wait_request_duration': 2000},
    },
)


@pytest.mark.now('2020-07-07T00:00:00Z')
@SET_TESTSUITE_TIMEOUTS
async def test_rps_limit_one_handler(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    limit = 3
    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=limit,
    )
    rps_limiter.set_budget('resource', limit)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # request quota 1, spend it and request one more in background
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}

    assert test_resource.times_called == 1
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert rps_limiter.call_count == 2

    # spend last unit and request 2 (incoming rps is 2 now),
    # but gets 1 unit only
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 2
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert rps_limiter.call_count == 3

    # use last quota unit, budget on the server is empty now
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert test_resource.times_called == 3
    assert rps_limiter.call_count == 4

    # assigned quota is zero, so request is rejected
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 429
    assert test_resource.times_called == 3
    assert rps_limiter.call_count == 4


@SET_TESTSUITE_TIMEOUTS
async def test_two_handlers_one_resource(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=3,
    )
    rps_limiter.set_budget('resource', 3)

    path1 = '/test/foo/bar'
    handler_def1 = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path1, get_handler=handler_def1)

    path2 = '/test/foo/bar2'
    handler_def2 = load_yaml('handler_with_fallback_on_rps_limit.yaml')
    await endpoints.safely_create_endpoint(path2, get_handler=handler_def2)

    response = await taxi_api_proxy.get(path1)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 1
    # request quota = 1 + background request (1)
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert rps_limiter.call_count == 2

    response = await taxi_api_proxy.get(path2)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 2
    # request 2 but get only 1 unit
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert rps_limiter.call_count == 3

    # burn last request
    assert (await taxi_api_proxy.get(path2)).status_code == 200
    # try to get quota, but server sends 0 in response
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert rps_limiter.call_count == 4

    # rps-limiter throws rps-limit-breach exception, switch to fallback logic
    response = await taxi_api_proxy.get(path2)
    assert response.status_code == 200
    assert response.json() == {'result': 'fallback-value'}
    assert rps_limiter.call_count == 4


@pytest.mark.now('2020-07-07T00:00:00Z')
@SET_TESTSUITE_TIMEOUTS
async def test_get_quotas_for_two_resources(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource1(request):
        return {'value': 'test1'}

    @mockserver.json_handler('/resource2')
    def test_resource2(request):
        return {'value': 'test2'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=10,
    )
    rps_limiter.set_budget('resource', 30)

    await resources.safely_create_resource(
        resource_id='resource2',
        url=mockserver.url('/resource2'),
        method='get',
        rps_limit=10,
    )
    rps_limiter.set_budget('resource2', 30)

    path1 = '/test/foo/bar1'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path1, get_handler=handler_def)
    path2 = '/test/foo/bar2'
    handler_def['sources'][0]['resource'] = 'resource2'
    await endpoints.safely_create_endpoint(path2, get_handler=handler_def)

    assert (await taxi_api_proxy.get(path1)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert (await taxi_api_proxy.get(path1)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert (await taxi_api_proxy.get(path1)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert test_resource1.times_called == 3
    assert rps_limiter.call_count == 4

    assert (await taxi_api_proxy.get(path2)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource2'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource2'})
    assert (await taxi_api_proxy.get(path2)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource2'})
    assert (await taxi_api_proxy.get(path2)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource2'})
    assert test_resource2.times_called == 3
    assert rps_limiter.call_count == 8

    # now 'resource' and 'resource2' have 4 units

    # Resource quota is not refreshed if it has enough units (quota == rps),
    # so spend one request from 'resource2' quota to make ready to refresh
    assert (await taxi_api_proxy.get(path2)).status_code == 200
    # burn 'resource' quota
    for _ in range(2):
        assert (await taxi_api_proxy.get(path1)).status_code == 200

    assert (await taxi_api_proxy.get(path1)).status_code == 200
    assert test_resource1.times_called == 6
    # 'resource' has only 1 point left in quota thus limiter sends request for
    # quotas and adds resource2 to the request
    await rps_limiter.wait_request(
        API_PROXY_SERVICE, {'resource', 'resource2'},
    )
    assert rps_limiter.call_count == 9

    # burn 'resource2' quota
    for _ in range(2):
        assert (await taxi_api_proxy.get(path2)).status_code == 200

    # spend 1 point from 'resource' quota to make sure it is touched
    assert (await taxi_api_proxy.get(path1)).status_code == 200

    assert (await taxi_api_proxy.get(path2)).status_code == 200
    assert test_resource2.times_called == 7
    # only 1 point left for 'resource2' quota, limiter makes request for
    # resource2 and resource1 in backgroud
    await rps_limiter.wait_request(
        API_PROXY_SERVICE, {'resource', 'resource2'},
    )
    assert rps_limiter.call_count == 10

    # check 'resource1' quota is enough for at least 3 requests
    for _ in range(3):
        assert (await taxi_api_proxy.get(path1)).status_code == 200
    # Check that no additional requests were made for 'resource'
    assert rps_limiter.call_count == 10
    assert test_resource1.times_called == 10


@SET_TESTSUITE_TIMEOUTS
async def test_cached_requests_are_not_accounted(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        api_cache,
        load_yaml,
        mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        caching_enabled=True,
        rps_limit=3,
    )
    rps_limiter.set_budget('resource', 3)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    for i in range(10):
        response = await taxi_api_proxy.get(path)
        assert response.status_code == 200
        assert response.json() == {'result': 'test'}
        await api_cache.check_requests(
            mockserver.base_url + 'resource:get', get=True, put=(i == 0),
        )

    assert test_resource.times_called == 1
    # initial + background request
    assert rps_limiter.call_count == 2


@pytest.mark.now('2020-07-07T00:00:00Z')
@SET_TESTSUITE_TIMEOUTS
async def test_reject_time(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        mocked_time,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    limit = 3
    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=limit,
    )
    rps_limiter.set_budget('resource', limit)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    for _ in range(limit):
        response = await taxi_api_proxy.get(path)
        assert response.status_code == 200
        assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 3
    assert rps_limiter.call_count == 4

    # assigned quota is zero, so request is rejected
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 429
    assert test_resource.times_called == 3
    assert rps_limiter.call_count == 4

    mocked_time.sleep(0.8)
    # reject time hasn't passed yet, no request to statistics
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 429
    assert rps_limiter.call_count == 4

    mocked_time.sleep(0.1)
    rps_limiter.set_budget('resource', 3)
    # reject time passed, try to get new quota
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert rps_limiter.call_count == 5


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_statistics_failure(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        mocked_time,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    limit = 3
    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=limit,
    )
    rps_limiter.set_budget('resource', limit)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    assert (await taxi_api_proxy.get(path)).status_code == 200
    assert test_resource.times_called == 1

    # gets quota: 1 + 1
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})

    rps_limiter.is_down = True

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    await rps_limiter.wait_request(
        API_PROXY_SERVICE, {'resource'},
    )  # fails to get quota, return fallback value calculated from avg rps = 3
    # Fallback value overwrites currnet quota

    for _ in range(3):
        assert (await taxi_api_proxy.get(path)).status_code == 200

    # when fallback quota is spent, try to get quota from server again
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})

    # after second attempt failure client is not allowed to request new quota
    # or set fallback values again during 1 second.
    # Otherwise client would immediately "generate" new
    # fallback quotas when previous ones are spent, that is wrong
    mocked_time.sleep(0.95)
    assert (await taxi_api_proxy.get(path)).status_code == 429

    # second passed, client tries to get quota once again, fails and uses
    # fallback quota (3) again
    mocked_time.sleep(0.05)
    assert (await taxi_api_proxy.get(path)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})


@SET_TESTSUITE_TIMEOUTS
async def test_two_handlers_need_to_request_quota(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        testpoint,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    limit = 20
    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=limit,
    )
    rps_limiter.set_budget('resource', limit)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # set delay to make sure no one handler will have refreshed quota by the
    # time of execution
    @testpoint('testpoint::request_quotas')
    async def _request_quota_testpoint(data):
        await asyncio.sleep(0.02)

    # run two parallel handlers that will try to update quota
    responses = await asyncio.gather(
        taxi_api_proxy.get(path), taxi_api_proxy.get(path),
    )

    for response in responses:
        assert response.status_code == 200
        assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 2
    # 1st handler: initial + background request
    # 2nd handler: background request
    # only one handler shall actually request quota directly.
    # Second handler shall wait for the result of quota refresh
    for _ in range(3):
        await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})


@SET_TESTSUITE_TIMEOUTS
async def test_set_limit_in_prestable_resource(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        testpoint,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    @mockserver.json_handler('/resource-prestable')
    def test_prestable_resource(request):
        return {'value': 'prestable'}

    @testpoint('prestable_match_decision')
    def _make_decision(request):
        assert request['tag'] == 'resource'
        return {'decision': 'prestable'}

    await resources.safely_create_resource(
        resource_id='resource', url=mockserver.url('/resource'), method='get',
    )
    rps_limiter.set_budget('resource', 5)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'test'}

    assert test_resource.times_called == 1
    assert rps_limiter.call_count == 0

    await resources.safely_update_resource(
        resource_id='resource',
        url=mockserver.url('/resource-prestable'),
        method='get',
        prestable=30,
        rps_limit=5,
    )

    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'result': 'prestable'}
    assert test_prestable_resource.times_called == 1
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})


@SET_TESTSUITE_TIMEOUTS
async def test_race_with_false_reject(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        testpoint,
):
    # Here test reproduces the following case: quota is 0 and two handlers
    # want to update it. First one locks flag and makes a request to statistics
    # while second handler waits on condition variable until quota is
    # refreshed. In rare cases first handler gets response and refreshes quota
    # so fast that second handler hasn't event started to wait on condition
    # variable. In 'cond var' branch second handler doesn't check that quota
    # has already been refreshed and makes false reject.

    @mockserver.json_handler('/resource')
    def test_resource(request):
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        rps_limit=10,
    )
    rps_limiter.set_budget('resource', 10)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # make a delay before quota awaiting to reproduce case when quota
    # requesting handler refreshes local quota before second one
    # starts to wait on condition variable
    @testpoint('testpoint::await_quotas')
    async def _request_quota_testpoint(data):
        await asyncio.sleep(0.02)

    # run two parallel handlers that will try get
    responses = await asyncio.gather(
        taxi_api_proxy.get(path), taxi_api_proxy.get(path),
    )

    for response in responses:
        assert response.status_code == 200
        assert response.json() == {'result': 'test'}
    assert test_resource.times_called == 2
    assert rps_limiter.call_count == 3


@pytest.mark.now('2020-07-07T00:00:00Z')
@SET_TESTSUITE_TIMEOUTS
async def test_limiter_statistics(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
        taxi_api_proxy_monitor,
        mocked_time,
):
    @mockserver.json_handler('/resource2')
    @mockserver.json_handler('/resource')
    def _test_resource(request):
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        method='get',
        dev_team='team1',
        rps_limit=2,
    )
    rps_limiter.set_budget('resource', 1)

    await resources.safely_create_resource(
        resource_id='resource2',
        url=mockserver.url('/resource2'),
        method='get',
        dev_team='team2',
        rps_limit=10,
    )
    rps_limiter.set_budget('resource2', 3)

    path1 = '/test/foo/bar1'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path1, get_handler=handler_def)
    path2 = '/test/foo/bar2'
    handler_def['sources'][0]['resource'] = 'resource2'
    await endpoints.safely_create_endpoint(path2, get_handler=handler_def)

    assert (await taxi_api_proxy.get(path1)).status_code == 200
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    assert rps_limiter.call_count == 2
    assert (await taxi_api_proxy.get(path1)).status_code == 429

    for _ in range(3):
        assert (await taxi_api_proxy.get(path1)).status_code == 429

    for _ in range(3):
        assert (await taxi_api_proxy.get(path2)).status_code == 200
    assert (await taxi_api_proxy.get(path2)).status_code == 429
    assert rps_limiter.call_count == 6

    statistics = await taxi_api_proxy_monitor.get_metric('rps-limiter')
    limiter = statistics['api-proxy-resource-limiter']
    assert limiter['quota-requests-failed'] == 0

    resource = limiter['resource_stat']['resource']['team1']
    assert resource['decision']['rejected'] == 4
    assert resource['decision']['allowed'] == 1
    assert resource['quota-assigned'] == 1
    assert resource['limit'] == 2

    resource = limiter['resource_stat']['resource2']['team2']
    assert resource['decision']['rejected'] == 1
    assert resource['decision']['allowed'] == 3
    assert resource['quota-assigned'] == 3
    assert resource['limit'] == 10

    rps_limiter.is_down = True
    mocked_time.sleep(1)

    assert (await taxi_api_proxy.get(path1)).status_code == 200
    assert (await taxi_api_proxy.get(path2)).status_code == 200

    statistics = await taxi_api_proxy_monitor.get_metric('rps-limiter')
    limiter = statistics['api-proxy-resource-limiter']
    assert limiter['quota-requests-failed'] == 2

    resource = limiter['resource_stat']['resource']['team1']
    assert resource['decision']['rejected'] == 4
    assert resource['decision']['allowed'] == 2
    assert resource['quota-assigned'] == 1
    assert resource['limit'] == 2

    resource = limiter['resource_stat']['resource2']['team2']
    assert resource['decision']['rejected'] == 1
    assert resource['decision']['allowed'] == 4
    assert resource['quota-assigned'] == 3
    assert resource['limit'] == 10


@SET_TESTSUITE_TIMEOUTS
async def test_retries_are_accounted(
        taxi_api_proxy,
        endpoints,
        resources,
        rps_limiter,
        load_yaml,
        mockserver,
):
    @mockserver.json_handler('/resource')
    def test_resource(request):
        if test_resource.retries > 0:
            test_resource.retries -= 1
            return mockserver.make_response(status=500)
        return {'value': 'test'}

    test_resource.retries = 2

    limit = 3
    await resources.safely_create_resource(
        resource_id='resource',
        url=mockserver.url('/resource'),
        rps_limit=limit,
        method='get',
        max_retries=3,  # attempts, in fact
    )
    rps_limiter.set_budget('resource', limit)

    path = '/test/foo/bar'
    handler_def = load_yaml('handler_with_rps_limit_handling.yaml')
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # gets quota == 3 and uses all of it because of 2 retries
    assert (await taxi_api_proxy.get(path)).status_code == 200

    # no more budget and quota
    assert (await taxi_api_proxy.get(path)).status_code == 429
    assert test_resource.times_called == 3
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})
    await rps_limiter.wait_request(API_PROXY_SERVICE, {'resource'})


async def test_basic_rate_limiter_proxy(
        taxi_api_proxy, endpoints, resources, load_yaml, mockserver, testpoint,
):
    @testpoint('rate_limiter_proxy_transport')
    def _change_transport(request):
        return {'transport': 'tcp'}

    @mockserver.json_handler('/resource')
    def _test_resource(request):
        return {'value': 'test'}

    await resources.safely_create_resource(
        resource_id='resource', url=mockserver.url('/resource'), method='get',
    )

    @mockserver.json_handler('/limits')
    def rate_limiter_proxy(request):
        rate_limiter_proxy.limits = request.json

    # initial call when api-proxy starts
    await taxi_api_proxy.run_periodic_task('rate_limit_sending_task')
    await rate_limiter_proxy.wait_call()
    assert rate_limiter_proxy.limits == {}

    handler_def = load_yaml('handler_with_rate_limit.yaml')

    path1 = '/test/foo/bar'
    await endpoints.safely_create_endpoint(path1, get_handler=handler_def)
    path2 = '/test/chuu/baka'
    handler_def['rate-limit']['limit'] = 50
    handler_def['rate-limit']['burst'] = 80
    handler_def['rate-limit']['interval'] = 60
    await endpoints.safely_create_endpoint(path2, get_handler=handler_def)

    sent_limits = {
        path1: {
            '__default__': {
                'rate': 100,
                'burst': 150,
                'unit': 1,
                'handler_name': '/test/foo/bar',
            },
        },
        path2: {
            '__default__': {
                'rate': 50,
                'burst': 80,
                'unit': 60,
                'handler_name': '/test/chuu/baka',
            },
        },
    }

    await taxi_api_proxy.run_periodic_task('rate_limit_sending_task')
    await rate_limiter_proxy.wait_call()
    assert rate_limiter_proxy.limits == sent_limits

    # check that handler execution doesn't send limits
    assert (await taxi_api_proxy.get(path1)).status_code == 200
    assert (await taxi_api_proxy.get(path1)).status_code == 200

    # check that prestable values are ignored
    handler_def['rate-limit']['limit'] = 70
    await endpoints.safely_update_endpoint(
        path2, get_handler=handler_def, prestable=30,
    )

    await taxi_api_proxy.run_periodic_task('rate_limit_sending_task')
    await rate_limiter_proxy.wait_call()
    assert rate_limiter_proxy.limits == sent_limits
