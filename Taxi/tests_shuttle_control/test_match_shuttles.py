# pylint: disable=import-error,too-many-lines,import-only-modules
import datetime
import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary

from tests_shuttle_control.utils import select_named


ROUTER_TIMES = {'37.643024,55.734742': 60, '37.643150,55.734754': 70}


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


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.parametrize(
    'router_time,pedestrian_time,pedestrian_distance'
    ',is_ok,sort_order,passengers_count,payment',
    [
        (91, 30, 10, False, 'less_is_better', None, None),
        (60, 50, 10, False, 'less_is_better', 1, None),
        (26, 30, 10, False, 'less_is_better', 1, None),
        (50, 30, 21, False, 'less_is_better', None, None),
        (
            50,
            30,
            10,
            True,
            'less_is_better',
            None,
            {'type': 'cash', 'payment_method_id': None},
        ),
        (
            50,
            30,
            10,
            True,
            'less_is_better',
            None,
            {'type': 'card', 'payment_method_id': '987654321'},
        ),
        (50, 30, 10, True, 'greater_is_better', 2, None),
        (50, 30, 10, True, 'less_is_better', None, None),
    ],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_couple_shuttle(
        taxi_shuttle_control,
        taxi_shuttle_control_monitor,
        mockserver,
        pgsql,
        load,
        load_json,
        taxi_config,
        experiments3,
        router_time,
        pedestrian_time,
        pedestrian_distance,
        is_ok,
        sort_order,
        passengers_count,
        payment,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
            'formula': {
                'sort_order': sort_order,
                'coeff_walk_pickup_time': 0,
                'coeff_walk_dropoff_time': 0,
                'coeff_shuttle_eta': 10,
                'coeff_user_wait_time': 0,
                'coeff_shuttle_ride_time': 0,
                'coeff_walk_ab_time': 0,
                'coeff_car_ab_time': 0,
            },
        },
        clauses=[],
    )

    queries = [load('main.sql')]
    pgsql['shuttle_control'].apply_queries(queries)

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(router_time, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(
                pedestrian_time, pedestrian_distance,
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    max_walk_time = 40
    max_walk_distance = 20
    request_json = {
        'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
        'match_params': {
            'pickup_limits': {
                'max_walk_time': max_walk_time,
                'max_walk_distance': max_walk_distance,
            },
            'dropoff_limits': {
                'max_walk_time': max_walk_time,
                'max_walk_distance': max_walk_distance,
            },
            'max_wait_time': 60,
        },
        'payment': payment,
    }
    if passengers_count is not None:
        request_json['passengers_count'] = passengers_count
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json=request_json,
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200

    if is_ok:
        resp = response.json()

        offer_id_3 = resp['matched_shuttles'][0]['offer_id']

        del resp['matched_shuttles'][0]['offer_id']
        del resp['matched_shuttles'][0]['base_match_info']['offer_id']

        expected_price = 35 * (passengers_count if passengers_count else 1)

        expected = [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 50,
                    },
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {
                        'time': pedestrian_time,
                        'distance': pedestrian_distance,
                    },
                    'from_dropoff_stop': {
                        'time': pedestrian_time,
                        'distance': pedestrian_distance,
                    },
                },
                'price': {'currency': 'RUB', 'total': expected_price},
            },
        ]

        assert resp == {'matched_shuttles': expected}

        assert mock_router.times_called == 5

        metrics = await taxi_shuttle_control_monitor.get_metric(
            'shuttle-matching-statistics',
        )
        expected_metrics = {
            '$meta': {
                'solomon_children_labels': 'shuttle-matching-statistics',
            },
            'matches': {
                'total': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 1,
                },
                'successful': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 1,
                },
                '$meta': {'solomon_children_labels': 'matching-status'},
            },
            'mismatches': {
                'no_shuttle_state': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'too_far_matches': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'too_far_dropoff': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'no_available_seats': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 1,
                },
                'blacklisted_pickup_stop': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'blacklisted_dropoff_stop': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'no_pedestrian_info': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'invalid_pickup_time': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'invalid_dropoff_time': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'no_pickup_eta': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'too_long_eta': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                '$meta': {'solomon_children_labels': 'matching-status'},
            },
        }
        assert metrics == expected_metrics

        rows = select_named(
            'SELECT * FROM state.matching_offers ORDER BY offer_id',
            pgsql['shuttle_control'],
        )
        assert rows == sorted(
            [
                {
                    'shuttle_id': 1,
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda26ac',
                    'route_id': 1,
                    'yandex_uid': '0123456789',
                    'order_point_a': '(30,60)',
                    'order_point_b': '(31,61)',
                    'pickup_stop_id': 1,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 2,
                    'dropoff_lap': 1,
                    'price': '(10.0000,RUB)',
                    'passengers_count': 1,
                    'created_at': datetime.datetime(2020, 1, 17, 18),
                    'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': None,
                    'payment_method_id': None,
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
                {
                    'shuttle_id': 1,
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda21ac',
                    'route_id': 1,
                    'yandex_uid': '0123456789',
                    'order_point_a': '(30,60)',
                    'order_point_b': '(31,61)',
                    'pickup_stop_id': 1,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 2,
                    'dropoff_lap': 1,
                    'price': '(10.0000,RUB)',
                    'passengers_count': 1,
                    'created_at': datetime.datetime(2020, 1, 17, 18),
                    'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': None,
                    'payment_method_id': None,
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
                {
                    'shuttle_id': 1,
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                    'route_id': 1,
                    'yandex_uid': '0123456789',
                    'order_point_a': '(30,60)',
                    'order_point_b': '(31,61)',
                    'pickup_stop_id': 1,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 2,
                    'dropoff_lap': 1,
                    'price': '(10.0000,RUB)',
                    'passengers_count': 1,
                    'created_at': datetime.datetime(2020, 1, 17, 18),
                    'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': None,
                    'payment_method_id': None,
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
                {
                    'shuttle_id': 1,
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
                    'route_id': 1,
                    'yandex_uid': '0123456789',
                    'order_point_a': '(30,60)',
                    'order_point_b': '(31,61)',
                    'pickup_stop_id': 1,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 2,
                    'dropoff_lap': 1,
                    'price': '(10.0000,RUB)',
                    'passengers_count': 1,
                    'created_at': datetime.datetime(2020, 1, 17, 18),
                    'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': None,
                    'payment_method_id': None,
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
                {
                    'shuttle_id': 1,
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda24ac',
                    'route_id': 1,
                    'yandex_uid': '0123456789',
                    'order_point_a': '(30,60)',
                    'order_point_b': '(31,61)',
                    'pickup_stop_id': 1,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 2,
                    'dropoff_lap': 1,
                    'price': '(10.0000,RUB)',
                    'passengers_count': 1,
                    'created_at': datetime.datetime(2020, 1, 17, 18),
                    'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': None,
                    'payment_method_id': None,
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
                {
                    'shuttle_id': 1,
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda25ac',
                    'route_id': 1,
                    'yandex_uid': '0123456789',
                    'order_point_a': '(30,60)',
                    'order_point_b': '(31,61)',
                    'pickup_stop_id': 1,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 2,
                    'dropoff_lap': 1,
                    'price': '(10.0000,RUB)',
                    'passengers_count': 1,
                    'created_at': datetime.datetime(2020, 1, 17, 18),
                    'expires_at': datetime.datetime(2020, 1, 17, 18, 18),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': None,
                    'payment_method_id': None,
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
                {
                    'shuttle_id': 1,
                    'offer_id': offer_id_3,
                    'route_id': 1,
                    'yandex_uid': '0123456785',
                    'order_point_a': '(37.643068,55.734641)',
                    'order_point_b': '(37.64138,55.733464)',
                    'pickup_stop_id': 2,
                    'pickup_lap': 1,
                    'dropoff_stop_id': 4,
                    'dropoff_lap': 1,
                    'price': '(35.0000,RUB)',
                    'passengers_count': (
                        1 if passengers_count is None else passengers_count
                    ),
                    'created_at': datetime.datetime(2020, 5, 28, 12, 29, 58),
                    'expires_at': datetime.datetime(2020, 5, 28, 12, 30, 58),
                    'external_confirmation_code': None,
                    'external_passenger_id': None,
                    'payment_type': (
                        None if payment is None else payment['type']
                    ),
                    'payment_method_id': (
                        None
                        if payment is None
                        else payment['payment_method_id']
                    ),
                    'dropoff_timestamp': None,
                    'pickup_timestamp': None,
                    'suggested_route_view': None,
                    'suggested_traversal_plan': None,
                },
            ],
            key=lambda it: it['offer_id'],
        )

    else:
        resp = response.json()
        assert not resp['matched_shuttles']

        assert mock_router.times_called == 3

        metrics = await taxi_shuttle_control_monitor.get_metric(
            'shuttle-matching-statistics',
        )
        expected_metrics = {
            '$meta': {
                'solomon_children_labels': 'shuttle-matching-statistics',
            },
            'matches': {
                'total': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'successful': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                '$meta': {'solomon_children_labels': 'matching-status'},
            },
            'mismatches': {
                'no_shuttle_state': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'too_far_matches': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'too_far_dropoff': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'no_available_seats': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 3 if passengers_count == 4 else 0,
                },
                'blacklisted_pickup_stop': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'blacklisted_dropoff_stop': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'no_pedestrian_info': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'invalid_pickup_time': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': (
                        0
                        if pedestrian_distance <= max_walk_distance
                        and pedestrian_time <= max_walk_time
                        else 2
                    ),
                },
                'invalid_dropoff_time': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': (
                        0
                        if pedestrian_distance <= max_walk_distance
                        and pedestrian_time <= max_walk_time
                        else 2
                    ),
                },
                'no_pickup_eta': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': 0,
                },
                'too_long_eta': {
                    '$meta': {
                        'solomon_children_labels': 'matching-route-name',
                    },
                    'route1': (
                        2
                        if passengers_count != 4
                        and pedestrian_distance <= max_walk_distance
                        and pedestrian_time <= max_walk_time
                        else 0
                    ),
                },
                '$meta': {'solomon_children_labels': 'matching-status'},
            },
        }
        assert metrics == expected_metrics

    assert mock_pedestrian_router.times_called == 3


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic.sql'])
@pytest.mark.parametrize('max_route_percent', [70, 5])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_cyclic(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        max_route_percent,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': max_route_percent,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.642329,
                        'lat': 55.733802,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.641571, 55.737499], [37.642939, 55.734150]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY offer_id
        """,
        pgsql['shuttle_control'],
    )

    resp = response.json()
    resp['matched_shuttles'].sort(key=lambda x: x['shuttle']['id'])

    if max_route_percent == 5:
        assert rows == sorted(
            [
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda25ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda24ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda26ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
                    'shuttle_id': 1,
                },
            ],
            key=lambda it: it['offer_id'],
        )
        assert resp == {
            'match_error': 'no_available_shuttle',
            'matched_shuttles': [],
        }
    else:
        offer_id_2 = resp['matched_shuttles'][0]['offer_id']
        offer_id_1 = resp['matched_shuttles'][1]['offer_id']

        assert rows == sorted(
            [
                {'offer_id': offer_id_2, 'shuttle_id': 2},
                {'offer_id': offer_id_1, 'shuttle_id': 1},
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda25ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda24ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda26ac',
                    'shuttle_id': 1,
                },
                {
                    'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
                    'shuttle_id': 1,
                },
            ],
            key=lambda it: it['offer_id'],
        )

        assert resp == {
            'matched_shuttles': [
                {
                    'match_type': 'detailed',
                    'base_match_info': {
                        'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                        'dropoff_stop_id': 'stop__2',
                        'route': {
                            'id': 'gkZxnYQ73QGqrKyz',
                            'name': 'route1',
                            'route_time': 50,
                        },
                        'offer_id': offer_id_2,
                    },
                    'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'dropoff_stop_id': 'stop__2',
                    'shuttle': {'id': 'Pmp80rQ23L4wZYxd', 'eta': 50},
                    'walk_routes': {
                        'to_pickup_stop': {'time': 30, 'distance': 10},
                        'from_dropoff_stop': {'time': 30, 'distance': 10},
                    },
                    'price': {'currency': 'RUB', 'total': 35},
                    'offer_id': offer_id_2,
                },
                {
                    'match_type': 'detailed',
                    'base_match_info': {
                        'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                        'dropoff_stop_id': 'stop__2',
                        'route': {
                            'id': 'gkZxnYQ73QGqrKyz',
                            'name': 'route1',
                            'route_time': 50,
                        },
                        'offer_id': offer_id_1,
                    },
                    'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'dropoff_stop_id': 'stop__2',
                    'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 50},
                    'walk_routes': {
                        'to_pickup_stop': {'time': 30, 'distance': 10},
                        'from_dropoff_stop': {'time': 30, 'distance': 10},
                    },
                    'price': {'currency': 'RUB', 'total': 35},
                    'offer_id': offer_id_1,
                },
            ],
        }


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_bookings.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_different_booked_seats(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200

    offer_id = response.json()['matched_shuttles'][0]['offer_id']
    assert response.json() == {
        'matched_shuttles': [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 50,
                    },
                    'offer_id': offer_id,
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'currency': 'RUB', 'total': 35},
                'offer_id': offer_id,
            },
        ],
    }

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY offer_id
        """,
        pgsql['shuttle_control'],
    )
    assert rows == sorted(
        [
            {'offer_id': offer_id, 'shuttle_id': 1},
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda25ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda21ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda24ac',
                'shuttle_id': 1,
            },
        ],
        key=lambda it: it['offer_id'],
    )


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_routes.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_multiple_routes(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
                'max_eta_at_pickup': 50,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    matched_shuttles.sort(key=lambda item: item['shuttle']['id'])
    offer_id_2 = matched_shuttles[0]['offer_id']
    offer_id_1 = matched_shuttles[1]['offer_id']
    assert matched_shuttles == sorted(
        [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': 'stop__4',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_1,
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': 'stop__4',
                'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 35, 'currency': 'RUB'},
                'offer_id': offer_id_1,
            },
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__5',
                    'dropoff_stop_id': 'stop__6',
                    'route': {
                        'id': 'Pmp80rQ23L4wZYxd',
                        'name': 'route2',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_2,
                },
                'pickup_stop_id': 'stop__5',
                'dropoff_stop_id': 'stop__6',
                'shuttle': {'id': 'Pmp80rQ23L4wZYxd', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 35, 'currency': 'RUB'},
                'offer_id': offer_id_2,
            },
        ],
        key=lambda item: item['shuttle']['id'],
    )

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'offer_id': offer_id_2, 'shuttle_id': 2},
        {'offer_id': offer_id_1, 'shuttle_id': 1},
    ]

    assert mock_router.times_called == 5
    assert mock_pedestrian_router.times_called == 5


@pytest.mark.pgsql(
    'shuttle_control', files=['multiple_routes.sql', 'workshifts.sql'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.now('2019-09-14T10:42:00+0000')
async def test_match_multiple_routes_with_workshifts(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1595500920,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1595500920,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        shuttle_category['currency']['name'] = 'USD'
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 100, 'meta': {}},
                    'user': {'total': 100, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
                'max_eta_at_pickup': 50,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    matched_shuttles.sort(key=lambda item: item['shuttle']['id'])
    offer_id_2 = matched_shuttles[0]['offer_id']
    assert matched_shuttles == sorted(
        [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__5',
                    'dropoff_stop_id': 'stop__6',
                    'route': {
                        'id': 'Pmp80rQ23L4wZYxd',
                        'name': 'route2',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_2,
                },
                'pickup_stop_id': 'stop__5',
                'dropoff_stop_id': 'stop__6',
                'shuttle': {'id': 'Pmp80rQ23L4wZYxd', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 100.0, 'currency': 'USD'},
                'offer_id': offer_id_2,
            },
        ],
        key=lambda item: item['shuttle']['id'],
    )

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [{'offer_id': offer_id_2, 'shuttle_id': 2}]

    assert mock_router.times_called == 5
    assert mock_pedestrian_router.times_called == 5


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_routes.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_multiple_routes_with_max_eta_at_pickup(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
                'max_eta_at_pickup': 49,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    assert matched_shuttles == []

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []

    assert mock_router.times_called == 3
    assert mock_pedestrian_router.times_called == 5


@pytest.mark.skip(reason='flapping test')
@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_routes.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_srw_blocked_shuttles(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'immobility'
        """,
    )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    assert matched_shuttles == []

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []

    assert mock_router.times_called == 1
    assert mock_pedestrian_router.times_called == 1


@pytest.mark.skip(reason='flapping test')
@pytest.mark.pgsql('shuttle_control', files=['multiple_routes.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_srw_blocked_shuttles_out_of_workshift(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'out_of_workshift'
        """,
    )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 300,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    assert matched_shuttles == []

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []

    assert mock_router.times_called == 1
    assert mock_pedestrian_router.times_called == 1


@pytest.mark.now('2019-09-14T09:55:00+0000')
@pytest.mark.pgsql(
    'shuttle_control', files=['multiple_routes.sql', 'workshifts.sql'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_srw_blocked_shuttles_out_of_workshift_soft(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_in_workshift',
        consumers=['shuttle-control/match_in_workshift'],
        default_value={'enabled': True},
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.642946,
                        'lat': 55.734979,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid2_uuid2': {
                'position': {
                    'lon': 37.642946,
                    'lat': 55.734979,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'out_of_workshift'
        """,
    )
    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.drivers_workshifts_subscriptions
        SET subscribed_at = '2020-05-28T09:50:00+0000'
        """,
    )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 300,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    matched_shuttles.sort(key=lambda item: item['shuttle']['id'])
    offer_id_1 = matched_shuttles[0]['offer_id']
    offer_id_2 = matched_shuttles[1]['offer_id']

    assert matched_shuttles == sorted(
        [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__5',
                    'dropoff_stop_id': 'stop__6',
                    'route': {
                        'id': 'Pmp80rQ23L4wZYxd',
                        'name': 'route2',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_1,
                },
                'pickup_stop_id': 'stop__5',
                'dropoff_stop_id': 'stop__6',
                'shuttle': {'id': '80vm7DQm7Ml24ZdO', 'eta': 5 * 60},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 35, 'currency': 'RUB'},
                'offer_id': offer_id_1,
            },
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__5',
                    'dropoff_stop_id': 'stop__6',
                    'route': {
                        'id': 'Pmp80rQ23L4wZYxd',
                        'name': 'route2',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_2,
                },
                'pickup_stop_id': 'stop__5',
                'dropoff_stop_id': 'stop__6',
                'shuttle': {'id': 'Pmp80rQ23L4wZYxd', 'eta': 5 * 60},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 35, 'currency': 'RUB'},
                'offer_id': offer_id_2,
            },
        ],
        key=lambda item: item['shuttle']['id'],
    )

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'offer_id': offer_id_1, 'shuttle_id': 3},
        {'offer_id': offer_id_2, 'shuttle_id': 2},
    ]

    assert mock_router.times_called == 4
    assert mock_pedestrian_router.times_called == 5


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_routes.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_multiple_routes_with_formula(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
            'formula': {
                'sort_order': 'less_is_better',
                'coeff_walk_pickup_time': 0,
                'coeff_walk_dropoff_time': 0,
                'coeff_shuttle_eta': 10,
                'coeff_user_wait_time': 0,
                'coeff_shuttle_ride_time': 0,
                'coeff_walk_ab_time': 10000,
                # из-за того что тут очень большой коэффициент
                # ожидается пустой список матчей
                'coeff_car_ab_time': 0,
                'min_score': 0,
                'max_score': 1,
            },
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    assert matched_shuttles == []

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []

    assert mock_router.times_called == 5
    assert mock_pedestrian_router.times_called == 5


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_routes.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_multiple_routes_with_formulas_array(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
            'formulas_array': [
                {
                    'name': 'filter_out_all_matches',
                    'formula': {
                        'sort_order': 'less_is_better',
                        'coeff_walk_pickup_time': 0,
                        'coeff_walk_dropoff_time': 0,
                        'coeff_shuttle_eta': 10,
                        'coeff_user_wait_time': 0,
                        'coeff_shuttle_ride_time': 0,
                        'coeff_walk_ab_time': 10000,
                        # из-за того что тут очень большой коэффициент
                        # ожидается пустой список матчей
                        'coeff_car_ab_time': 0,
                        'min_score': 0,
                        'max_score': 1,
                    },
                },
            ],
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.642947,
                        'lat': 55.734978,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.642947,
                    'lat': 55.734978,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    matched_shuttles = response.json()['matched_shuttles']
    assert matched_shuttles == []

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == []

    assert mock_router.times_called == 5
    assert mock_pedestrian_router.times_called == 5


@pytest.mark.pgsql('shuttle_control', files=['multiple_shuttles.sql'])
@pytest.mark.now('2020-07-23T10:42:00+0000')
@pytest.mark.parametrize('is_scheduled', [True, False])
@pytest.mark.parametrize('dropoff', ['stop__3', 'stop__4'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_multiple_shuttles(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load,
        load_binary,
        is_scheduled,
        dropoff,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        rlls = request.args['rll'].split('~')
        src = rlls[0]

        router_dist = ROUTER_TIMES.get(src, 50)
        return mockserver.make_response(
            response=_proto_driving_summary(router_dist, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary('route_resp_match.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1595500920,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.643150,
                        'lat': 55.734754,
                        'timestamp': 1595500920,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.643150,
                    'lat': 55.734754,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }
        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    if is_scheduled:
        pgsql['shuttle_control'].cursor().execute(
            load('multiple_shuttles_schedule.sql'),
        )

    endpoint = (
        [37.641380, 55.733464]
        if dropoff == 'stop__4'
        else [37.643077, 55.734100]
    )
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], endpoint],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200

    matched_shuttles = response.json()['matched_shuttles']
    matched_shuttles.sort(key=lambda item: item['shuttle']['id'])
    offer_id_2 = matched_shuttles[0]['offer_id']
    offer_id_1 = matched_shuttles[1]['offer_id']

    expected_time = {
        'eta': {
            'stop__3': {True: [60, 70], False: [60, 70]},
            'stop__4': {True: [60, 70], False: [60, 70]},
        },
        'route_time': {
            'stop__3': {True: [50, 50], False: [50, 50]},
            'stop__4': {True: [1686, 1676], False: [50, 50]},
        },
    }

    assert matched_shuttles == sorted(
        [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': dropoff,
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': expected_time['route_time'][dropoff][
                            is_scheduled
                        ][0],
                    },
                    'offer_id': offer_id_1,
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': dropoff,
                'shuttle': {
                    'id': 'gkZxnYQ73QGqrKyz',
                    'eta': expected_time['eta'][dropoff][is_scheduled][0],
                },
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 35, 'currency': 'RUB'},
                'offer_id': offer_id_1,
            },
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': dropoff,
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': expected_time['route_time'][dropoff][
                            is_scheduled
                        ][1],
                    },
                    'offer_id': offer_id_2,
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': dropoff,
                'shuttle': {
                    'id': 'Pmp80rQ23L4wZYxd',
                    'eta': expected_time['eta'][dropoff][is_scheduled][1],
                },
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'total': 35, 'currency': 'RUB'},
                'offer_id': offer_id_2,
            },
        ],
        key=lambda item: item['shuttle']['id'],
    )

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY shuttle_id DESC
        """,
        pgsql['shuttle_control'],
    )
    assert rows == [
        {'offer_id': offer_id_2, 'shuttle_id': 2},
        {'offer_id': offer_id_1, 'shuttle_id': 1},
    ]

    assert mock_router.times_called == (
        3 if is_scheduled and dropoff == 'stop__4' else 5
    )
    assert mock_pedestrian_router.times_called == 3


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_bad_dropoff(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 20,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200

    assert response.json() == {
        'match_error': 'no_point_b',
        'matched_shuttles': [],
    }
    assert mock_router.times_called == 3

    assert mock_pedestrian_router.times_called == 3


@pytest.mark.skip(reason='flapping test')
@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_stops_restrictions(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_control_stop_restrictions',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'route1': {
                'pickup_allowed_stops': [],
                'dropoff_allowed_stops': [],
            },
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid1_uuid1': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
            'dbid3_uuid3': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'match_error': 'no_available_shuttle',
        'matched_shuttles': [],
    }

    assert mock_router.times_called == 1

    assert mock_pedestrian_router.times_called == 1


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['multiple_bookings.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_match_previous_match(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/driver-trackstory/position')
    def _mock_trackstory(request):
        req = json.loads(request.get_data())
        driver_id = req['driver_id']

        result = {
            'dbid0_uuid0': {
                'position': {
                    'lon': 37.643024,
                    'lat': 55.734742,
                    'timestamp': 3,
                },
                'type': 'adjusted',
            },
        }

        return mockserver.make_response(
            json=result[f'{driver_id}'], status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        headers={'X-Yandex-UID': '0123456785'},
        json={
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
    )
    assert response.status_code == 200

    offer_id = response.json()['matched_shuttles'][0]['offer_id']
    assert response.json() == {
        'matched_shuttles': [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 50,
                    },
                    'offer_id': offer_id,
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 50},
                'price': {'currency': 'RUB', 'total': 35},
                'offer_id': offer_id,
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
            },
        ],
    }

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router_new(request):
        return mockserver.make_response(
            response=_proto_driving_summary(55, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        headers={'X-Yandex-UID': '0123456785'},
        json={
            'previous_match': {'offer_id': offer_id},
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'matched_shuttles': [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'stop__2',
                    'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 55,
                    },
                    'offer_id': offer_id,
                },
                'pickup_stop_id': 'stop__2',
                'dropoff_stop_id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 55},
                'price': {'currency': 'RUB', 'total': 35},
                'offer_id': offer_id,
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
            },
        ],
    }

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        headers={'X-Yandex-UID': '0123456785'},
        json={
            'previous_match': {
                # some random uuid
                'offer_id': 'e3adfa14-beb0-4928-a423-f155c37d0529',
            },
            'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()['matched_shuttles'][0]['offer_id'] != offer_id


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    'payment_type',
    [
        'cash',
        'card',
        'corp',
        'applepay',
        'googlepay',
        'coupon',
        'personal_wallet',
        'coop_account',
        'agent',
        'cargocorp',
        'yandex_card',
    ],
)
async def test_match_payment_type(
        taxi_shuttle_control,
        mockserver,
        experiments3,
        pgsql,
        load_json,
        payment_type,
        driver_trackstory_v2_shorttracks,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'max_matches_overall': 5,
            'max_matches_per_route': 5,
            'max_matches_per_shuttle': 5,
            'match_ttl': 60,
            'max_route_percent': 70,
        },
        clauses=[],
    )

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(50, 100),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(30, 10),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_trackstory_positions():
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.642329,
                        'lat': 55.733802,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1590668998,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(
        _mock_trackstory_positions(),
    )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        shuttle_category = load_json('v2_prepare_response.json')
        return mockserver.make_response(
            json={'categories': {'shuttle': shuttle_category}}, status=200,
        )

    @mockserver.json_handler('/pricing-data-preparer/v2/recalc')
    def _mock_v2_recalc(request):
        return mockserver.make_response(
            json={
                'price': {
                    'driver': {'total': 35, 'meta': {}},
                    'user': {'total': 35, 'meta': {}},
                },
            },
            status=200,
        )

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/match_shuttles',
        json={
            'route': [[37.641571, 55.737499], [37.642939, 55.734150]],
            'match_params': {
                'pickup_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'dropoff_limits': {
                    'max_walk_time': 40,
                    'max_walk_distance': 20,
                },
                'max_wait_time': 60,
            },
            'payment': {'type': payment_type, 'payment_method_id': None},
        },
        headers={'X-Yandex-UID': '0123456785'},
    )
    assert response.status_code == 200

    rows = select_named(
        """
        SELECT offer_id, shuttle_id
        FROM state.matching_offers
        ORDER BY offer_id
        """,
        pgsql['shuttle_control'],
    )

    resp = response.json()
    resp['matched_shuttles'].sort(key=lambda x: x['shuttle']['id'])

    offer_id_2 = resp['matched_shuttles'][0]['offer_id']
    offer_id_1 = resp['matched_shuttles'][1]['offer_id']

    assert rows == sorted(
        [
            {'offer_id': offer_id_2, 'shuttle_id': 2},
            {'offer_id': offer_id_1, 'shuttle_id': 1},
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda22ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda25ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda24ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda26ac',
                'shuttle_id': 1,
            },
            {
                'offer_id': 'acfff773-398f-4913-b9e9-03bf5eda23ac',
                'shuttle_id': 1,
            },
        ],
        key=lambda it: it['offer_id'],
    )

    assert resp == {
        'matched_shuttles': [
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'dropoff_stop_id': 'stop__2',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_2,
                },
                'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                'dropoff_stop_id': 'stop__2',
                'shuttle': {'id': 'Pmp80rQ23L4wZYxd', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'currency': 'RUB', 'total': 35},
                'offer_id': offer_id_2,
            },
            {
                'match_type': 'detailed',
                'base_match_info': {
                    'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                    'dropoff_stop_id': 'stop__2',
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'route_time': 50,
                    },
                    'offer_id': offer_id_1,
                },
                'pickup_stop_id': 'shuttle-stop-bjoAWlMYJRG14Nnm',
                'dropoff_stop_id': 'stop__2',
                'shuttle': {'id': 'gkZxnYQ73QGqrKyz', 'eta': 50},
                'walk_routes': {
                    'to_pickup_stop': {'time': 30, 'distance': 10},
                    'from_dropoff_stop': {'time': 30, 'distance': 10},
                },
                'price': {'currency': 'RUB', 'total': 35},
                'offer_id': offer_id_1,
            },
        ],
    }
