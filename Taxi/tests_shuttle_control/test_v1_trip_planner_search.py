# pylint: disable=import-error,too-many-lines,import-only-modules
import copy
import datetime

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary

from tests_shuttle_control.utils import select_named
from tests_shuttle_control.utils import stringify_detailed_view


YANDEX_UID = '0123456785'


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


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


class AnyString:
    def __eq__(self, other):
        return isinstance(other, str)


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize(
    'router_time,pedestrian_time,pedestrian_distance'
    ',is_ok,sort_order,passengers_count,payment',
    [
        (91, 30, 10, False, 'less_is_better', 1, None),
        (60, 50, 10, False, 'less_is_better', 1, None),
        (26, 30, 10, False, 'less_is_better', 1, None),
        (50, 30, 21, False, 'less_is_better', 1, None),
        (
            50,
            30,
            10,
            True,
            'less_is_better',
            1,
            {'type': 'cash', 'payment_method_id': None},
        ),
        (
            50,
            30,
            10,
            True,
            'less_is_better',
            1,
            {'type': 'card', 'payment_method_id': '987654321'},
        ),
        (50, 30, 10, True, 'greater_is_better', 2, None),
        (50, 30, 10, True, 'less_is_better', 1, None),
    ],
)
@pytest.mark.parametrize(
    'external_passenger_id', [None, 'external_passenger_id'],
)
async def test_basic_flow(
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
        external_passenger_id,
        driver_trackstory_v2_shorttracks,
):
    max_walk_time = 40
    max_walk_distance = 20
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_v1_trip_planner_search_settings',
        consumers=['shuttle-control/trip-planner/search'],
        default_value={
            'enabled': True,
            'operation_flow_config': [
                {
                    'code': 'unknown_operation',
                    'params': {'param1': 1, 'param2': '2'},
                },
                {
                    'code': 'search_routes_linear',
                    'params': {'routes_permitted': ['route1']},
                },
                {'code': 'calc_car_ab_info'},
                {'code': 'calc_walk_ab_info'},
                {
                    'code': 'pricing_request_prepare',
                    'params': {
                        'command_control': {'timeout': 300, 'retry_cnt': 3},
                    },
                },
                {
                    'code': 'search_stops_linear',
                    'params': {
                        'max_line_dist_to_pickup': (
                            max_walk_distance + 10
                        ),  # it does include linear surplus from v1 matching,,
                        'max_line_dist_from_dropoff': max_walk_distance + 10,
                    },
                },
                {
                    'code': 'route_passenger',
                    'params': {'max_bulk_size': 1, 'max_parallel_requests': 1},
                },
                {'code': 'search_shuttles'},
                {'code': 'generate_trips'},
                {
                    'code': 'calc_pickup_eta',
                    'params': {'max_bulk_size': 1, 'max_parallel_requests': 1},
                },
                {
                    'code': 'calc_route_info',
                    'params': {'max_bulk_size': 1, 'max_parallel_requests': 1},
                },
                {
                    'code': 'calc_price',
                    'params': {
                        'max_bulk_size': 1,
                        'max_parallel_requests': 1,
                        'command_control': {'timeout': 300, 'retry_cnt': 3},
                    },
                },
                {
                    'code': 'calc_trip_score',
                    'params': {
                        'formula': {
                            'coeff_walk_pickup_time': 0,
                            'coeff_walk_dropoff_time': 0,
                            'coeff_shuttle_eta': 10,
                            'coeff_user_wait_time': 0,
                            'coeff_shuttle_ride_time': 0,
                            'coeff_walk_ab_time': 0,
                            'coeff_car_ab_time': 0,
                        },
                    },
                },
                {
                    'code': 'filter_by_pickup_eta',
                    'params': {'min_seconds': 0, 'max_seconds': 3000},
                },
                {'code': 'filter_by_passengers_sla'},
                {
                    'code': 'filter_by_passenger_routes',
                    'params': {
                        'to_pickup': {
                            'max_seconds': max_walk_time,
                            'max_meters': max_walk_distance,
                        },
                        'from_dropoff': {
                            'max_seconds': max_walk_time,
                            'max_meters': max_walk_distance,
                        },
                        'max_wait_seconds': 60,
                    },
                },
                {'code': 'filter_by_shuttle_load'},
                {'code': 'filter_by_workshift'},
                {
                    'code': 'filter_by_direction_on_cyclic',
                    'params': {'max_route_percent': 100},
                },
                {'code': 'filter_by_block_reason'},
                {'code': 'filter_by_pause_state'},
                {'code': 'filter_by_stop_restrictions'},
                {
                    'code': 'filter_by_trip_score',
                    'params': {
                        'max_overall': 5,
                        'max_per_route': 5,
                        'max_per_shuttle': 5,
                        'sort_order': sort_order,
                    },
                },
                {
                    'code': 'filter_by_trip_feasibility',
                    'params': {'min_eta_to_next_shuttle_stop_s': 10000},
                },
                {
                    'code': 'store_trips_in_pg',
                    'params': {'trip_ttl_seconds': 180},
                },
            ],
        },
        clauses=[],
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_sla_params',
        consumers=['shuttle-control/sla_params'],
        default_value={
            'add_expected_sla_deviation_to_dropoff_time': True,
            'dropoff_deviation': {'max_acceptable_deviation_s': 100},
        },
        clauses=[],
    )

    # Dummy /v2/route mock
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(router_time, 200),
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
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.643024,
                        'lat': 55.734742,
                        'timestamp': 1622202780,
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

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(
                pedestrian_time, pedestrian_distance,
            ),
            status=200,
            content_type='application/x-protobuf',
        )

    request_json = {
        'route': [[37.643068, 55.734641], [37.641380, 55.733464]],
        'payment': payment,
        'passengers_count': passengers_count,
        'external_passenger_id': external_passenger_id,
    }

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/trip-planner/search',
        json=request_json,
        headers={'X-Yandex-UID': YANDEX_UID},
    )
    assert response.status_code == 200

    rows = select_named(
        f"""
        SELECT * FROM state.matching_offers
        WHERE yandex_uid = '{YANDEX_UID}'
        ORDER BY offer_id
        """,
        pgsql['shuttle_control'],
    )

    if is_ok:
        trip_id = response.json()['trips'][0]['id']

        assert response.json() == {
            'service_available': True,
            'trips': [
                {
                    'id': trip_id,
                    'price': {
                        'per_seat': {'amount': 35.0, 'currency': 'RUB'},
                        'total': {
                            'amount': 35.0 * passengers_count,
                            'currency': 'RUB',
                        },
                    },
                    'shuttle': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'pickup_eta': {
                            'distance_meters': 200,
                            'time_seconds': 50,
                        },
                    },
                    'route': {
                        'id': 'gkZxnYQ73QGqrKyz',
                        'name': 'route1',
                        'segment': {
                            'pickup': {
                                'id': 'stop__2',
                                'position': [37.643129, 55.734452],
                            },
                            'dropoff': {
                                'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                                'position': [37.641628, 55.733419],
                            },
                            'route_info': {
                                'distance_meters': 200,
                                'time_seconds': 100,
                            },
                        },
                    },
                    'walk_to_pickup': {
                        'distance_meters': 10,
                        'time_seconds': 30,
                    },
                    'walk_from_dropoff': {
                        'distance_meters': 10,
                        'time_seconds': 30,
                    },
                },
            ],
        }

        assert rows == [
            {
                'shuttle_id': 1,
                'offer_id': trip_id,
                'route_id': 1,
                'yandex_uid': YANDEX_UID,
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
                'expires_at': datetime.datetime(2020, 5, 28, 12, 32, 58),
                'external_confirmation_code': None,
                'payment_type': (None if payment is None else payment['type']),
                'payment_method_id': (
                    None if payment is None else payment['payment_method_id']
                ),
                'dropoff_timestamp': datetime.datetime(
                    2020, 5, 28, 12, 31, 38,
                ),
                'pickup_timestamp': datetime.datetime(2020, 5, 28, 12, 30, 48),
                'suggested_route_view': None,
                'suggested_traversal_plan': None,
                'external_passenger_id': external_passenger_id,
            },
        ]
    else:
        assert response.json() == {
            'service_available': False,
            'trips': [],
            'unavailability_reason': 'no_shuttle_available',
        }
        assert rows == []


@pytest.mark.now('2020-05-28T12:29:58+0000')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
@pytest.mark.parametrize('is_flex_route', [True, False])
@pytest.mark.parametrize(
    'bookings, exp_view, exp_view_flex, exp_detailed_view, '
    'exp_detailed_view_flex',
    [
        (
            [],
            [[2, 6, 8]],
            [[2, 6, 3]],
            [[(2, None, None), (6, None, None), (8, None, None)]],
            [[(2, None, None), (6, None, None), (3, None, None)]],
        ),
        (
            [1],
            [[1, 2, 6, 8]],
            [[1, 2, 6, 3]],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (6, None, None),
                    (8, None, None),
                ],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (6, None, None),
                    (3, None, None),
                ],
            ],
        ),
        (
            [1, 2],
            [[1, 2, 4, 6, 8], [1, 2, 6, 4, 8]],
            [[1, 2, 4, 6, 3], [1, 2, 6, 4, 3]],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, None, None),
                    (8, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (6, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (8, None, None),
                ],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, None, None),
                    (3, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (6, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (3, None, None),
                ],
            ],
        ),
        (
            [1, 3],
            [[1, 2, 6, 8]],
            [[1, 2, 6, 8, 3]],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                ],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                    (3, None, None),
                ],
            ],
        ),
        (
            [1, 2, 3],
            [[1, 2, 4, 6, 8]],
            [[1, 2, 4, 6, 8, 3]],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                ],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', True),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', False),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                    (3, None, None),
                ],
            ],
        ),
        (
            [2],
            [
                [1, 2, 4, 6, 8],
                [1, 2, 6, 4, 8],
                [1, 4, 2, 6, 8],
                [2, 1, 4, 6, 8],
                [2, 1, 6, 4, 8],
                [2, 6, 1, 4, 8],
            ],
            [
                [1, 2, 4, 6, 3],
                [1, 2, 6, 4, 3],
                [1, 4, 2, 6, 3],
                [2, 1, 4, 6, 3],
                [2, 1, 6, 4, 3],
                [2, 6, 1, 4, 3],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, None, None),
                    (8, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, None, None),
                    (6, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (8, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (2, None, None),
                    (6, None, None),
                    (8, None, None),
                ],
                [
                    (2, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, None, None),
                    (8, None, None),
                ],
                [
                    (2, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (6, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (8, None, None),
                ],
                [
                    (2, None, None),
                    (6, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (8, None, None),
                ],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, None, None),
                    (3, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, None, None),
                    (6, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (3, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (2, None, None),
                    (6, None, None),
                    (3, None, None),
                ],
                [
                    (2, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, None, None),
                    (3, None, None),
                ],
                [
                    (2, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (6, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (3, None, None),
                ],
                [
                    (2, None, None),
                    (6, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (3, None, None),
                ],
            ],
        ),
        (
            [2, 3],
            [[1, 2, 4, 6, 8], [1, 4, 2, 6, 8], [2, 1, 4, 6, 8]],
            [[1, 2, 4, 6, 8, 3], [1, 4, 2, 6, 8, 3], [2, 1, 4, 6, 8, 3]],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (2, None, None),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                ],
                [
                    (2, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                ],
            ],
            [
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (2, None, None),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                    (3, None, None),
                ],
                [
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (2, None, None),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                    (3, None, None),
                ],
                [
                    (2, None, None),
                    (1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', True),
                    (4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', False),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                    (3, None, None),
                ],
            ],
        ),
        (
            [3],
            [[2, 6, 8]],
            [[2, 6, 8, 3]],
            [
                [
                    (2, None, None),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                ],
            ],
            [
                [
                    (2, None, None),
                    (6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', True),
                    (8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', False),
                    (3, None, None),
                ],
            ],
        ),
    ],
)
async def test_generate_trips(
        taxi_shuttle_control,
        mockserver,
        pgsql,
        load,
        load_json,
        taxi_config,
        experiments3,
        is_flex_route,
        bookings,
        exp_view,
        exp_view_flex,
        exp_detailed_view,
        exp_detailed_view_flex,
        driver_trackstory_v2_shorttracks,
):
    max_walk_distance = 20

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_v1_trip_planner_search_settings',
        consumers=['shuttle-control/trip-planner/search'],
        default_value={
            'enabled': True,
            'operation_flow_config': [
                {
                    'code': 'search_routes_linear',
                    'params': {'routes_permitted': ['route1']},
                },
                {'code': 'calc_car_ab_info'},
                {'code': 'calc_walk_ab_info'},
                {
                    'code': 'pricing_request_prepare',
                    'params': {
                        'command_control': {'timeout': 300, 'retry_cnt': 3},
                    },
                },
                {
                    'code': 'search_stops_linear',
                    'params': {
                        'max_line_dist_to_pickup': (
                            max_walk_distance + 10
                        ),  # it does include linear surplus from v1 matching,,
                        'max_line_dist_from_dropoff': max_walk_distance + 10,
                    },
                },
                {
                    'code': 'route_passenger',
                    'params': {'max_bulk_size': 1, 'max_parallel_requests': 1},
                },
                {'code': 'search_shuttles'},
                {'code': 'generate_trips'},
                {
                    'code': 'calc_pickup_eta',
                    'params': {'max_bulk_size': 1, 'max_parallel_requests': 1},
                },
                {
                    'code': 'calc_route_info',
                    'params': {'max_bulk_size': 1, 'max_parallel_requests': 1},
                },
                {
                    'code': 'calc_price',
                    'params': {
                        'max_bulk_size': 1,
                        'max_parallel_requests': 1,
                        'command_control': {'timeout': 300, 'retry_cnt': 3},
                    },
                },
                {
                    'code': 'calc_trip_score',
                    'params': {
                        'formula': {
                            'coeff_walk_pickup_time': 0,
                            'coeff_walk_dropoff_time': 0,
                            'coeff_shuttle_eta': 10,
                            'coeff_user_wait_time': 0,
                            'coeff_shuttle_ride_time': 0,
                            'coeff_walk_ab_time': 0,
                            'coeff_car_ab_time': 0,
                        },
                    },
                },
                {
                    'code': 'store_trips_in_pg',
                    'params': {'trip_ttl_seconds': 180},
                },
            ],
        },
        clauses=[],
    )

    queries = [
        load('main_generate_trips_flex.sql')
        if is_flex_route
        else load('main_generate_trips.sql'),
    ]
    if bookings:
        for idx in bookings:
            queries.append(load(f'add_booking_{idx}.sql'))
        queries.append(
            load('upd_traversal_plans_flex.sql')
            if is_flex_route
            else load('upd_traversal_plans.sql'),
        )
    pgsql['shuttle_control'].apply_queries(queries)

    # Dummy /v2/route mock
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(100, 200),
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
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
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

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(0, 0),
            status=200,
            content_type='application/x-protobuf',
        )

    request_json = {
        'route': [[37.651075, 55.743728], [37.641201, 55.751559]],
        'payment': {'type': 'cash', 'payment_method_id': None},
        'passengers_count': 1,
    }

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/trip-planner/search',
        json=request_json,
        headers={'X-Yandex-UID': YANDEX_UID},
    )
    assert response.status_code == 200

    expected_response = load_json('exp_response_generate_trips.json')
    resp = response.json()
    for trip in resp['trips']:
        rows = select_named(
            f"""
            SELECT * FROM state.matching_offers
            WHERE offer_id = '{trip['id']}'
            """,
            pgsql['shuttle_control'],
        )

        del trip['id']
        del trip['shuttle']
        del trip['price']
        del trip['route']['segment']['route_info']
        del trip['walk_to_pickup']
        del trip['walk_from_dropoff']
        trip['route_view'] = rows[0]['suggested_route_view']
        trip['traversal_plan'] = rows[0]['suggested_traversal_plan']

    resp['trips'].sort(key=lambda t: t['route_view'])
    new_trips = len(exp_view_flex if is_flex_route else exp_view) - 1
    for _ in range(new_trips):
        expected_response['trips'].append(
            copy.deepcopy(expected_response['trips'][0]),
        )

    for idx, view in enumerate(exp_view_flex if is_flex_route else exp_view):
        expected_response['trips'][idx]['route_view'] = view
    for idx, view in enumerate(
            exp_detailed_view_flex if is_flex_route else exp_detailed_view,
    ):
        expected_response['trips'][idx][
            'traversal_plan'
        ] = stringify_detailed_view(view)

    assert resp == expected_response
