import pytest


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
async def test_request_car_path(taxi_tigraph_router, load_binary, mockserver):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary('maps.protobuf'),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_tigraph_router.post(
        'test-router-query',
        {
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
            'request_type': 'path',
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert 'router_name' in data
    assert data['router_name'] == 'yamaps-router'

    assert 'paths' in data
    assert len(data['paths']) == 1

    path = data['paths'][0]
    assert int(path['duration']) == 747
    assert int(path['length']) == 3541
    assert len(path['path']) == 97
