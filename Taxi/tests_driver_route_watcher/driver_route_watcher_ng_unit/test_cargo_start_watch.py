import json  # noqa: F401

import pytest


POINTS = [
    [37.451695, 55.723917],
    [37.473896, 55.728358],
    [37.518952, 55.736290],
]


@pytest.mark.servicetest
async def test_cargo_start_watch_200(driver_route_watcher_ng_adv, mockserver):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/route')
    def _mock_route(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('pedestrian_maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    drw = driver_route_watcher_ng_adv

    dbid_uuid = 'dbid_uuid'
    body = {
        'courier': dbid_uuid,
        'path': [
            {
                'point': POINTS[0],
                'wait_time': 60,
                'park_time': 0,
                'order_id': 'order-id-111111',
                'point_id': 'point-id-111111',
            },
            {
                'point': POINTS[1],
                'wait_time': 61,
                'park_time': 0,
                'order_id': 'order-id-111112',
                'point_id': 'point-id-111112',
            },
            {
                'point': POINTS[2],
                'wait_time': 62,
                'park_time': 0,
                'order_id': 'order-id-111111',
                'point_id': 'point-id-111113',
            },
        ],
    }

    response = await drw.post('cargo/start-watch', json=body)
    assert response.status_code == 200


@pytest.mark.servicetest
async def test_cargo_start_watch_with_park_time(
        driver_route_watcher_ng_adv, mockserver,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/route')
    def _mock_route(request):
        # 37.466104,55.727191 -> 37.454099,55.718486
        return mockserver.make_response(
            response=load_binary('pedestrian_maps_response.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    drw = driver_route_watcher_ng_adv

    dbid_uuid = 'dbid_uuid5'
    body = {
        'courier': dbid_uuid,
        'path': [
            {
                'point': POINTS[0],
                'wait_time': 1000,
                'park_time': 10,
                'order_id': 'aaaa1',
                'point_id': 'bbbb1',
            },
            {
                'point': POINTS[1],
                'wait_time': 2000,
                'park_time': 20,
                'order_id': 'aaaa2',
                'point_id': 'bbbb2',
            },
            {
                'point': POINTS[2],
                'wait_time': 4000,
                'park_time': 30,
                'order_id': 'aaaa3',
                'point_id': 'bbbb3',
            },
        ],
    }

    response = await drw.post('cargo/start-watch', json=body)
    assert response.status_code == 200
