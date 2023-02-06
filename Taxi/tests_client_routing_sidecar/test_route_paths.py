import json

import pytest


@pytest.mark.config(ROUTER_SELECT=[{'routers': ['linear-fallback']}])
async def test_route_paths_response_check(
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
        f'/router/{router}/fetch_route_paths', json=body,
    )
    assert response.status_code == 200, response.content.decode()

    response_object = json.loads(response.content.decode())
    assert response_object == {
        'result': [
            {
                'info': {'distance': 28733.704719471043, 'time': 4137},
                'legs': [0, 1],
                'path': [
                    {
                        'distance_since_ride_start': 0.0,
                        'position': [58.0, 35.0],
                        'time_since_ride_start': 0,
                    },
                    {
                        'distance_since_ride_start': 14370.3855051965,
                        'position': [58.1, 35.1],
                        'time_since_ride_start': 2069,
                    },
                    {
                        'distance_since_ride_start': 28733.704719471043,
                        'position': [58.2, 35.2],
                        'time_since_ride_start': 4137,
                    },
                ],
                'request_id': '',
                'route_id': '',
            },
        ],
    }


async def test_route_paths_map_request_check(
        taxi_client_routing_sidecar, mockserver,
):
    @mockserver.handler('/maps-router/v2/route')
    def maps_route_mock(data):
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
        f'/router/{router}/fetch_route_path', json=body,
    )
    assert maps_route_mock.times_called == 1
