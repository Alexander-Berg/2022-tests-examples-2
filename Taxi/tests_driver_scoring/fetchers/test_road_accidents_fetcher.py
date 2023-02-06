import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='settings.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_order_road_accidents(
        taxi_driver_scoring, mockserver, load_json, load_binary,
):

    router_requests = 0

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        nonlocal router_requests
        router_requests += 1
        return mockserver.make_response(
            response=load_binary('route1.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    cache_reads = 0
    cache_writes = 0
    cache_storage = {}

    @mockserver.json_handler('/api-cache/v1/cached-value/road-hazards')
    def _api_cache_mock(request):
        nonlocal cache_reads, cache_writes, cache_storage
        key = request.query['key']
        if request.method == 'PUT':
            assert request.headers.get('Cache-Control').startswith('max-age=')
            data = request.get_data()
            cache_storage[key] = data
            cache_writes += 1
            return {}
        if request.method == 'GET':
            data = cache_storage.get(key)
            if not data:
                return mockserver.make_response(status=404)
            cache_reads += 1
            return mockserver.make_response(
                data,
                headers={'Content-Type': 'application/octet-stream'},
                status=200,
            )
        raise RuntimeError(f'Unsupported method {request.method}')

    request_body = load_json('request_body.json')
    response_body = load_json('response_body.json')

    async def make_request():
        response = await taxi_driver_scoring.post(
            'v2/score-candidates-bulk',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=request_body,
        )
        assert response.status_code == 200
        assert response.json() == response_body

    router_requests = cache_writes = cache_reads = 0
    await make_request()
    assert router_requests == 1
    assert cache_writes == 1
    assert cache_reads == 0

    router_requests = cache_writes = cache_reads = 0
    await make_request()
    assert router_requests == 0
    assert cache_writes == 0
    assert cache_reads == 1
