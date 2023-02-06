import flatbuffers
import pytest
# pylint: disable=import-error
import rate_limiter_proxy.fbs.Quota as FbQuota

RATE_LIMITER_SERVICE = 'rate-limiter-proxy-nginx-rate-limiter'

SET_TESTSUITE_TIMEOUTS = pytest.mark.config(
    STATISTICS_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    STATISTICS_RPS_LIMITER_PER_LIMITER_SETTINGS={
        '__default__': {'wait_request_duration': 2000},
    },
)

FORBIDDEN = -1
NO_LIMIT = -2


def _parse_quota(data):
    result = {}
    quota = FbQuota.Quota.GetRootAsQuota(data, 0)
    path = quota.Path()
    result['path'] = path.decode('utf-8') if path else ''
    client = quota.Client()
    result['client'] = client.decode('utf-8') if client else ''
    result['quota'] = quota.Quota()
    result['is_regexp'] = quota.IsRegexp()
    handler_name = quota.HandlerName()
    if handler_name:
        result['handler_name'] = handler_name.decode('utf-8')
    return result


def _serialize_quota(path, client, quota):
    builder = flatbuffers.Builder(0)
    path_offset = builder.CreateString(path)
    client_offset = builder.CreateString(client)
    FbQuota.QuotaStart(builder)
    FbQuota.QuotaAddPath(builder, path_offset)
    FbQuota.QuotaAddClient(builder, client_offset)
    FbQuota.QuotaAddQuota(builder, quota)
    builder.Finish(FbQuota.QuotaEnd(builder))
    return bytes(builder.Output())


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client_1': 23456,
        'client_2': 234567,
    },
    RATE_LIMITER_LIMITS={
        'auto': {
            '/test1': {
                'client_1': {'rate': 100, 'unit': 60},
                '__default__': {'rate': 10, 'unit': 1},
                '__anonym__': {'rate': 5, 'unit': 1},
            },
            '/test2': {
                'client_1': {'rate': 500, 'burst': 600, 'unit': 1},
                'client_2': {'rate': 1000, 'burst': 2000, 'unit': 1},
                'unknown': {'rate': 100},
            },
            '__default__': {
                'client_1': {'rate': 500, 'burst': 600, 'unit': 1},
            },
        },
    },
)
@SET_TESTSUITE_TIMEOUTS
async def test_quotas(taxi_rate_limiter_proxy, rps_limiter):
    resources = {
        '/test1:client_1': {'path': '/test1', 'client': '23456', 'quota': 10},
        '/test1:': {'path': '/test1', 'client': '', 'quota': 10},
        '/test1:anonym': {'path': '/test1', 'client': 'anonym', 'quota': 5},
        '/test2:client_1': {'path': '/test2', 'client': '23456', 'quota': 10},
        '/test2:client_2': {'path': '/test2', 'client': '234567', 'quota': 10},
        '/test2:unknown': {'path': '/test2', 'client': 'unknown', 'quota': 10},
        ':client_1': {'path': '', 'client': '23456', 'quota': 10},
    }
    for resource in resources:
        rps_limiter.set_budget(resource, 100)

    async def request_quotas():
        for resource, values in resources.items():
            # request 10 for every resource
            request = _serialize_quota(values['path'], values['client'], 10)
            response = await taxi_rate_limiter_proxy.post(
                'quota',
                data=request,
                headers={'Content-Type': 'application/flatbuffer'},
            )
            assert response.status_code == 200
            response = _parse_quota(response.content)
            assert response == dict(**values, is_regexp=False)
            # initial request for resource
            await rps_limiter.wait_request(RATE_LIMITER_SERVICE, {resource})
            # wait for background request
            await rps_limiter.wait_request(RATE_LIMITER_SERVICE, {resource})

    await request_quotas()


@pytest.mark.config(
    TVM_SERVICES={'auto': 2345, 'statistics': 777, 'client_1': 23456},
    RATE_LIMITER_LIMITS={
        'auto': {'/test1': {'client_1': {'rate': 0, 'unit': 60}}},
    },
)
@SET_TESTSUITE_TIMEOUTS
async def test_forbidden(taxi_rate_limiter_proxy, rps_limiter):
    request = _serialize_quota('/test1', '23456', 10)
    response = await taxi_rate_limiter_proxy.post(
        'quota',
        data=request,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    response = _parse_quota(response.content)
    assert response == {
        'path': '/test1',
        'client': '23456',
        'quota': FORBIDDEN,
        'is_regexp': False,
    }
    assert rps_limiter.call_count == 0


@pytest.mark.config(TVM_SERVICES={'auto': 2345, 'statistics': 777})
@SET_TESTSUITE_TIMEOUTS
async def test_no_limit(taxi_rate_limiter_proxy, rps_limiter):
    request = _serialize_quota('/test1', '23456', 10)
    response = await taxi_rate_limiter_proxy.post(
        'quota',
        data=request,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    response = _parse_quota(response.content)
    assert response == {
        'path': '/test1',
        'client': '23456',
        'quota': NO_LIMIT,
        'is_regexp': False,
    }
    assert rps_limiter.call_count == 0


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client_1': 23456,
        'client_2': 678,
        'client_3': 567,
    },
    RATE_LIMITER_LIMITS={
        'auto': {
            '/test-2': {'__default__': {'rate': 100}},
            '/test-[3-4]': {'__default__': {'rate': 100, 'is_regexp': True}},
            '__default__': {'client_1': {'rate': 100}},
        },
    },
)
@pytest.mark.parametrize(
    'path, client, resource, response_path, response_client, is_regexp',
    [
        ('/test-1', '23456', ':client_1', '', '23456', False),
        # matching client has higher priority than default path
        ('/test-2', '23456', ':client_1', '', '23456', False),
        ('/test-2', '678', '/test-2:', '/test-2', '', False),
        ('/test-3', '567', '/test-[3-4]:', '/test-[3-4]', '', True),
        # matching client has higher priority thann default path
        ('/test-3', '23456', ':client_1', '', '23456', False),
    ],
)
@SET_TESTSUITE_TIMEOUTS
async def test_default_values(
        taxi_rate_limiter_proxy,
        rps_limiter,
        path,
        client,
        resource,
        response_path,
        response_client,
        is_regexp,
):
    rps_limiter.set_budget(resource, 0)

    request = _serialize_quota(path, client, 10)
    response = await taxi_rate_limiter_proxy.post(
        'quota',
        data=request,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    response = _parse_quota(response.content)
    assert response == {
        'path': response_path,
        'client': response_client,
        'quota': 0,
        'is_regexp': is_regexp,
    }
    await rps_limiter.wait_request(RATE_LIMITER_SERVICE, {resource})


@pytest.mark.config(
    TVM_SERVICES={'auto': 2345, 'statistics': 777, 'client': 23456},
    RATE_LIMITER_LIMITS={
        'auto': {'/test': {'client': {'rate': 100, 'unit': 1}}},
    },
    STATISTICS_RPS_LIMITER_PER_LIMITER_SETTINGS={
        'rate-limiter-proxy-nginx-rate-limiter': {'minimal_quota': 25},
        '__default__': {'minimal_quota': 10},
    },
)
@SET_TESTSUITE_TIMEOUTS
async def test_per_limiter_settings(taxi_rate_limiter_proxy, rps_limiter):
    rps_limiter.set_budget('/test:client', 100)

    request = _serialize_quota('/test', '23456', 10)
    response = await taxi_rate_limiter_proxy.post(
        'quota',
        data=request,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    response = _parse_quota(response.content)
    assert response == {
        'path': '/test',
        'client': '23456',
        'quota': 10,
        'is_regexp': False,
    }
    await rps_limiter.wait_request(
        RATE_LIMITER_SERVICE,
        {'/test:client': {'requested-quota': 10, 'minimal-quota': 25}},
    )


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client_1': 123,
        'client_2': 456,
    },
)
@pytest.mark.parametrize(
    'path, client, resource, handler_name',
    [
        ('/test1', '123', '/test1:client_1', 'my_handler_1'),
        ('/test2', '456', '/test2:client_2', 'my_handler_2'),
        ('/test3', '123', '/test3:client_1', ''),
    ],
)
async def test_handler_name_in_quota(
        taxi_rate_limiter_proxy,
        rps_limiter,
        path,
        client,
        resource,
        handler_name,
):
    response = await taxi_rate_limiter_proxy.post(
        'limits',
        json={
            '/test1': {
                'client_1': {
                    'rate': 50,
                    'unit': 20,
                    'handler_name': 'my_handler_1',
                },
                'client_2': {
                    'rate': 100,
                    'unit': 10,
                    'handler_name': 'my_handler_1',
                },
            },
            '/test2': {
                'client_1': {
                    'rate': 40,
                    'burst': 100,
                    'unit': 20,
                    'handler_name': 'my_handler_2',
                },
                'client_2': {
                    'rate': 30,
                    'burst': 200,
                    'unit': 10,
                    'handler_name': 'my_handler_2',
                },
                '__default__': {
                    'rate': 20,
                    'unit': 1,
                    'handler_name': 'my_handler_2',
                },
            },
            '/test3': {'client_1': {'rate': 50, 'unit': 20}},
        },
    )
    assert response.status_code == 200

    rps_limiter.set_budget(resource, 10)

    request = _serialize_quota(path, client, 10)
    response = await taxi_rate_limiter_proxy.post(
        'quota',
        data=request,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status_code == 200
    response = _parse_quota(response.content)
    expected = {
        'path': path,
        'client': client,
        'quota': 10,
        'is_regexp': False,
    }
    if handler_name:
        expected['handler_name'] = handler_name
    assert response == expected
    await rps_limiter.wait_request(RATE_LIMITER_SERVICE, {resource})

    # cleanup external limits
    response = await taxi_rate_limiter_proxy.post('limits', json={})
    assert response.status_code == 200


@pytest.mark.config(
    TVM_SERVICES={'auto': 2345, 'statistics': 777, 'client': 23456},
    RATE_LIMITER_LIMITS={
        'auto': {
            r'/test(/\w+)+': {'client': {'rate': 100, 'is_regexp': True}},
            r'__default__': {'client': {'rate': 100}},
        },
    },
)
@SET_TESTSUITE_TIMEOUTS
async def test_regexp_limits(taxi_rate_limiter_proxy, rps_limiter):
    resource = r'/test(/\w+)+'
    rps_limiter.set_budget(resource + ':client', 100)

    for handler in '/test/handler1', '/test/handler2':
        request = _serialize_quota(handler, '23456', 10)
        response = await taxi_rate_limiter_proxy.post(
            'quota',
            data=request,
            headers={'Content-Type': 'application/flatbuffer'},
        )
        response = _parse_quota(response.content)
        assert response == {
            'path': resource,
            'client': '23456',
            'quota': 10,
            'is_regexp': True,
        }

        await rps_limiter.wait_request(
            RATE_LIMITER_SERVICE,
            {resource + ':client': {'requested-quota': 10}},
        )


@pytest.mark.config(
    TVM_SERVICES={'auto': 2345, 'statistics': 777, 'client3': 999},
    RATE_LIMITER_LIMITS={
        'auto': {r'/test[': {'client3': {'rate': 100, 'is_regexp': True}}},
    },
)
@SET_TESTSUITE_TIMEOUTS
async def test_broken_regexp(taxi_rate_limiter_proxy, rps_limiter):
    request = _serialize_quota('/broken/handler', '999', 10)
    response = await taxi_rate_limiter_proxy.post(
        'quota',
        data=request,
        headers={'Content-Type': 'application/flatbuffer'},
    )
    response = _parse_quota(response.content)
    assert response == {
        'path': '/broken/handler',
        'client': '999',
        'quota': NO_LIMIT,
        'is_regexp': False,
    }


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client_1': 23456,
        'client_2': 234567,
    },
    RATE_LIMITER_LIMITS={
        'auto': {'/test1': {'client_1': {'rate': 100, 'unit': 1}}},
    },
    STATISTICS_RPS_LIMITER_DISABLE_LIMITING={'__default__': True},
)
@SET_TESTSUITE_TIMEOUTS
async def test_disabled_limits(taxi_rate_limiter_proxy, rps_limiter):
    resources = {
        '/test1:client_1': {'path': '', 'client': '', 'quota': 100},
        '/test1:': {'path': '', 'client': '', 'quota': 5},
        '/test2:unknown': {'path': '', 'client': '', 'quota': 10},
    }

    async def request_quotas():
        for resource, values in resources.items():
            # request 10 for every resource
            request = _serialize_quota(
                values['path'], values['client'], values['quota'],
            )
            response = await taxi_rate_limiter_proxy.post(
                'quota',
                data=request,
                headers={'Content-Type': 'application/flatbuffer'},
            )
            assert response.status_code == 200
            response = _parse_quota(response.content)
            assert response == dict(**values, is_regexp=False)
            # initial request for resource
            await rps_limiter.wait_request(RATE_LIMITER_SERVICE, {resource})
            # wait for background request
            await rps_limiter.wait_request(RATE_LIMITER_SERVICE, {resource})

    await request_quotas()
