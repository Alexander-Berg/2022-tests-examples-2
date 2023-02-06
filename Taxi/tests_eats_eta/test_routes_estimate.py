# pylint: disable=import-error
import collections

import pytest
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521
from yamaps_tools import masstransit as yamaps_masstransit  # noqa: F401 C5521

from . import utils


HANDLE = 'v1/eta/routes/estimate'
REDIS_TTL = 100


def to_yamaps(value: float):
    return round(value * 1e6)


def parse_point(point_str):
    lon, lat = map(float, point_str.split(','))
    return {'lon': lon, 'lat': lat}


def parse_rll(rll):
    return [parse_point(point_str) for point_str in rll.split('~')]


def _proto_masstransit_summary(time, distance):
    return yamaps_masstransit.proto_summary_time_distance(
        time=time, distance=distance,
    )


def _proto_car_summary(time, distance):
    data = {'time': time, 'distance': distance}
    return yamaps_driving.proto_driving_summary(data)


def mock_router(mockserver, transport_type, route_info):
    mock_url_by_transport = {
        'car': '/maps-router/v2/summary',
        'pedestrian': '/maps-pedestrian-router/pedestrian/v2/summary',
    }
    serializer_by_transport = {
        'car': _proto_car_summary,
        'pedestrian': _proto_masstransit_summary,
    }

    class RouterMock:
        def __init__(self):
            self.responses = collections.defaultdict(int)
            self._do_mock_router()

        def reset_responses(self):
            self.responses.clear()

        def _do_mock_router(self):
            @mockserver.handler(mock_url_by_transport[transport_type])
            def _mock(request):
                assert request.method == 'GET'
                path = parse_rll(request.query['rll'])
                assert len(path) == 2
                for edge_info in route_info:
                    if path == [edge_info['src'], edge_info['dst']]:
                        response = mockserver.make_response(
                            response=serializer_by_transport[transport_type](
                                time=edge_info['time'],
                                distance=edge_info['distance'],
                            ),
                            status=200,
                            content_type='application/x-protobuf',
                        )
                        break
                else:
                    response = mockserver.make_response(status=500)
                self.responses[response.status] += 1
                return response

            self.handler = _mock

    return RouterMock()


@utils.eats_eta_route_estimation_router_settings(redis_ttl=100)
@pytest.mark.parametrize(
    'test_file',
    [
        'linear_fallback.json',
        'car_router.json',
        'pedestrian_router.json',
        'car_router_no_waiting.json',
        'car_router_multipoints.json',
    ],
)
async def test_actions_sequences_estimate_200(
        experiments3,
        mockserver,
        taxi_eats_eta,
        load_json,
        test_file,
        mocked_time,
):
    testcase = load_json(test_file)
    experiments3.add_experiment3_from_marker(
        utils.eats_eta_route_estimation_estimation_settings(
            **testcase['config_estimations'],
        ),
        None,
    )
    routers = {}
    for route in testcase['routes']:
        courier_transport_type = route['courier_transport_type']
        routers[courier_transport_type] = mock_router(
            mockserver, courier_transport_type, testcase['route_info'],
        )

    response = await taxi_eats_eta.post(
        HANDLE, json={'routes': testcase['routes']},
    )
    assert response.status == 200

    response_body = response.json()
    assert (
        response_body['routes_estimations'] == testcase['routes_estimations']
    )
    router_errors = {
        key: router.responses[500] for key, router in routers.items()
    }
    for router in routers.values():
        assert (
            router.handler.times_called
            == router.responses[200] + router.responses[500]
            > 0
        )
        router.reset_responses()

    response = await taxi_eats_eta.post(
        HANDLE, json={'routes': testcase['routes']},
    )
    assert response.status == 200
    assert response.json() == response_body

    for key, router in routers.items():
        assert router.handler.times_called > 0
        # успешные ответы роутера кешируются
        assert router.responses[200] == 0
        # фолбечные значения не кешируются
        assert router.responses[500] == router_errors[key]
        router.reset_responses()


@pytest.mark.parametrize(
    'request_file', ['duplicate_route_ids.json', 'missing_action_key.json'],
)
async def test_actions_sequences_estimate_400(
        taxi_eats_eta, load_json, request_file,
):
    response = await taxi_eats_eta.post(HANDLE, json=load_json(request_file))
    assert response.status == 400
