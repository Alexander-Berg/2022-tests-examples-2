# flake8: noqa
# pylint: disable=import-error,wildcard-import
from geobus_tools import geobus  # noqa: F401 C5521

import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
from tests_plugins import utils

import pytest


def _rll_to_array(rll):
    raw_points = rll.split('~')
    string_points = [p.split(',') for p in raw_points]
    return [[float(x), float(y)] for x, y in string_points]


def _proto_driving_summary(time, distance):
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


POSITIONS_CHANNEL = 'channel:yagr:position'


@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_ROUTE_WATCHER_ENABLE_ORDER_CORE_VERIFY=True,
    DRIVER_ROUTE_RESPONDER_ENABLE_TIMELEFT_FROM_CACHE=True,
    DRIVER_ROUTE_RESPONDER_EXTENDED_FUNCTIONALITY={
        'chain_verification': True,
        'filter_finished_or_cancelled': True,
        'drw_start_watch': True,
    },
)
async def test_timeleft_drw_start_watch(
        driver_route_responder_adv, mockserver, now, load_binary,
):
    transporting_points = [
        [37.451695, 55.723917],
        [37.473896, 55.728358],
        [37.518952, 55.736290],
    ]
    source = [37.4516, 55.7239]
    raw_position = [37.455596, 55.719463]
    destinations = transporting_points

    driver_id = 'driver0dbid_driver0uuid'
    order_id = 'orderid123'

    request_body = {
        'driver': driver_id,
        'meta': {'some-field': 123, 'some-other-field': 'hello'},
        'with_route': True,
        'mode': 'sharedroute',
        'order_id': order_id,
    }

    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': raw_position,
            'direction': 45,
            'unix_time': timestamp * 1000,
            'speed': 11,
            'accuracy': 1,
            'source': 'AndroidGps',
            'timestamp': timestamp,
        },
    ]
    message = geobus.serialize_positions_v2(drivers, now)

    @mockserver.json_handler('/maps-router/v2/summary')
    def _mock_router_summary(request):
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        rll = _rll_to_array(request.args['rll'])
        assert rll == [raw_position] + destinations
        return mockserver.make_response(
            response=load_binary(
                'maps_response-37.455596,55.719463'
                '~37.451695,55.723917~'
                '37.473896,55.728358~'
                '37.518952,55.73629.pb',
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_core(request):
        del request
        proc_destinations = [{'geopoint': x} for x in destinations]
        return mockserver.make_response(
            json={
                'fields': {
                    'order': {
                        'taxi_status': 'transporting',
                        'status': 'assigned',
                        'request': {
                            'source': {'geopoint': source},
                            'destinations': proc_destinations,
                        },
                    },
                    'destinations_statuses': [False, False],
                },
                'order_id': order_id,
                'replica': 'master',
                'version': '5',
            },
            status=200,
        )

    @mockserver.json_handler('/driver-route-watcher/start-watch')
    def _mock_drw_start_watch(request):
        assert request.json == {
            'driver': {'uuid': 'driver0uuid', 'dbid': 'driver0dbid'},
            'destination_point': destinations[-1],
            'destinations': destinations,
            'metainfo': {
                'order_id': 'orderid123',
                'taxi_status': 'transporting',
            },
            'router_type': 'car',
            'toll_roads': False,
            'service_id': 'processing:transporting',
        }
        return mockserver.make_response(status=200)

    await driver_route_responder_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )

    response = await driver_route_responder_adv.post(
        '/timeleft', json=request_body,
    )
    assert response.status_code == 200
    assert _mock_drw_start_watch.times_called == 1
