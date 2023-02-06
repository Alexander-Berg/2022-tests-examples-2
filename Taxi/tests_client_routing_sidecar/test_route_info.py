import json

import pytest


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
async def test_route_info_response_check(
        taxi_client_routing_sidecar, mockserver,
):
    router = 'car'
    body = {
        'selector_settings': {},
        'query_settings': {
            'path': [[58, 35], [58.1, 35.1], [58.2, 35.2]],
            'source_direction': 135,
            'router_settings': {},
            'query_settings': {},
            'execution_settings': {},
        },
    }
    response = await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_route_info', json=body,
    )
    print(response.content.decode())
    assert response.status_code == 200, response.content.decode()
    response_object = json.loads(response.content.decode())

    assert response_object == {
        'result': {'distance': 28733.704719471043, 'time': 4137},
    }


async def test_route_info_map_request_check(
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


@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['google']}], ROUTER_GOOGLE_ENABLED=True,
)
async def test_route_info_google_request_check(
        taxi_client_routing_sidecar, mockserver,
):
    @mockserver.handler('/maps-google-router/google/maps/api/directions/json')
    def maps_google_mock(data):
        assert data.url.find('TEST_GOOGLE_KEY') != -1
        return mockserver.make_response('OK', 200)

    router = 'car'
    body = {
        'selector_settings': {},
        'query_settings': {
            'path': [[58, 35], [58.1, 35.1], [58.1, 35.1]],
            'source_direction': 135,
            'router_settings': {},
            'query_settings': {
                'external_api_keys': {'google_api_key': 'TEST_GOOGLE_KEY'},
            },
            'execution_settings': {},
        },
    }
    await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_route_info', json=body,
    )
    assert maps_google_mock.times_called == 1
