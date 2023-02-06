import json

import pytest


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
async def test_route_infos_response_check(
        taxi_client_routing_sidecar, mockserver,
):
    router = 'car'
    body = {
        'selector_settings': {},
        'query_settings': {
            'path': [[58, 35], [58.1, 35.1], [58.5, 35.6]],
            'router_settings': {},
            'query_settings': {},
            'execution_settings': {},
        },
    }
    response = await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_route_infos', json=body,
    )
    print(response.content.decode())
    assert response.status_code == 200, response.content.decode()
    response_object = json.loads(response.content.decode())

    assert response_object == {
        'result': [{'distance': 80756.67090352962, 'time': 11628}],
    }


async def test_route_infos_map_request_check(
        taxi_client_routing_sidecar, mockserver,
):
    @mockserver.handler('/maps-router/v2/summary')
    def maps_summary_mock(data):
        return mockserver.make_response('OK', 200)

    router = 'car'
    body = {
        'selector_settings': {},
        'query_settings': {
            'path': [[58, 35], [58.1, 35.1], [58.1, 35.1]],
            'source_direction': 135,
            'router_settings': {},
            'query_settings': {},
            'execution_settings': {},
        },
    }
    await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_route_info', json=body,
    )
    assert maps_summary_mock.times_called == 1
