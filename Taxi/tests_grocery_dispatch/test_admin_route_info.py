# pylint: disable=import-error, import-only-modules
import pytest
import yandex.maps.proto.bicycle.summary_pb2 as ProtoBicycleSummary
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary

from tests_grocery_dispatch.plugins.models import OrderInfo


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


def _proto_masstransit_summary(summary):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = summary['time']
    item.weight.time.text = ''
    item.weight.walking_distance.value = summary['distance']
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


def _proto_bicycle_summary(summary):
    time = summary['time']
    distance = summary['distance']
    response = ProtoBicycleSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    return response.SerializeToString()


@pytest.mark.parametrize(
    ['transport'], [[None], [['pedestrian']], [['car', 'bicycle']]],
)
async def test_admin_route_info_400(taxi_grocery_dispatch, transport):
    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/route_info', json={'transport': transport},
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    ['req_body'],
    [
        [{'dispatch_id': '00000000-0000-0000-0000-000000000000'}],
        [{'order_id': 'not_existed_order_id'}],
    ],
)
@pytest.mark.parametrize(
    ['transport'], [[None], [['pedestrian']], [['car', 'bicycle']]],
)
async def test_admin_route_info_404(
        taxi_grocery_dispatch, req_body, transport, grocery_dispatch_pg,
):
    grocery_dispatch_pg.create_dispatch()

    req_body.update({'transport': transport})
    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/route_info', json=req_body,
    )
    assert response.status_code == 404


@pytest.mark.config(ROUTER_BICYCLE_MAPS_ENABLED=True)
@pytest.mark.parametrize(
    ['req_body'],
    [
        [{'dispatch_id': '00000000-0000-0000-0000-000000000000'}],
        [{'order_id': 'not_existed_order_id'}],
    ],
)
@pytest.mark.parametrize(
    ['transport'], [[None], [['pedestrian']], [['car', 'bicycle']]],
)
async def test_admin_route_info_200(
        taxi_grocery_dispatch,
        mockserver,
        req_body,
        transport,
        grocery_dispatch_pg,
):
    grocery_dispatch_pg.create_dispatch(
        dispatch_id=req_body.get(
            'dispatch_id', '11111111-1111-1111-1111-111111111111',
        ),
        order=OrderInfo(order_id=req_body.get('order_id', 'some_order_id')),
    )

    route_responses = {
        'car': {'time': 1800, 'distance': 9456},
        'pedestrian': {'time': 1732, 'distance': 2314},
        'bicycle': {'time': 345, 'distance': 5614},
    }

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_car_router(request):
        data = route_responses['car']
        return mockserver.make_response(
            response=_proto_driving_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        data = route_responses['pedestrian']
        return mockserver.make_response(
            response=_proto_masstransit_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-bicycle-router/v2/summary')
    def _mock_bicycle_router(request):
        data = route_responses['bicycle']
        return mockserver.make_response(
            response=_proto_bicycle_summary(data),
            status=200,
            content_type='application/x-protobuf',
        )

    req_body.update({'transport': transport})
    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/route_info', json=req_body,
    )
    assert response.status_code == 200

    if transport is None:
        transport = ['pedestrian', 'car', 'bicycle']
    transport = set(transport)

    for route in response.json()['routes']:
        transp = route.pop('transport')
        assert transp in transport
        assert route == route_responses[transp]
        transport.remove(transp)
    assert not transport
