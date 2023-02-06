# pylint: disable=import-only-modules, import-error, redefined-outer-name
import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary

from tests_shuttle_control.utils import select_named


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


@pytest.fixture
def external_mocks(mockserver, driver_trackstory_v2_shorttracks):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_0_uuid_0',
                    'data': {'car_id': 'shuttle_car_id'},
                },
            ],
        }

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'dbid_0_shuttle_car_id',
                    'data': {
                        'number': 'A666MP77',
                        'park_id': 'park_id',
                        'car_id': 'car_id',
                    },
                },
            ],
        }

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(100, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    # Dummy /v2/route mock
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    def _mock():
        return {
            'results': [
                {
                    'position': {
                        'lat': 59.995,
                        'lon': 29.995,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_0_uuid_0',
                },
                {
                    'position': {
                        'lat': 59.995,
                        'lon': 29.995,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_2_uuid_2',
                },
                {
                    'position': {
                        'lat': 59.995,
                        'lon': 29.995,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid_3_uuid_3',
                },
                {
                    'position': {
                        'lon': 37.642329,
                        'lat': 55.733802,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
                {
                    'position': {
                        'lon': 37.640681,
                        'lat': 55.736028,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid3_uuid3',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    @mockserver.json_handler('driver-trackstory/shorttrack')
    def _mock_shorttrack(request):
        args = json.loads(request.get_data())

        if args['driver_id'] in ['dbid_4_uuid_4', 'dbid4_uuid4']:
            return {}

        response_by_driver = {
            'dbid_0_uuid_0': {
                'lat': 59.995,
                'lon': 29.995,
                'timestamp': 1579285059,
            },
            'dbid_2_uuid_2': {
                'lat': 59.995,
                'lon': 29.995,
                'timestamp': 1579285059,
            },
            'dbid_3_uuid_3': {
                'lat': 59.995,
                'lon': 29.995,
                'timestamp': 1579285059,
            },
            'dbid0_uuid0': {
                'lon': 37.642329,
                'lat': 55.733802,
                'timestamp': 1579285059,
            },
            'dbid1_uuid1': {
                'lon': 37.640681,
                'lat': 55.736028,
                'timestamp': 1579285059,
            },
            'dbid2_uuid2': {
                'lon': 37.640681,
                'lat': 55.736028,
                'timestamp': 1579285059,
            },
            'dbid3_uuid3': {
                'lon': 37.640681,
                'lat': 55.736028,
                'timestamp': 1579285059,
            },
        }

        return {'adjusted': [response_by_driver[args['driver_id']]]}

    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_park(request):
        return {
            'id': '',
            'login': '',
            'name': '',
            'is_active': True,
            'city_id': '',
            'locale': '',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'country_id': 'russian_id',
            'demo_mode': True,
            'geodata': {'lat': 0, 'lon': 1, 'zoom': 2},
        }


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.parametrize(
    'offer_id,code,body_code',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 200, None),
        (None, 400, 'INVALID_INPUT_MOSCOW_BUS'),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            400,
            'OFFER_EXPIRED_MOSCOW_BUS',
        ),  # expired offer
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            400,
            'INVALID_INPUT_MOSCOW_BUS',
        ),  # offer not found
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d23',
            400,
            'NO_SEATS_AVAILABLE_MOSCOW_BUS',
        ),
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_main(
        taxi_shuttle_control, external_mocks, pgsql, offer_id, code, body_code,
):
    if offer_id == '5c76c35b-98df-481c-ac21-0555c5e51d23':
        commited_booking = {'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730779'}
        await taxi_shuttle_control.post(
            '/internal/shuttle-control/v1/service/booking/create',
            headers={'Accept-Language': 'ru'},
            params={'service_id': 'moscow_bus'},
            json=commited_booking,
        )

    req = {'offer_id': offer_id}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/service/booking/create',
        headers={'Accept-Language': 'ru'},
        params={'service_id': 'moscow_bus'},
        json=req,
    )

    assert response.status_code == code

    if response.status_code == 200:
        booking_id = offer_id
        expected_response = {
            'booking_id': booking_id,
            'status': {'status': 'driving'},
        }

        assert response.json() == expected_response

        rows = select_named(
            f"""
            SELECT booking_id, yandex_uid, shuttle_id, stop_id,
            dropoff_stop_id, shuttle_lap, offer_id, origin, service_origin_id
            FROM state.passengers
            WHERE offer_id = '{offer_id}'
            ORDER BY yandex_uid, shuttle_id, stop_id
            """,
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'yandex_uid': None,
                'shuttle_id': 1,
                'stop_id': 1,
                'dropoff_stop_id': 5,
                'shuttle_lap': 1,
                'offer_id': offer_id,
                'origin': 'service',
                'service_origin_id': 'moscow_bus',
            },
        ]
    elif offer_id:
        assert response.json()['code'] == body_code


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.parametrize(
    'offer_id,shuttle_id,response_code,response_body_code',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'gkZxnYQ73QGqrKyz',
            200,
            None,
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'Pmp80rQ23L4wZYxd',
            200,
            None,
        ),
        # (
        #     '5c76c35b-98df-481c-ac21-0555c5e51d21',
        #     '80vm7DQm7Ml24ZdO',
        #     400,
        #     'OFFER_EXPIRED_MOSCOW_BUS',
        # ),  # offer is ahead of end stop
        # @dvinokurov: deprecated functionality
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
            'VlAK13MzaLx6Bmnd',
            400,
            'NO_SEATS_AVAILABLE_MOSCOW_BUS',
        ),  # no seats available in shuttle
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            'gkZxnYQ73QGqrKyz',
            400,
            'OFFER_EXPIRED_MOSCOW_BUS',
        ),  # offer is behind shuttle
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_main_cyclic(
        taxi_shuttle_control,
        external_mocks,
        pgsql,
        experiments3,
        offer_id,
        shuttle_id,
        response_code,
        response_body_code,
        load_json,
):
    req = {'offer_id': offer_id}

    experiments3.add_experiment(
        name='shuttle_procaas_settings',
        consumers=['shuttle-control/create_booking'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/create_booking'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'processing_type': 'in_parallel'},
            },
        ],
    )

    # Loop validates idempotency
    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/internal/shuttle-control/v1/service/booking/create',
            headers={'Accept-Language': 'ru'},
            params={'service_id': 'moscow_bus'},
            json=req,
        )

        assert response.status_code == response_code

        if response_code == 200:
            booking_id = offer_id

            expected_response = {
                'booking_id': booking_id,
                'status': {'status': 'driving'},
            }

            assert response.json() == expected_response

            rows = select_named(
                f"""
                SELECT booking_id, yandex_uid, shuttle_id, stop_id,
                dropoff_stop_id,shuttle_lap, offer_id, processing_type
                FROM state.passengers
                WHERE offer_id = '{offer_id}'
                ORDER BY shuttle_id, stop_id
                """,
                pgsql['shuttle_control'],
            )
            assert rows == [
                {
                    'booking_id': booking_id,
                    'yandex_uid': None,
                    'shuttle_id': 1 if shuttle_id == 'gkZxnYQ73QGqrKyz' else 2,
                    'stop_id': 5,
                    'dropoff_stop_id': 2,
                    'shuttle_lap': (
                        4 if shuttle_id == 'gkZxnYQ73QGqrKyz' else 2
                    ),
                    'offer_id': offer_id,
                    'processing_type': 'in_parallel',
                },
            ]

        elif offer_id:
            assert response.json()['code'] == response_body_code


@pytest.mark.now('2020-01-17T18:00:00+0000')
@pytest.mark.parametrize(
    'offer_id,shuttle_id,response_code,response_body_code,position',
    [
        (
            'acfff773-398f-4913-b9e9-03bf5eda22ad',
            'gkZxnYQ73QGqrKyz',
            200,
            None,
            [37.642329, 55.733802],
        ),
    ],
)
@pytest.mark.parametrize('upd_trip_state', [False, True])
@pytest.mark.pgsql('shuttle_control', files=['main_dynamic.sql'])
async def test_main_dynamic(
        taxi_shuttle_control,
        external_mocks,
        mockserver,
        cached_stops_route_info,
        pgsql,
        load,
        experiments3,
        offer_id,
        shuttle_id,
        response_code,
        response_body_code,
        load_json,
        position,
        upd_trip_state,
):
    @mockserver.json_handler('/driver-trackstory/positions')
    def _mock(request):
        return {
            'results': [
                {
                    'position': {
                        'lon': 37.642329,
                        'lat': 55.733802,
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
            ],
        }

    req = {'offer_id': offer_id}

    experiments3.add_experiment(
        name='shuttle_procaas_settings',
        consumers=['shuttle-control/create_booking'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/create_booking'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'processing_type': 'in_parallel'},
            },
        ],
    )

    route_time = 500 if upd_trip_state else 69
    cached_stops_route_info.set_time(route_time)

    # short version of config
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_v1_trip_planner_search_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'enabled': True,
            'operation_flow_config': [
                {
                    'code': 'filter_by_passengers_sla',
                    'params': {
                        'max_pickup_delay_s': route_time * 3,
                        'max_dropoff_delay_s': route_time * 6,
                    },
                },
            ],
        },
        clauses=[],
    )

    await taxi_shuttle_control.invalidate_caches(
        cache_names=[
            'shuttle-positions-cache',
            'shuttle-eta-to-stops-cache',
            'stops-mutual-eta-cache',
        ],
    )

    if upd_trip_state:
        pgsql['shuttle_control'].cursor().execute(
            load('upd_trip_state_dynamic.sql'),
        )

    # Loop validates idempotency
    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/internal/shuttle-control/v1/service/booking/create',
            headers={'Accept-Language': 'ru'},
            params={'service_id': 'moscow_bus'},
            json=req,
        )

        assert response.status_code == response_code

        expected_response = {
            'booking_id': offer_id,
            'status': {'status': 'driving'},
        }
        assert response.json() == expected_response

        rows = select_named(
            'SELECT booking_id, yandex_uid, shuttle_id, stop_id, '
            'dropoff_stop_id,shuttle_lap, offer_id, processing_type, '
            'dropoff_lap, origin, service_origin_id '
            'FROM state.passengers '
            'WHERE yandex_uid IS NULL '
            'ORDER BY yandex_uid, shuttle_id, stop_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': offer_id,
                'yandex_uid': None,
                'shuttle_id': 1,
                'stop_id': 2,
                'dropoff_stop_id': 6,
                'shuttle_lap': 1,
                'offer_id': offer_id,
                'processing_type': 'in_parallel',
                'dropoff_lap': 1,
                'origin': 'service',
                'service_origin_id': 'moscow_bus',
            },
        ]

        rows = select_named(
            f"""
            SELECT booking_id, status
            FROM state.booking_tickets
            WHERE booking_id = '{offer_id}'
            ORDER BY code
            """,
            pgsql['shuttle_control'],
        )
        assert rows == [{'booking_id': offer_id, 'status': 'issued'}]

        rows = select_named(
            f"""
            SELECT current_view
            FROM state.route_views
            WHERE view_id = 1
            """,
            pgsql['shuttle_control'],
        )
        assert rows[0]['current_view'] == [1, 2, 3, 6, 5, 7]

        rows = select_named(
            f"""
            SELECT next_stop_id, lap
            FROM state.shuttle_trip_progress
            WHERE shuttle_id = 1
            """,
            pgsql['shuttle_control'],
        )

        if upd_trip_state:
            assert rows[0] == {'next_stop_id': 2, 'lap': 1}
        else:
            assert rows[0] == {'next_stop_id': 1, 'lap': 0}


class DriverInfo(object):
    def __init__(self, driver_id, position):
        self.driver_id = driver_id
        self.position = position


@pytest.mark.now('2019-09-14T09:55:00+0000')
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.parametrize(
    'queries,driver_info,offer_id,http_code',
    [
        (
            [
                'test_specific/config_dynamic_route.sql',
                'test_specific/state_with_booking_before_confirm_departure.sql',
            ],
            DriverInfo('dbid0_uuid0', [37.642874, 55.734083]),
            'acfff773-398f-4913-b9e9-03bf5eda22ad',
            200,
        ),
        (
            [
                'test_specific/config_dynamic_route.sql',
                'test_specific/state_with_booking_after_confirm_departure.sql',
            ],
            DriverInfo('dbid0_uuid0', [37.642874, 55.734083]),
            'acfff773-398f-4913-b9e9-03bf5eda22ad',
            400,
        ),
    ],
    ids=(
        'shuttle with booking before confirm departure',
        'shuttle with booking after confirm departure',
    ),
)
async def test_specific(
        external_mocks,
        taxi_shuttle_control,
        mockserver,
        cached_stops_route_info,
        experiments3,
        pgsql,
        load,
        queries,
        driver_info,
        offer_id,
        http_code,
):
    pgsql['shuttle_control'].apply_queries([load(q) for q in queries])

    @mockserver.json_handler('/driver-trackstory/positions')
    def _mock(request):
        return {
            'results': [
                {
                    'position': {
                        'lon': driver_info.position[0],
                        'lat': driver_info.position[1],
                        'timestamp': 1579285059,
                    },
                    'type': 'adjusted',
                    'driver_id': driver_info.driver_id,
                },
            ],
        }

    experiments3.add_experiment(
        name='shuttle_procaas_settings',
        consumers=['shuttle-control/create_booking'],
        match={
            'enabled': True,
            'consumers': [{'name': 'shuttle-control/create_booking'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'main',
                'predicate': {'type': 'true', 'init': {}},
                'value': {'processing_type': 'in_parallel'},
            },
        ],
    )

    route_time = 69
    cached_stops_route_info.set_time(route_time)

    # short version of config
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_v1_trip_planner_search_settings',
        consumers=['shuttle-control/match_shuttles'],
        default_value={
            'enabled': True,
            'operation_flow_config': [
                {
                    'code': 'filter_by_passengers_sla',
                    'params': {
                        'max_pickup_delay_s': route_time * 3,
                        'max_dropoff_delay_s': route_time * 6,
                    },
                },
            ],
        },
        clauses=[],
    )

    await taxi_shuttle_control.invalidate_caches(
        cache_names=[
            'shuttle-positions-cache',
            'shuttle-eta-to-stops-cache',
            'stops-mutual-eta-cache',
        ],
    )

    # Loop validates idempotency
    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/internal/shuttle-control/v1/service/booking/create',
            headers={'Accept-Language': 'ru'},
            params={'service_id': 'moscow_bus'},
            json={'offer_id': offer_id},
        )

        assert response.status_code == http_code
