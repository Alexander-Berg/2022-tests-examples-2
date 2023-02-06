# pylint: disable=import-error

import pytest
from yamaps_tools import driving as yamaps_driving  # noqa: F401 C5521
from yamaps_tools import masstransit as yamaps_masstransit  # noqa: F401 C5521


def _proto_masstransit_summary(time, distance):
    return yamaps_masstransit.proto_summary_time_distance(
        time=time, distance=distance,
    )


def _proto_car_summary(time, distance):
    data = {'time': time, 'distance': distance}
    return yamaps_driving.proto_driving_summary(data)


@pytest.mark.experiments3(filename='eats-eta-routers.json')
@pytest.mark.parametrize('transport_type', ['car', 'bicycle'])
async def test_eta_router_multiple_routers(
        taxi_eats_eta, mockserver, transport_type,
):
    mock_url_by_transport = {
        'car': '/maps-router/v2/summary',
        'bicycle': '/maps-pedestrian-router/pedestrian/v2/summary',
    }
    serializer_by_transport = {
        'car': _proto_car_summary,
        'bicycle': _proto_masstransit_summary,
    }

    @mockserver.handler(mock_url_by_transport[transport_type])
    def _mock_route_jams(request):
        return mockserver.make_response(
            response=serializer_by_transport[transport_type](
                time=2500, distance=2500,
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_eats_eta.post(
        'v2/eta',
        json={
            'sources': [
                {
                    'position': [37.683000, 55.774000],
                    'zone_id': 'moscow',
                    'transport_type': transport_type,
                },
            ],
            'destination': {'position': [37.656000, 55.764000]},
        },
    )

    assert response.status_code == 200
    assert response.json() == {'etas': [{'distance': 2500.0, 'time': 2500.0}]}


@pytest.mark.experiments3(filename='eats-eta-routers.json')
async def test_eta_caching(taxi_eats_eta, mockserver):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_route_jams(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=1700, distance=2500),
            status=200,
            content_type='application/x-protobuf',
        )

    for _ in range(1, 3):
        response = await taxi_eats_eta.post(
            'v2/eta',
            json={
                'sources': [
                    {
                        'position': [37.683000, 55.774000],
                        'zone_id': 'moscow',
                        'transport_type': 'bicycle',
                    },
                ],
                'destination': {'position': [37.656000, 55.764000]},
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            'etas': [{'distance': 2500.0, 'time': 1700.0}],
        }

    # Check that subsequent calls are processed by cache
    assert _mock_route_jams.times_called == 1


@pytest.mark.config(
    ROUTER_MASSTRANSIT_MAPS_ENABLED=True,
)  # turn on masstransit router
@pytest.mark.experiments3(filename='eats-eta-routers.json')
async def test_eta_take_fastest_for_multiple_routers(
        taxi_eats_eta, mockserver,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=2500, distance=2500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/masstransit/v2/summary')
    def _mock_masstransit(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=1200, distance=2500),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_eats_eta.post(
        'v2/eta',
        json={
            'sources': [
                {
                    'position': [37.683000, 55.774000],
                    'zone_id': 'moscow',
                    'transport_type': 'pedestrian',
                },
            ],
            'destination': {'position': [37.656000, 55.764000]},
        },
    )

    assert response.status_code == 200
    assert response.json() == {'etas': [{'distance': 2500.0, 'time': 1200.0}]}
    assert _mock_pedestrian.times_called == 1
    assert _mock_masstransit.times_called == 1


@pytest.mark.experiments3(
    name='eats_eta_correctors_dropoff',
    consumers=['eats-eta-correctors/dropoff'],
    default_value={'multiplier': 2.0, 'summand': 12},
    is_config=True,
)
@pytest.mark.experiments3(
    name='eats_eta_correctors_pickup',
    consumers=['eats-eta-correctors/pickup'],
    default_value={'multiplier': 3.0, 'summand': 14},
    is_config=True,
)
@pytest.mark.experiments3(
    name='eats_eta_routers',
    consumers=['eats-eta/v2/eta'],
    default_value={'routers': ['pedestrian']},
    is_config=True,
)
@pytest.mark.parametrize(
    'should_apply,point_type,expected_time',
    [
        (True, 'dropoff', 2 * 2500 + 12),
        (True, 'pickup', 3 * 2500 + 14),
        (False, 'dropoff', 2500),
        (False, 'pickup', 2500),
    ],
)
async def test_eta_linear_correction(
        taxi_eats_eta, mockserver, should_apply, point_type, expected_time,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(time=2500, distance=2500),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_eats_eta.post(
        'v2/eta',
        json={
            'sources': [
                {
                    'position': [37.683000, 55.774000],
                    'zone_id': 'moscow',
                    'transport_type': 'pedestrian',
                },
            ],
            'destination': {
                'position': [37.656000, 55.764000],
                'type': point_type,
            },
            'apply-correctors': should_apply,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'etas': [{'distance': 2500.0, 'time': expected_time}],
    }


async def test_eta_linear_correction_bad_request(taxi_eats_eta):
    response = await taxi_eats_eta.post(
        'v2/eta',
        json={
            'sources': [
                {
                    'position': [37.683000, 55.774000],
                    'zone_id': 'moscow',
                    'transport_type': 'pedestrian',
                },
            ],
            'destination': {'position': [37.656000, 55.764000]},
            'apply-correctors': True,
        },
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'NO_DEST_TYPE'
