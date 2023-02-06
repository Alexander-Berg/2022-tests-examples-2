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
            'srcs': [[58, 35], [58.2, 35.2]],
            'dsts': [[58.1, 35.1], [58.3, 35.3]],
        },
    }
    response = await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_matrix_info', json=body,
    )
    print(response.content.decode())
    assert response.status_code == 200, response.content.decode()
    response_object = json.loads(response.content.decode())

    assert response_object == {
        'result': [
            [
                {
                    'route_info': {'time': 2069, 'distance': 14370.3855051965},
                    'dst_point_idx': 0,
                    'src_point_idx': 0,
                },
                {
                    'route_info': {'time': 6204, 'distance': 43089.9082268317},
                    'dst_point_idx': 1,
                    'src_point_idx': 0,
                },
            ],
            [
                {
                    'route_info': {
                        'time': 2068,
                        'distance': 14363.31921427453,
                    },
                    'dst_point_idx': 0,
                    'src_point_idx': 1,
                },
                {
                    'route_info': {
                        'time': 2067,
                        'distance': 14356.240601486135,
                    },
                    'dst_point_idx': 1,
                    'src_point_idx': 1,
                },
            ],
        ],
    }


async def test_route_infocar__map_request_check(
        taxi_client_routing_sidecar, mockserver,
):
    @mockserver.handler('/maps-matrix-router/v2/matrix')
    def maps_matrix_mock(data):
        return mockserver.make_response('OK', 200)

    router = 'car'
    body = {
        'selector_settings': {},
        'query_settings': {
            'srcs': [[58, 35], [58.2, 35.2]],
            'dsts': [[58.1, 35.1], [58.3, 35.3]],
        },
    }
    await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_matrix_info', json=body,
    )
    assert maps_matrix_mock.times_called == 1


async def test_route_info_bicycle_map_request_check(
        taxi_client_routing_sidecar, mockserver,
):
    @mockserver.handler('/maps-bicycle-matrix-router/v2/matrix')
    def maps_matrix_mock(data):
        return mockserver.make_response('OK', 200)

    router = 'bicycle'
    body = {
        'selector_settings': {},
        'query_settings': {
            'srcs': [[58, 35], [58.2, 35.2]],
            'dsts': [[58.1, 35.1], [58.3, 35.3]],
        },
    }
    await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_matrix_info', json=body,
    )
    assert maps_matrix_mock.times_called == 1


async def test_route_pedestrian_map_request_check(
        taxi_client_routing_sidecar, mockserver,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/matrix')
    def maps_matrix_mock(data):
        return mockserver.make_response('OK', 200)

    router = 'pedestrian'
    body = {
        'selector_settings': {},
        'query_settings': {
            'srcs': [[58, 35], [58.2, 35.2]],
            'dsts': [[58.1, 35.1], [58.3, 35.3]],
        },
    }
    await taxi_client_routing_sidecar.post(
        f'/router/{router}/fetch_matrix_info', json=body,
    )
    assert maps_matrix_mock.times_called == 1
