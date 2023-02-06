# pylint: disable=import-only-modules, import-error, redefined-outer-name

import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


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


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.07',
    'X-YaTaxi-Park-Id': '111',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'Accept-Language': 'ru',
}


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
    },
)
@pytest.mark.parametrize(
    'shuttle_id,response_code',
    [
        ('VlAK13MzaLx6Bmnd', 200),
        ('gkZxnYQ73QGqrKyz', 200),
        ('Pmp80rQ23L4wZYxd', 200),
        ('Pmp80rQ23L4wZYxd', 200),
        ('bjoAWlMYJRG14Nnm', 200),
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        load,
        load_json,
        shuttle_id,
        response_code,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(5000, 10000),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
                {
                    'position': {
                        'lon': 30.5,
                        'lat': 60.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid4_uuid4',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        req = json.loads(request.get_data())
        assert req['extra'] == {
            'providers': {
                'discounts': {'is_enabled': False},
                'router': {'is_fallback': True},
                'surge': {'is_enabled': False},
            },
            'shuttle_params': {'is_street_hail_booking': True},
        }

        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 45, 'meta': {}},
                    'user': {'total': 45, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.get(
        '/driver/v1/shuttle-control/v1/street_hailing/stops_ahead',
        headers=HEADERS,
        params={'shuttle_id': shuttle_id},
    )
    assert response.status_code == 200

    if shuttle_id == 'gkZxnYQ73QGqrKyz':
        assert mock_router.times_called == 4
        assert response.json() == {
            'route_name': 'route1',
            'stops': [
                {
                    'hint': {'title': 'Мест нет'},
                    'num_passengers': 0,
                    'stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                    'stop_name': 'stop4',
                },
                {
                    'hint': {'title': 'Мест нет'},
                    'num_passengers': 0,
                    'stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'stop_name': 'stop5',
                },
                {
                    'hint': {'title': 'Мест нет'},
                    'num_passengers': 0,
                    'stop_id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
                    'stop_name': 'stop1',
                },
                {
                    'hint': {'title': 'Мест нет'},
                    'num_passengers': 0,
                    'stop_id': 'shuttle-stop-Pmp80rQ23L4wZYxd',
                    'stop_name': 'stop_2',
                },
            ],
        }

    elif shuttle_id == 'Pmp80rQ23L4wZYxd':
        assert mock_router.times_called == 5
        assert response.json() == {
            'route_name': 'route1',
            'stops': [
                {
                    'hint': {'subtitle': '4 мест', 'title': '45 руб.'},
                    'num_passengers': 4,
                    'stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'stop_name': 'stop5',
                },
                {
                    'hint': {'subtitle': '4 мест', 'title': '45 руб.'},
                    'num_passengers': 4,
                    'stop_id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
                    'stop_name': 'stop1',
                },
                {
                    'hint': {'subtitle': '4 мест', 'title': '45 руб.'},
                    'num_passengers': 4,
                    'stop_id': 'shuttle-stop-Pmp80rQ23L4wZYxd',
                    'stop_name': 'stop_2',
                },
                {
                    'hint': {'subtitle': '4 мест', 'title': '45 руб.'},
                    'num_passengers': 4,
                    'stop_id': 'shuttle-stop-80vm7DQm7Ml24ZdO',
                    'stop_name': 'stop3',
                },
            ],
        }

    elif shuttle_id == 'VlAK13MzaLx6Bmnd':
        assert mock_router.times_called == 3
        assert response.json() == {
            'route_name': 'route1',
            'stops': [
                {
                    'hint': {'subtitle': '4 мест', 'title': '45 руб.'},
                    'num_passengers': 4,
                    'stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                    'stop_name': 'stop4',
                },
                {
                    'hint': {'subtitle': '2 мест', 'title': '45 руб.'},
                    'num_passengers': 2,
                    'stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'stop_name': 'stop5',
                },
                {
                    'hint': {'title': 'Мест нет'},
                    'num_passengers': 0,
                    'stop_id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
                    'stop_name': 'stop1',
                },
                {
                    'hint': {'title': 'Мест нет'},
                    'num_passengers': 0,
                    'stop_id': 'shuttle-stop-Pmp80rQ23L4wZYxd',
                    'stop_name': 'stop_2',
                },
            ],
        }

    elif shuttle_id == 'bjoAWlMYJRG14Nnm':
        assert mock_router.times_called == 0
        assert response.json() == {'route_name': 'route1', 'stops': []}

    else:
        assert 0
