import pytest


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
async def test_request_no_conf3(taxi_tigraph_router, mockserver):
    calls = {'yamaps': 0}

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        calls['yamaps'] = calls['yamaps'] + 1
        return mockserver.make_response('503 Service Unavailable ', 503)

    response = await taxi_tigraph_router.post(
        'test-router-query',
        {
            'router_type': 'car',
            'id': 'default',
            'request_type': 'summary',
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
        },
    )

    assert calls['yamaps'] == 3
    assert response.status_code == 500


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
@pytest.mark.experiments3(filename='config.json')
async def test_request_default_zone(taxi_tigraph_router, mockserver):
    calls = {'yamaps': 0}

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        calls['yamaps'] = calls['yamaps'] + 1
        return mockserver.make_response('503 Service Unavailable ', 503)

    response = await taxi_tigraph_router.post(
        'test-router-query',
        {
            'router_type': 'car',
            'id': 'default',
            'request_type': 'summary',
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
        },
    )

    assert calls['yamaps'] == 3
    assert response.status_code == 500


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
@pytest.mark.experiments3(filename='config_default_disabled.json')
async def test_request_default_disabled(taxi_tigraph_router, mockserver):
    calls = {'yamaps': 0}

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        calls['yamaps'] = calls['yamaps'] + 1
        return mockserver.make_response('503 Service Unavailable ', 503)

    response = await taxi_tigraph_router.post(
        'test-router-query',
        {
            'router_type': 'car',
            'id': 'default',
            'request_type': 'summary',
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
        },
    )

    assert calls['yamaps'] == 3
    assert response.status_code == 500


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
@pytest.mark.experiments3(filename='config.json')
async def test_request_zone1(taxi_tigraph_router, mockserver):
    calls = {'yamaps': 0}

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        calls['yamaps'] = calls['yamaps'] + 1
        return mockserver.make_response('503 Service Unavailable ', 503)

    response = await taxi_tigraph_router.post(
        'test-router-query',
        {
            'router_type': 'car',
            'id': 'zone1',
            'request_type': 'summary',
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
        },
    )

    assert calls['yamaps'] == 1
    assert response.status_code == 500


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
@pytest.mark.experiments3(filename='config.json')
async def test_request_zone2(taxi_tigraph_router, mockserver):
    calls = {'yamaps': 0}

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_route(request):
        calls['yamaps'] = calls['yamaps'] + 1
        return mockserver.make_response('503 Service Unavailable ', 503)

    response = await taxi_tigraph_router.post(
        'test-router-query',
        {
            'router_type': 'car',
            'id': 'zone2',
            'request_type': 'summary',
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
        },
    )

    assert calls['yamaps'] == 3
    assert response.status_code == 500
