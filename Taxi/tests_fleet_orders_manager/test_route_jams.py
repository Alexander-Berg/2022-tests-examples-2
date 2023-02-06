# pylint: disable=import-error
import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary

ENDPOINT = '/v1/route_jams'

GEOPOINTS = [[37.455434, 55.719436], [37.451695, 55.723917]]


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


@pytest.mark.parametrize('is_jams', [True, False])
async def test_routing(taxi_fleet_orders_manager, mockserver, is_jams):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        data = {'time': 2500, 'distance': 2500}
        return mockserver.make_response(
            response=_proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    request_body = {'is_jams': is_jams, 'geopoints': GEOPOINTS}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request_body,
    )

    assert response.status_code == 200
    assert response.json()['time'] == 2500
    assert response.json()['distance'] == 2500


@pytest.mark.parametrize('is_jams', [True, False])
async def test_routing_disabled(
        taxi_fleet_orders_manager, mockserver, is_jams,
):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    request_body = {'is_jams': is_jams, 'geopoints': GEOPOINTS}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=request_body,
    )

    assert response.status_code == 500
