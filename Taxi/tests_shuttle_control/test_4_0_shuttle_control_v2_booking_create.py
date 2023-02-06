# pylint: disable=import-only-modules, import-error, redefined-outer-name
# pylint: disable=too-many-lines
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


def check_stq(stq, code, booking_id):
    times_called = stq.routehistory_shuttle_order_add.times_called
    if code == 200:
        assert times_called == 1
        call_json = stq.routehistory_shuttle_order_add.next_call()
        call_json.pop('eta')
        call_json['kwargs'].pop('log_extra')
        assert call_json == {
            'id': 'routehistory_' + booking_id,
            'queue': 'routehistory_shuttle_order_add',
            'args': [],
            'kwargs': {
                'order': {
                    'created': '2020-01-17T18:17:38+0000',
                    'order_id': booking_id,
                    'yandex_uid': '0123456789',
                    'source': {
                        'position': [30.0, 60.0],
                        'text': 'full_text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
                        ),
                    },
                    'destination': {
                        'position': [31.0, 61.0],
                        'text': 'full_text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
                        ),
                    },
                },
            },
        }
    else:
        assert not times_called


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
    'offer_id,route,payment_type,code,body_code,passengers_count',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            200,
            None,
            None,
        ),
        (
            None,
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            400,
            'INVALID_INPUT',
            None,
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            [[30.0, 60.0], [32.0, 62.0]],
            'cash',
            400,
            'OFFER_EXPIRED',
            None,
        ),  # wrong route
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            [[30.0, 60.0], [32.0, 62.0]],
            'cash',
            400,
            'OFFER_EXPIRED',
            None,
        ),  # expired offer
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            400,
            'INVALID_INPUT',
            None,
        ),  # offer not found
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d22',
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            200,
            None,
            3,
        ),  # booked multiple seats
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d22',
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            400,
            'OFFER_EXPIRED',
            5,
        ),  # offer and booking passengers_count don't match
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d23',
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            400,
            'NO_SEATS_AVAILABLE',
            16,
        ),
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d24',
            [[30.0, 60.0], [31.0, 61.0]],
            'cash',
            400,
            'INVALID_INPUT',
            None,
        ),
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.parametrize(
    'full_address',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=True),
            id='full_address_info_enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=False),
            id='full_address_info_disabled',
        ),
    ],
)
async def test_main(
        taxi_shuttle_control,
        external_mocks,
        pgsql,
        offer_id,
        route,
        payment_type,
        code,
        body_code,
        passengers_count,
        load_json,
        full_address,
):
    req = {
        'route': [
            {
                'position': route[0],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
            },
            {
                'position': route[1],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
            },
        ],
        'payment': {'type': payment_type},
    }

    if offer_id == '5c76c35b-98df-481c-ac21-0555c5e51d23':
        commited_booking = req
        commited_booking['offer_id'] = '2fef68c9-25d0-4174-9dd0-bdd1b3730779'
        await taxi_shuttle_control.post(
            '/4.0/shuttle-control/v2/booking/create',
            headers={'X-Yandex-UID': 'legacy_client'},
            json=commited_booking,
        )

    if offer_id:
        req['offer_id'] = offer_id
    if passengers_count:
        req['passengers_count'] = passengers_count

    # Loop validates idempotency
    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/4.0/shuttle-control/v2/booking/create',
            headers={'X-Yandex-UID': '0123456789'},
            json=req,
        )

        assert response.status_code == code

        if response.status_code == 200:
            booking_id = response.json()['booking_id']

            cur_price = 10 * (
                passengers_count if passengers_count is not None else 1
            )
            generated_codes = response.json()['ticket']['code']

            expected_response = load_json(
                'v2_booking_create_test_main_expected_response.json',
            )

            expected_response['booking_id'] = booking_id
            expected_response['cost'] = {
                'total': f'{cur_price} $SIGN$$CURRENCY$',
            }
            expected_response['ticket'] = {'code': generated_codes}
            expected_response['ui']['main_panel']['footer'][
                'text'
            ] = f'Билет {generated_codes}'
            expected_response['ui']['card_details'][
                'text'
            ] = f'Стоимость {cur_price} $SIGN$$CURRENCY$'
            expected_response['ui']['card_details'][
                'title'
            ] = f'Билет {generated_codes}'

            if offer_id:
                if full_address:
                    expected_response['source_point'] = {
                        'position': [30, 60],
                        'short_text': 'text',
                        'full_text': 'full_text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
                        ),
                    }
                    expected_response['destination_point'] = {
                        'position': [31, 61],
                        'short_text': 'text',
                        'full_text': 'full_text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
                        ),
                    }
                else:
                    expected_response['source_point'] = {
                        'position': [30, 60],
                        'short_text': '',
                        'full_text': '',
                    }
                    expected_response['destination_point'] = {
                        'position': [31, 61],
                        'short_text': '',
                        'full_text': '',
                    }

            assert response.json() == expected_response
            if full_address:
                rows = select_named(
                    f"""
                    SELECT booking_id, point_type, full_text,
                    short_text, uri
                    FROM state.order_point_text_info
                    WHERE booking_id = '{booking_id}'
                    AND point_type = 'order_point_a'
                    """,
                    pgsql['shuttle_control'],
                )
                assert rows == [
                    {
                        'booking_id': booking_id,
                        'point_type': 'order_point_a',
                        'full_text': 'full_text',
                        'short_text': 'text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
                        ),
                    },
                ]

                rows = select_named(
                    f"""
                    SELECT booking_id, point_type, full_text,
                    short_text, uri
                    FROM state.order_point_text_info
                    WHERE booking_id = '{booking_id}'
                    AND point_type = 'order_point_b'
                    """,
                    pgsql['shuttle_control'],
                )
                assert rows == [
                    {
                        'booking_id': booking_id,
                        'point_type': 'order_point_b',
                        'full_text': 'full_text',
                        'short_text': 'text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
                        ),
                    },
                ]

            rows = select_named(
                'SELECT booking_id, yandex_uid, shuttle_id, stop_id, '
                'dropoff_stop_id, shuttle_lap, offer_id '
                'FROM state.passengers '
                'ORDER BY yandex_uid, shuttle_id, stop_id',
                pgsql['shuttle_control'],
            )
            assert rows == [
                {
                    'booking_id': booking_id,
                    'yandex_uid': '0123456789',
                    'shuttle_id': 1,
                    'stop_id': 1,
                    'dropoff_stop_id': 5,
                    'shuttle_lap': 1,
                    'offer_id': offer_id,
                },
            ]

            expected_booking_tickets = []
            for gen_code in generated_codes.split():
                expected_booking_tickets.append(
                    {
                        'booking_id': booking_id,
                        'code': gen_code,
                        'status': 'issued',
                    },
                )

            rows = select_named(
                f"""
                SELECT booking_id, code, status
                FROM state.booking_tickets
                WHERE booking_id = '{booking_id}'
                ORDER BY code
                """,
                pgsql['shuttle_control'],
            )
            assert rows == expected_booking_tickets
        else:
            assert response.json()['code'] == body_code


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.parametrize(
    'offer_id,shuttle_id,response_code,response_body_code,position',
    [
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'gkZxnYQ73QGqrKyz',
            200,
            None,
            [37.642329, 55.733802],
        ),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'Pmp80rQ23L4wZYxd',
            200,
            None,
            [37.640681, 55.736028],
        ),
        (
            '5c76c35b-98df-481c-ac21-0555c5e51d21',
            '80vm7DQm7Ml24ZdO',
            400,
            'OFFER_EXPIRED',
            None,
        ),  # offer is ahead of end stop
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3738888',
            'VlAK13MzaLx6Bmnd',
            400,
            'NO_SEATS_AVAILABLE',
            None,
        ),  # no seats available in shuttle
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730779',
            'gkZxnYQ73QGqrKyz',
            400,
            'OFFER_EXPIRED',
            None,
        ),  # offer is behind shuttle
    ],
)
@pytest.mark.parametrize(
    'full_address',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=True),
            id='full_address_info_enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=False),
            id='full_address_info_disabled',
        ),
    ],
)
@pytest.mark.pgsql('shuttle_control', files=['main_cyclic.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.experiments3(filename='exp3_shuttle_save_routehistory.json')
async def test_main_cyclic(
        taxi_shuttle_control,
        stq,
        external_mocks,
        pgsql,
        experiments3,
        offer_id,
        shuttle_id,
        response_code,
        response_body_code,
        load_json,
        position,
        full_address,
):
    req = {
        'offer_id': offer_id,
        'route': [
            {
                'position': [30.0, 60.0],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
            },
            {
                'position': [31.0, 61.0],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
            },
        ],
        'payment': {'type': 'cash'},
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

    booking_id = ''
    # Loop validates idempotency
    for _ in range(2):
        response = await taxi_shuttle_control.post(
            '/4.0/shuttle-control/v2/booking/create',
            headers={'X-Yandex-UID': '0123456789'},
            json=req,
        )

        assert response.status_code == response_code

        if response_code == 200:
            booking_id = response.json()['booking_id']

            generated_codes = response.json()['ticket']['code']

            expected_response = load_json(
                'v2_booking_create_test_main_cyclic_expected_response.json',
            )

            expected_response['booking_id'] = booking_id
            expected_response['ticket'] = {'code': generated_codes}
            expected_response['shuttle']['id'] = shuttle_id
            expected_response['shuttle']['position'] = position
            expected_response['ui']['main_panel']['footer'][
                'text'
            ] = f'Билет {generated_codes}'
            expected_response['ui']['card_details'][
                'title'
            ] = f'Билет {generated_codes}'

            if offer_id:
                if full_address:
                    expected_response['source_point'] = {
                        'position': [30, 60],
                        'short_text': 'text',
                        'full_text': 'full_text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
                        ),
                    }
                    expected_response['destination_point'] = {
                        'position': [31, 61],
                        'short_text': 'text',
                        'full_text': 'full_text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
                        ),
                    }
                else:
                    expected_response['source_point'] = {
                        'position': [30, 60],
                        'short_text': '',
                        'full_text': '',
                    }
                    expected_response['destination_point'] = {
                        'position': [31, 61],
                        'short_text': '',
                        'full_text': '',
                    }

            assert response.json() == expected_response

            if full_address:
                rows = select_named(
                    f"""
                    SELECT booking_id, point_type, full_text,
                    short_text, uri
                    FROM state.order_point_text_info
                    WHERE booking_id = '{booking_id}'
                    AND point_type = 'order_point_a'
                    """,
                    pgsql['shuttle_control'],
                )
                assert rows == [
                    {
                        'booking_id': booking_id,
                        'point_type': 'order_point_a',
                        'full_text': 'full_text',
                        'short_text': 'text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1'
                        ),
                    },
                ]

                rows = select_named(
                    f"""
                    SELECT booking_id, point_type, full_text,
                    short_text, uri
                    FROM state.order_point_text_info
                    WHERE booking_id = '{booking_id}'
                    AND point_type = 'order_point_b'
                    """,
                    pgsql['shuttle_control'],
                )
                assert rows == [
                    {
                        'booking_id': booking_id,
                        'point_type': 'order_point_b',
                        'full_text': 'full_text',
                        'short_text': 'text',
                        'uri': (
                            'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2'
                        ),
                    },
                ]

            rows = select_named(
                'SELECT booking_id, yandex_uid, shuttle_id, stop_id, '
                'dropoff_stop_id,shuttle_lap, offer_id, processing_type '
                'FROM state.passengers '
                'WHERE yandex_uid = \'0123456789\' '
                'ORDER BY yandex_uid, shuttle_id, stop_id',
                pgsql['shuttle_control'],
            )
            assert rows == [
                {
                    'booking_id': booking_id,
                    'yandex_uid': '0123456789',
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

            rows = select_named(
                f"""
                SELECT booking_id, code, status
                FROM state.booking_tickets
                WHERE booking_id = '{booking_id}'
                ORDER BY code
                """,
                pgsql['shuttle_control'],
            )
            assert rows == [
                {
                    'booking_id': booking_id,
                    'code': generated_codes,
                    'status': 'issued',
                },
            ]
        else:
            assert response.json()['code'] == response_body_code
    check_stq(stq, response_code, booking_id)


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
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
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

    req = {
        'offer_id': offer_id,
        'route': [
            {
                'position': [37.643148, 55.734349],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
            },
            {
                'position': [37.641866, 55.737599],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
            },
        ],
        'payment': {'type': 'cash'},
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
            '/4.0/shuttle-control/v2/booking/create',
            headers={'X-Yandex-UID': '0123456789'},
            json=req,
        )

        assert response.status_code == response_code

        booking_id = response.json()['booking_id']
        generated_codes = response.json()['ticket']['code']

        expected_response = load_json(
            'v2_booking_create_test_main_dynamic_expected_response.json',
        )

        expected_response['booking_id'] = booking_id
        expected_response['ticket'] = {'code': generated_codes}
        expected_response['ui']['main_panel']['footer'][
            'text'
        ] = f'Билет {generated_codes}'
        expected_response['ui']['card_details'][
            'title'
        ] = f'Билет {generated_codes}'

        expected_eta = (route_time * (1 if upd_trip_state else 2)) // 60 * 60
        expected_eta_min = expected_eta // 60
        expected_response['ui']['estimated_waiting'][
            'message'
        ] = f'{expected_eta_min} мин'
        expected_response['ui']['estimated_waiting']['seconds'] = expected_eta
        expected_response['ui']['main_panel'][
            'title'
        ] = f'{expected_eta_min} мин и приедет'

        if offer_id:
            expected_response['source_point'] = {
                'position': [37.643148, 55.734349],
                'short_text': '',
                'full_text': '',
            }
            expected_response['destination_point'] = {
                'position': [37.641866, 55.737599],
                'short_text': '',
                'full_text': '',
            }

        assert response.json() == expected_response

        rows = select_named(
            'SELECT booking_id, yandex_uid, shuttle_id, stop_id, '
            'dropoff_stop_id,shuttle_lap, offer_id, processing_type, '
            'dropoff_lap '
            'FROM state.passengers '
            'WHERE yandex_uid = \'0123456789\' '
            'ORDER BY yandex_uid, shuttle_id, stop_id',
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'yandex_uid': '0123456789',
                'shuttle_id': 1,
                'stop_id': 2,
                'dropoff_stop_id': 6,
                'shuttle_lap': 1,
                'offer_id': offer_id,
                'processing_type': 'in_parallel',
                'dropoff_lap': 1,
            },
        ]

        rows = select_named(
            f"""
            SELECT booking_id, code, status
            FROM state.booking_tickets
            WHERE booking_id = '{booking_id}'
            ORDER BY code
            """,
            pgsql['shuttle_control'],
        )
        assert rows == [
            {
                'booking_id': booking_id,
                'code': generated_codes,
                'status': 'issued',
            },
        ]

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


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_multiple_booking_different_offers(
        taxi_shuttle_control, external_mocks,
):
    req = {
        'route': [
            {
                'position': [30.0, 60.0],
                'short_text': 'text',
                'full_text': 'full_text',
            },
            {
                'position': [31.0, 61.0],
                'short_text': 'text',
                'full_text': 'full_text',
            },
        ],
        'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        'payment': {'type': 'cash'},
    }

    response_first = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v2/booking/create',
        headers={'X-Yandex-UID': '0123456789'},
        json=req,
    )
    assert response_first.status_code == 200

    req['offer_id'] = '5c76c35b-98df-481c-ac21-0555c5e51d21'
    response_second = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v2/booking/create',
        headers={'X-Yandex-UID': '0123456789'},
        json=req,
    )

    assert response_second.status_code == 400
    assert (
        response_second.json()['message']
        == 'Cancel the previous booking before committing a new one'
    )


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'upd_booking.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_different_booking_same_offer(
        taxi_shuttle_control, external_mocks,
):
    req = {
        'route': [
            {
                'position': [30.0, 60.0],
                'short_text': 'text',
                'full_text': 'full_text',
            },
            {
                'position': [31.0, 61.0],
                'short_text': 'text',
                'full_text': 'full_text',
            },
        ],
        'offer_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        'payment': {'type': 'cash'},
    }

    response = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v2/booking/create',
        headers={'X-Yandex-UID': '0123456789'},
        json=req,
    )

    assert response.status_code == 400
    assert response.json()['message'] == 'Queried shuttle was not found'
    assert response.json()['code'] == 'OFFER_ALREADY_USED'


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'payment_type,is_allowed',
    [
        ('card', True),
        ('corp', False),
        ('applepay', True),
        ('googlepay', True),
        ('coupon', False),
        ('personal_wallet', False),
        ('coop_account', False),
        ('agent', False),
        ('cargocorp', False),
        ('yandex_card', False),
    ],
)
@pytest.mark.parametrize(
    'offer_id,is_free',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', False),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730666', True),
    ],
)
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
async def test_zero_payment_types(
        taxi_shuttle_control,
        external_mocks,
        experiments3,
        payment_type,
        is_allowed,
        offer_id,
        is_free,
):
    experiments3.add_config(
        name='shuttle_payment_settings',
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
                'value': {
                    'zero_payment_types': ['card', 'applepay', 'googlepay'],
                },
            },
        ],
    )

    route = [[30.0, 60.0], [31.0, 61.0]]
    req = {
        'route': [
            {
                'position': route[0],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
            },
            {
                'position': route[1],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
            },
        ],
        'offer_id': offer_id,
        'payment': {'type': payment_type},
    }

    response = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v2/booking/create',
        headers={'X-Yandex-UID': '0123456789'},
        json=req,
    )

    expected_satus_code = 200 if is_allowed and is_free else 400
    response_body_code = (
        None if is_allowed and is_free else 'INVALID_PAYMENT_TYPE'
    )

    assert response.status_code == expected_satus_code
    if response_body_code is not None:
        assert response.json()['code'] == response_body_code


@pytest.mark.now('2019-09-14T09:55:00+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.parametrize(
    'offer_id',
    [
        '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
        '2fef68c9-25d0-4174-9dd0-bdd1b3730778',
    ],
)
async def test_out_of_workshift(
        taxi_shuttle_control, external_mocks, experiments3, pgsql, offer_id,
):
    experiments3.add_config(
        name='shuttle_payment_settings',
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
                'value': {
                    'zero_payment_types': ['card', 'applepay', 'googlepay'],
                },
            },
        ],
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='shuttle_match_in_workshift',
        consumers=['shuttle-control/match_in_workshift'],
        default_value={'enabled': True},
        clauses=[],
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

    route = [[30.0, 60.0], [31.0, 61.0]]
    req = {
        'route': [
            {
                'position': route[0],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
            },
            {
                'position': route[1],
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
            },
        ],
        'offer_id': offer_id,
        'payment': {'type': 'cash'},
    }

    response = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v2/booking/create',
        headers={'X-Yandex-UID': '0123456789'},
        json=req,
    )

    assert response.status_code == 200
    assert response.json()['ui']['estimated_waiting'] == {
        'message': '5 мин',
        'seconds': 300,
    }


class DriverInfo(object):
    def __init__(self, driver_id, position):
        self.driver_id = driver_id
        self.position = position


class ReqInfo(object):
    def __init__(self, offer_id, yandex_uid, point_pickup, point_dropoff):
        self.offer_id = offer_id
        self.yandex_uid = yandex_uid
        self.point_pickup = point_pickup
        self.point_dropoff = point_dropoff


@pytest.mark.now('2019-09-14T09:55:00+0000')
@pytest.mark.experiments3(filename='shuttle_booking_information_settings.json')
@pytest.mark.parametrize(
    'queries,driver_info,req_info,http_code',
    [
        (
            [
                'test_specific/config_dynamic_route.sql',
                'test_specific/state_with_booking_before_confirm_departure.sql',
            ],
            DriverInfo(
                driver_id='dbid0_uuid0', position=[37.642874, 55.734083],
            ),
            ReqInfo(
                offer_id='acfff773-398f-4913-b9e9-03bf5eda22ad',
                yandex_uid='0002',
                point_pickup=[37.642874, 55.734083],
                point_dropoff=[37.642234, 55.733778],
            ),
            200,
        ),
        (
            [
                'test_specific/config_dynamic_route.sql',
                'test_specific/state_with_booking_after_confirm_departure.sql',
            ],
            DriverInfo(
                driver_id='dbid0_uuid0', position=[37.642874, 55.734083],
            ),
            ReqInfo(
                offer_id='acfff773-398f-4913-b9e9-03bf5eda22ad',
                yandex_uid='0002',
                point_pickup=[37.642874, 55.734083],
                point_dropoff=[37.642234, 55.733778],
            ),
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
        mockserver,
        taxi_shuttle_control,
        experiments3,
        pgsql,
        load,
        queries,
        driver_info,
        req_info,
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

    experiments3.add_config(
        name='shuttle_payment_settings',
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
                'value': {
                    'zero_payment_types': ['card', 'applepay', 'googlepay'],
                },
            },
        ],
    )

    req = {
        'route': [
            {
                'position': req_info.point_pickup,
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C1',
            },
            {
                'position': req_info.point_dropoff,
                'short_text': 'text',
                'full_text': 'full_text',
                'uri': 'ymapsbm1: //geo?ll=-0.069%2C51.516&spn=0.001%2C2',
            },
        ],
        'offer_id': req_info.offer_id,
        'payment': {'type': 'cash'},
    }

    response = await taxi_shuttle_control.post(
        '/4.0/shuttle-control/v2/booking/create',
        headers={'X-Yandex-UID': req_info.yandex_uid},
        json=req,
    )

    assert response.status_code == http_code
