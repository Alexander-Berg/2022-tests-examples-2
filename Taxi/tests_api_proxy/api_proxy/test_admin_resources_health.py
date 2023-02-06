import pytest


RESOURCES_HEALTH_V1_URL = 'admin/v1/resources/health'
RESOURCES_HEALTH_V2_URL = 'admin/v2/resource/health'
RESOURCES_HEALTH_BATCH_URL = 'admin/v2/resource/health/batch'

AUTH_REQUEST_HEADER = 'X-YaTaxi-Allow-Auth-Request'
AUTH_RESPONSE_HEADER = 'X-YaTaxi-Allow-Auth-Response'
ALLOW = 'Allow'

WATCHDOG_TASK = 'distlock/resource_health_check_watchdog'


async def make_dependent_endpoint(endpoints, resource_ids):
    handler = {
        'enabled': True,
        'default-response': 'resp-ok',
        'responses': [{'id': 'resp-ok', 'status-code': '200'}],
        'sources': [
            {'id': res, 'resource': res, 'enabled': True}
            for res in resource_ids
        ],
    }
    ep_id = '--'.join(resource_ids)
    await endpoints.safely_create_endpoint(
        '/foo', endpoint_id=ep_id, get_handler=handler,
    )


@pytest.mark.parametrize('tvm_pass', [True, False])
@pytest.mark.config(API_PROXY_RESOURCE_HP_ALLOWED=True)
async def test_existing_resource_health(
        taxi_api_proxy,
        taxi_config,
        mockserver,
        resources,
        endpoints,
        tvm_pass,
):
    taxi_config.set(
        TVM_SERVICES={'monolith': 300},
        TVM_RULES=[{'src': 'api-proxy', 'dst': 'monolith'}],
    )
    await taxi_api_proxy.invalidate_caches()

    @mockserver.handler('/mock-me')
    def _mock_resource(request):
        if request.method in {'GET', 'POST'}:
            return mockserver.make_response(status=200, json={'key': 'value'})

        if request.method == 'OPTIONS':
            headers = {ALLOW: 'OPTIONS, GET, POST'}
            if request.headers.get(AUTH_REQUEST_HEADER) == 'tvm2':
                headers[AUTH_RESPONSE_HEADER] = (
                    'OK' if tvm_pass else 'forbidden'
                )
            return mockserver.make_response(status=200, headers=headers)

        return mockserver.make_response(status=405)

    for method in ['post', 'get', 'delete']:
        await resources.safely_create_resource(
            resource_id=f'mocked-resource-{method}',
            url=mockserver.url('mock-me'),
            method=method,
            tvm_name='monolith',
        )
    await make_dependent_endpoint(
        endpoints,
        [
            'mocked-resource-post',
            'mocked-resource-get',
            'mocked-resource-delete',
        ],
    )

    await taxi_api_proxy.run_task(WATCHDOG_TASK)

    for method in ['post', 'get']:
        resp = await taxi_api_proxy.get(
            RESOURCES_HEALTH_V1_URL,
            params=dict(id=f'mocked-resource-{method}', revision='0'),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body['method_status'] == 'ok'
        assert body['tvm_status'] == 'ok' if tvm_pass else 'denied'

    for method in ['delete']:
        resp = await taxi_api_proxy.get(
            RESOURCES_HEALTH_V1_URL,
            params=dict(id=f'mocked-resource-{method}', revision='0'),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body['method_status'] == 'method_not_allowed'
        assert body['tvm_status'] == 'ok' if tvm_pass else 'denied'


@pytest.mark.config(API_PROXY_RESOURCE_HP_ALLOWED=True)
async def test_unavailable_resource_health(
        taxi_api_proxy, mockserver, resources, endpoints,
):
    @mockserver.handler('/mock-me-500')
    def _mock_resource_500(request):
        return mockserver.make_response(status=500)

    @mockserver.handler('/mock-me-options-405')
    def _mock_resource_options_405(request):
        if request.method == 'OPTIONS':
            return mockserver.make_response(status=405)
        return mockserver.make_response(status=200)

    await resources.safely_create_resource(
        resource_id='mocked-resource-500',
        url=mockserver.url('mock-me-500'),
        method='post',
    )

    await resources.safely_create_resource(
        resource_id='mocked-resource-options-405',
        url=mockserver.url('mock-me-options-405'),
        method='post',
    )

    await make_dependent_endpoint(
        endpoints, ['mocked-resource-500', 'mocked-resource-options-405'],
    )

    await taxi_api_proxy.run_task(WATCHDOG_TASK)

    resp = await taxi_api_proxy.get(
        RESOURCES_HEALTH_V1_URL,
        params=dict(id='mocked-resource-500', revision='0'),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['method_status'] == 'resource_not_available'
    assert body['tvm_status'] == 'check_not_supported'

    resp = await taxi_api_proxy.get(
        RESOURCES_HEALTH_V1_URL,
        params=dict(id='mocked-resource-options-405', revision='0'),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['method_status'] == 'check_not_supported'
    assert body['tvm_status'] == 'check_not_supported'

    resp = await taxi_api_proxy.get(
        RESOURCES_HEALTH_V1_URL,
        params=dict(id='mocked-resource-unknown', revision='0'),
    )
    assert resp.status_code == 404


@pytest.mark.config(API_PROXY_RESOURCE_HP_ALLOWED=True)
async def test_bad_tvm2_resource_health(
        taxi_api_proxy, mockserver, resources, endpoints,
):
    @mockserver.handler('/mock-me-unknown')
    def _mock_resource(request):
        if request.method in {'GET', 'POST'}:
            return mockserver.make_response(status=200, json={'key': 'value'})

        if request.method == 'OPTIONS':
            headers = {ALLOW: 'OPTIONS, GET'}
            if request.headers.get(AUTH_REQUEST_HEADER) == 'tvm2':
                headers[AUTH_RESPONSE_HEADER] = 'OK'
            return mockserver.make_response(status=200, headers=headers)

        return mockserver.make_response(status=405)

    await resources.safely_create_resource(
        resource_id=f'mocked-resource-unknown-get',
        url=mockserver.url('mock-me-unknown'),
        method='get',
        tvm_name='unknown_source',
    )
    await make_dependent_endpoint(endpoints, ['mocked-resource-unknown-get'])

    await taxi_api_proxy.run_task(WATCHDOG_TASK)

    resp = await taxi_api_proxy.get(
        RESOURCES_HEALTH_V1_URL,
        params=dict(id='mocked-resource-unknown-get', revision='0'),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['method_status'] == 'check_not_supported'
    assert body['tvm_status'] == 'denied'
    assert body['check_fail_reason'] == (
        'Failed to create signed request to unknown_source: '
        'No TVM service id in TVM_SERVICES for unknown_source'
    )


@pytest.mark.config(API_PROXY_RESOURCE_HP_ALLOWED=False)
async def test_disabled_resource_health_checks(
        taxi_api_proxy, mockserver, resources, endpoints,
):
    @mockserver.handler('/mock-me-yet-another')
    def _mock_resource(request):
        if request.method == 'OPTIONS':
            headers = {ALLOW: 'OPTIONS'}
            if request.headers.get(AUTH_REQUEST_HEADER) == 'tvm2':
                headers[AUTH_RESPONSE_HEADER] = 'OK'
            return mockserver.make_response(status=200, headers=headers)
        return mockserver.make_response(status=405)

    await resources.safely_create_resource(
        resource_id=f'mocked-resource-yet-another-get',
        url=mockserver.url('mock-me-yet-another'),
        method='get',
    )
    await make_dependent_endpoint(
        endpoints, ['mocked-resource-yet-another-get'],
    )

    await taxi_api_proxy.run_task(WATCHDOG_TASK)

    resp = await taxi_api_proxy.get(
        RESOURCES_HEALTH_V1_URL,
        params=dict(id='mocked-resource-yet-another-get', revision='0'),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body['method_status'] == 'check_not_supported'
    assert body['tvm_status'] == 'check_not_supported'
    assert (
        body['check_fail_reason']
        == 'Resource check has been cancelled manually'
    )
