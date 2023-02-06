# pylint: disable=import-error
import pytest

import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


def _proto_masstransit_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


def _proto_driving_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


async def test_calculate_eta_pedestrian(taxi_cargo_eta, mockserver):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian(request):
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_masstransit_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_cargo_eta.post(
        'v1/calculate-eta',
        json={
            'source': [37.683000, 55.774000],
            'destination': [37.656000, 55.764000],
            'transport_type': 'pedestrian',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'eta': {'distance': 2500.0, 'time': 2500.0}}

    assert _mock_pedestrian.times_called == 1


async def test_calculate_eta_car(taxi_cargo_eta, mockserver):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_cargo_eta.post(
        'v1/calculate-eta',
        json={
            'source': [37.632509, 55.774674],
            'destination': [37.63223287, 55.76815715],
            'transport_type': 'car',
            'zone_id': 'moscow',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'eta': {'distance': 2500.0, 'time': 2500.0}}

    assert _mock_router.times_called == 1


async def test_calculate_eta_wrong_transport(taxi_cargo_eta, mockserver):
    response = await taxi_cargo_eta.post(
        'v1/calculate-eta',
        json={
            'source': [37.683000, 55.774000],
            'destination': [37.656000, 55.764000],
            'transport_type': 'taxi',
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        'code': 'unknown_transport_type',
        'message': 'Don\'t know which router to use for type taxi',
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_eta_transport_to_router_type',
    consumers=['cargo-eta/calculate-eta'],
    clauses=[],
    default_value={
        'enabled': True,
        'router_info': {
            'router_type': 'pedestrian',
            'multiplier': 3.5,
            'additional_in_sec': 42,
        },
    },
)
async def test_calculate_eta_change_router(taxi_cargo_eta, mockserver):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian(request):
        data = {'time': 250, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_masstransit_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_cargo_eta.post(
        'v1/calculate-eta',
        json={
            'source': [37.683000, 55.774000],
            'destination': [37.656000, 55.764000],
            'transport_type': 'taxi',
        },
    )

    assert response.status_code == 200
    # expected: time * multiplier + additional_in_sec
    assert response.json() == {'eta': {'distance': 2500.0, 'time': 917.0}}
    assert _mock_pedestrian.times_called == 1
