# pylint: disable=import-error, import-only-modules, too-many-lines
import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary


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


@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_stops_list(taxi_shuttle_control, mockserver, pgsql):
    def arrange_response(resp):
        resp = sorted(resp, key=lambda x: x['name_tanker_key'])
        for item in resp:
            item['routes'] = sorted(item['routes'], key=lambda x: x['name'])
        return resp

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/stops/list',
    )
    assert arrange_response(response.json()) == arrange_response(
        [
            {
                'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
                'position': [30.00, 60.00],
                'name_tanker_key': 'shuttle_control.stops.stop1',
                'routes': [
                    {'name': 'route2'},
                    {'name': 'route3'},
                    {'name': 'route1'},
                ],
            },
            {
                'id': 'stop__2',
                'position': [30.02, 60.02],
                'ya_transport_id': 'stop__2',
                'name_tanker_key': 'shuttle_control.stops.stop2',
                'routes': [
                    {'name': 'route2'},
                    {'name': 'route3'},
                    {'name': 'route1'},
                ],
            },
            {
                'id': 'stop__3',
                'position': [30.04, 60.04],
                'ya_transport_id': 'stop__3',
                'name_tanker_key': 'shuttle_control.stops.stop3',
                'routes': [{'name': 'route1'}, {'name': 'route2'}],
            },
            {
                'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'position': [30.05, 60.05],
                'name_tanker_key': 'shuttle_control.stops.stop4',
                'routes': [{'name': 'route1'}, {'name': 'route2'}],
            },
        ],
    )


@pytest.mark.now('2020-05-28T12:29:55+0000')
@pytest.mark.parametrize(
    'stop_id', ['shuttle-stop-Pmp80rQ23L4wZYxd', 'stop__2'],
)
@pytest.mark.parametrize('max_dist', [10600, 10400])
@pytest.mark.parametrize(
    'use_linear_fallback', [(False, False), (False, True), (True, False)],
)
async def test_stops_item(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        load,
        max_dist,
        stop_id,
        use_linear_fallback,
        driver_trackstory_v2_shorttracks,
):
    taxi_config.set_values(
        dict(
            SHUTTLE_CONTROL_STOP_SCHEDULE_THRESHOLDS={
                'min_distance_m': 30,
                'max_distance_m': max_dist,
            },
            SHUTTLE_CONTROL_FAKE_SCHEDULED_ARRIVAL_SETTINGS={
                'min_displayed_eta': 2,
                'max_eta_to_show': 120,
            },
            SHUTTLE_CONTROL_ENABLE_LINEAR_FALLBACK=use_linear_fallback,
            ROUTER_SELECT=[{'routers': ['yamaps']}],
            SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
                'route1': {
                    'driver': 'shuttle_control.routes.route1.name_for_driver',
                    'passenger': (
                        'shuttle_control.routes.route1.name_for_passenger'
                    ),
                },
                'route2': {
                    'driver': 'shuttle_control.routes.route2.name_for_driver',
                    'passenger': (
                        'shuttle_control.routes.route2.name_for_passenger'
                    ),
                },
            },
        ),
    )

    queries = [load('main.sql')]
    pgsql['shuttle_control'].apply_queries(queries)

    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        if use_linear_fallback:
            return mockserver.make_response(status=410)

        return mockserver.make_response(
            response=_proto_driving_summary(100, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_position():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.008,
                        'lat': 60.008,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 30.045,
                        'lat': 60.45,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_position())

    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/stops/item?stop_id=' + stop_id,
    )

    first_eta = 100 if not use_linear_fallback else 214
    shuttle2_schedule = {
        'shuttle_id': 'Pmp80rQ23L4wZYxd',
        'shuttle_state': 'enroute',
    }
    if max_dist > 10500 and not use_linear_fallback:
        shuttle2_schedule['eta'] = first_eta
    response = response.json()
    response['routes'] = sorted(
        response['routes'], key=lambda x: x['name_tanker_key'],
    )
    response['routes'][0]['schedule'].sort(key=lambda x: x['shuttle_id'])
    assert response == {
        'info': {
            'id': 'stop__2',
            'position': [30.02, 60.02],
            'ya_transport_id': 'stop__2',
            'name_tanker_key': 'shuttle_control.stops.stop2',
        },
        'routes': [
            {
                'id': 'gkZxnYQ73QGqrKyz',
                'schedule': [
                    {
                        'eta': first_eta,
                        'shuttle_id': 'gkZxnYQ73QGqrKyz',
                        'shuttle_state': 'enroute',
                    },
                ],
                'name': 'route1',
                'name_tanker_key': (
                    'shuttle_control.routes.route1.name_for_passenger'
                ),
            },
            {
                'id': 'Pmp80rQ23L4wZYxd',
                'schedule': [shuttle2_schedule],
                'name': 'route2',
                'name_tanker_key': (
                    'shuttle_control.routes.route2.name_for_passenger'
                ),
            },
        ],
    }

    assert mock_router.times_called == 2


@pytest.mark.now('2020-05-28T12:01:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_STOP_SCHEDULE_THRESHOLDS={
        'min_distance_m': 30,
        'max_distance_m': 10400,
    },
    SHUTTLE_CONTROL_FAKE_SCHEDULED_ARRIVAL_SETTINGS={
        'min_displayed_eta': 2,
        'max_eta_to_show': 120,
    },
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_first_stop_item(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
    @mockserver.handler('/maps-router/v2/summary')
    def mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_position():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.008,
                        'lat': 60.008,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 30.045,
                        'lat': 60.45,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_position())

    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/stops/item?stop_id='
        'shuttle-stop-gkZxnYQ73QGqrKyz',
    )
    response = response.json()
    response['routes'] = sorted(
        response['routes'], key=lambda x: x['name_tanker_key'],
    )
    assert response == {
        'info': {
            'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
            'position': [30.0, 60.0],
            'name_tanker_key': 'shuttle_control.stops.stop1',
        },
        'routes': [
            {
                'id': 'gkZxnYQ73QGqrKyz',
                'schedule': [],
                'name': 'route1',
                'name_tanker_key': (
                    'shuttle_control.routes.route1.name_for_passenger'
                ),
            },
            {
                'id': 'Pmp80rQ23L4wZYxd',
                'schedule': [
                    {
                        'shuttle_id': 'Pmp80rQ23L4wZYxd',
                        'shuttle_state': 'enroute',
                    },
                ],
                'name': 'route2',
                'name_tanker_key': (
                    'shuttle_control.routes.route2.name_for_passenger'
                ),
            },
        ],
    }
    assert mock_router.times_called == 1


@pytest.mark.now('2019-09-14T09:58:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_STOP_SCHEDULE_THRESHOLDS={
        'min_distance_m': 30,
        'max_distance_m': 10400,
    },
    SHUTTLE_CONTROL_FAKE_SCHEDULED_ARRIVAL_SETTINGS={
        'min_displayed_eta': 2,
        'max_eta_to_show': 120,
    },
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql', 'workshifts.sql'])
async def test_first_stop_item_out_of_workshift(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        experiments3,
        driver_trackstory_v2_shorttracks,
):
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
            response=_proto_driving_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_position():
        return {
            'results': [
                {
                    'position': {
                        'lon': 30.018,
                        'lat': 60.018,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 30.045,
                        'lat': 60.45,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 29.987,
                        'lat': 60.13,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_position())

    pgsql['shuttle_control'].cursor().execute(
        """
        UPDATE state.shuttle_trip_progress
        SET block_reason = 'out_of_workshift'
        where shuttle_id <> 2
        """,
    )

    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/stops/item?stop_id='
        'shuttle-stop-gkZxnYQ73QGqrKyz',
    )
    response = response.json()
    response['routes'] = sorted(
        response['routes'], key=lambda x: x['name_tanker_key'],
    )
    assert response == {
        'info': {
            'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
            'position': [30.0, 60.0],
            'name_tanker_key': 'shuttle_control.stops.stop1',
        },
        'routes': [
            {
                'id': 'gkZxnYQ73QGqrKyz',
                'schedule': [
                    {
                        'eta': 120,
                        'shuttle_id': '80vm7DQm7Ml24ZdO',
                        'shuttle_state': 'enroute',
                    },
                    {
                        'eta': 120,
                        'shuttle_id': 'gkZxnYQ73QGqrKyz',
                        'shuttle_state': 'enroute',
                    },
                ],
                'name': 'route1',
                'name_tanker_key': (
                    'shuttle_control.routes.route1.name_for_passenger'
                ),
            },
            {
                'id': 'Pmp80rQ23L4wZYxd',
                'schedule': [
                    {
                        'eta': 120 + 2500,
                        'shuttle_id': 'Pmp80rQ23L4wZYxd',
                        'shuttle_state': 'enroute',
                    },
                ],
                'name': 'route2',
                'name_tanker_key': (
                    'shuttle_control.routes.route2.name_for_passenger'
                ),
            },
        ],
    }
    assert mock_router.times_called == 1


ROUTE1_INFO = {
    'id': 'gkZxnYQ73QGqrKyz',
    'is_cyclic': False,
    'version': 1,
    'name': 'route1',
    'name_tanker_key': 'shuttle_control.routes.route1.name_for_passenger',
    'stops': [
        {
            'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
            'position': [30.0, 60.0],
            'name_tanker_key': 'shuttle_control.stops.stop1',
        },
        {
            'id': 'stop__2',
            'position': [30.02, 60.02],
            'ya_transport_id': 'stop__2',
            'name_tanker_key': 'shuttle_control.stops.stop2',
        },
        {
            'id': 'stop__3',
            'position': [30.04, 60.04],
            'ya_transport_id': 'stop__3',
            'name_tanker_key': 'shuttle_control.stops.stop3',
        },
        {
            'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
            'position': [30.05, 60.05],
            'name_tanker_key': 'shuttle_control.stops.stop4',
        },
    ],
    'polyline': [
        [30.0, 60.0],
        [30.01, 60.01],
        [30.02, 60.02],
        [30.03, 60.03],
        [30.04, 60.04],
        [30.05, 60.05],
    ],
}

ROUTE2_INFO = {
    'id': 'Pmp80rQ23L4wZYxd',
    'is_cyclic': False,
    'name': 'route2',
    'name_tanker_key': 'shuttle_control.routes.route2.name_for_passenger',
    'version': 1,
    'stops': [
        {
            'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
            'position': [30.05, 60.05],
            'name_tanker_key': 'shuttle_control.stops.stop4',
        },
        {
            'id': 'stop__3',
            'position': [30.04, 60.04],
            'ya_transport_id': 'stop__3',
            'name_tanker_key': 'shuttle_control.stops.stop3',
        },
        {
            'id': 'stop__2',
            'position': [30.02, 60.02],
            'ya_transport_id': 'stop__2',
            'name_tanker_key': 'shuttle_control.stops.stop2',
        },
        {
            'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
            'position': [30.0, 60.0],
            'name_tanker_key': 'shuttle_control.stops.stop1',
        },
    ],
    'polyline': [
        [30.05, 60.05],
        [30.04, 60.04],
        [30.03, 60.03],
        [30.02, 60.02],
        [30.01, 60.01],
        [30.0, 60.0],
    ],
}

ROUTE3_INFO = {
    'id': '80vm7DQm7Ml24ZdO',
    'is_cyclic': False,
    'polyline': [[30.0, 60.0], [30.01, 60.01], [30.02, 60.02]],
    'version': 1,
    'name': 'route3',
    'name_tanker_key': 'shuttle_control.routes.route3',
    'stops': [
        {
            'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
            'position': [30.0, 60.0],
            'name_tanker_key': 'shuttle_control.stops.stop1',
        },
        {
            'id': 'stop__2',
            'position': [30.02, 60.02],
            'ya_transport_id': 'stop__2',
            'name_tanker_key': 'shuttle_control.stops.stop2',
        },
    ],
}

ROUTE4_INFO = {
    'id': 'VlAK13MzaLx6Bmnd',
    'is_cyclic': False,
    'polyline': [[30.0, 60.0], [30.01, 60.01], [30.08, 60.08]],
    'version': 1,
    'name': 'route4',
    'name_tanker_key': 'shuttle_control.routes.route4',
    'stops': [
        {
            'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
            'position': [30.0, 60.0],
            'name_tanker_key': 'shuttle_control.stops.stop1',
        },
        {
            'id': 'stop__5',
            'position': [30.08, 60.08],
            'ya_transport_id': 'stop__5',
            'name_tanker_key': 'shuttle_control.stops.stop5',
        },
    ],
}


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'admin': 'shuttle_control.routes.route1.name_for_admin',
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'requested_ids, expected_response',
    [
        (None, [ROUTE1_INFO, ROUTE2_INFO, ROUTE3_INFO, ROUTE4_INFO]),
        (['Pmp80rQ23L4wZYxd'], [ROUTE2_INFO]),
        (['Pmp80rQ23L4wZYxd', 'SOMEINVALIDID'], [ROUTE2_INFO]),
        (['SOMEINVALIDID'], []),
    ],
)
async def test_routes_list(
        taxi_shuttle_control,
        requested_ids,
        expected_response,
        mockserver,
        pgsql,
):
    request_json = {}
    if requested_ids is not None:
        request_json['route_ids'] = requested_ids

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/routes/list', json=request_json,
    )
    response = response.json()
    response = sorted(response, key=lambda x: x['name_tanker_key'])
    assert response == expected_response


SHUTTLE1_INFO = {
    'id': 'gkZxnYQ73QGqrKyz',
    'position': [30.5, 60.5],
    'route': {
        'id': 'gkZxnYQ73QGqrKyz',
        'is_cyclic': False,
        'name_tanker_key': 'shuttle_control.routes.route1.name_for_passenger',
        'name': 'route1',
        'version': 1,
        'stops': [
            {
                'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
                'name_tanker_key': 'shuttle_control.stops.stop1',
                'position': [30.0, 60.0],
            },
            {
                'id': 'stop__2',
                'position': [30.02, 60.02],
                'ya_transport_id': 'stop__2',
                'name_tanker_key': 'shuttle_control.stops.stop2',
            },
            {
                'id': 'stop__3',
                'position': [30.04, 60.04],
                'ya_transport_id': 'stop__3',
                'name_tanker_key': 'shuttle_control.stops.stop3',
            },
            {
                'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'position': [30.05, 60.05],
                'name_tanker_key': 'shuttle_control.stops.stop4',
            },
        ],
        'polyline': [
            [30.0, 60.0],
            [30.01, 60.01],
            [30.02, 60.02],
            [30.03, 60.03],
            [30.04, 60.04],
            [30.05, 60.05],
        ],
    },
    'booked': False,
    'seats_available': 16,
    'state': 'enroute',
}

SHUTTLE2_INFO = {
    'id': 'Pmp80rQ23L4wZYxd',
    'position': [34.5, 64.5],
    'route': {
        'id': 'Pmp80rQ23L4wZYxd',
        'is_cyclic': False,
        'name_tanker_key': 'shuttle_control.routes.route2.name_for_passenger',
        'name': 'route2',
        'version': 1,
        'stops': [
            {
                'id': 'shuttle-stop-VlAK13MzaLx6Bmnd',
                'name_tanker_key': 'shuttle_control.stops.stop4',
                'position': [30.05, 60.05],
            },
            {
                'id': 'stop__3',
                'position': [30.04, 60.04],
                'ya_transport_id': 'stop__3',
                'name_tanker_key': 'shuttle_control.stops.stop3',
            },
            {
                'id': 'stop__2',
                'position': [30.02, 60.02],
                'ya_transport_id': 'stop__2',
                'name_tanker_key': 'shuttle_control.stops.stop2',
            },
            {
                'id': 'shuttle-stop-gkZxnYQ73QGqrKyz',
                'position': [30.0, 60.0],
                'name_tanker_key': 'shuttle_control.stops.stop1',
            },
        ],
        'polyline': [
            [30.05, 60.05],
            [30.04, 60.04],
            [30.03, 60.03],
            [30.02, 60.02],
            [30.01, 60.01],
            [30.0, 60.0],
        ],
    },
    'booked': False,
    'seats_available': 16,
    'state': 'enroute',
}


@pytest.mark.now('2020-05-28T11:54:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'requested_ids, expected_response',
    [
        (['Pmp80rQ23L4wZYxd'], [SHUTTLE2_INFO]),
        (['Pmp80rQ23L4wZYxd', 'INVALID_ID'], [SHUTTLE2_INFO]),
        ([''], []),
    ],
)
async def test_shuttles_list(
        taxi_shuttle_control,
        requested_ids,
        expected_response,
        mockserver,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
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
                        'lon': 34.5,
                        'lat': 64.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    request_json = {}
    request_json['shuttle_ids'] = requested_ids

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/shuttles/list', json=request_json,
    )
    assert sorted(response.json(), key=lambda x: x['id']) == sorted(
        expected_response, key=lambda x: x['id'],
    )


@pytest.mark.now('2020-05-28T11:54:00+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'requested_bbox, expected_response',
    [
        ([1, 1, 2, 2], []),
        ([30, 60, 40, 70], [SHUTTLE1_INFO, SHUTTLE2_INFO]),
        (None, [SHUTTLE1_INFO, SHUTTLE2_INFO]),
    ],
)
async def test_shuttles_list_with_bbox(
        taxi_shuttle_control,
        requested_bbox,
        expected_response,
        mockserver,
        pgsql,
        driver_trackstory_v2_shorttracks,
):
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
                        'lon': 34.5,
                        'lat': 64.5,
                        'timestamp': 1622202780,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock())

    # Dummy /v2/route mock
    @mockserver.handler('/maps-router/v2/route')
    def _mock_router_route(request):
        return mockserver.make_response(
            status=200, content_type='application/x-protobuf',
        )

    request_json = {}
    if requested_bbox is not None:
        request_json['bbox'] = requested_bbox

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/shuttles/list', json=request_json,
    )
    assert sorted(response.json(), key=lambda x: x['id']) == sorted(
        expected_response, key=lambda x: x['id'],
    )


@pytest.mark.now('2020-05-28T11:54:00+0000')
@pytest.mark.pgsql('shuttle_control', files=['scheduled.sql'])
@pytest.mark.parametrize(
    'stop_id', ['stop__1', 'stop__2', 'stop__3', 'stop__4'],
)
async def test_scheduled_stops_item(
        taxi_shuttle_control,
        mockserver,
        taxi_config,
        pgsql,
        load,
        load_binary,
        stop_id,
        driver_trackstory_v2_shorttracks,
):
    taxi_config.set_values(
        dict(
            SHUTTLE_CONTROL_STOP_SCHEDULE_THRESHOLDS={
                'min_distance_m': -1,
                'max_distance_m': 30600,
            },
            SHUTTLE_CONTROL_FAKE_SCHEDULED_ARRIVAL_SETTINGS={
                'min_displayed_eta': 2,
                'max_eta_to_show': 120,
            },
            SHUTTLE_CONTROL_ENABLE_DRW=False,
            SHUTTLE_CONTROL_ENABLE_LINEAR_FALLBACK=False,
            ROUTER_SELECT=[{'routers': ['yamaps']}],
            SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
                'route1': {
                    'admin': 'shuttle_control.routes.route1.name_for_admin',
                    'driver': 'shuttle_control.routes.route1.name_for_driver',
                    'passenger': (
                        'shuttle_control.routes.route1.name_for_passenger'
                    ),
                },
                'route2': {
                    'driver': 'shuttle_control.routes.route2.name_for_driver',
                    'passenger': (
                        'shuttle_control.routes.route2.name_for_passenger'
                    ),
                },
            },
        ),
    )

    @mockserver.handler('/maps-router/v2/route')
    def mock_router(request):
        return mockserver.make_response(
            response=load_binary(f'route_resp_{stop_id}.pb'),
            status=200,
            content_type='application/x-protobuf',
        )

    def _mock_position():
        return {
            'results': [
                {
                    'position': {
                        'lon': 29.99,
                        'lat': 59.99,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid0_uuid0',
                },
                {
                    'position': {
                        'lon': 30.025,
                        'lat': 60.025,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid1_uuid1',
                },
                {
                    'position': {
                        'lon': 30.021,
                        'lat': 60.021,
                        'timestamp': 1590668995,
                    },
                    'type': 'adjusted',
                    'driver_id': 'dbid2_uuid2',
                },
            ],
        }

    driver_trackstory_v2_shorttracks.set_data_from_positions(_mock_position())

    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/stops/item?stop_id=' + stop_id,
    )

    stop_info = {
        'stop__1': {
            'expected_eta_1': 360,
            'expected_eta_2': 2160,
            'expected_eta_3': 3900,
            'position': [30.00, 60.00],
            'router_times_called': 1,
            'fake_ts': '2020-05-28T12:30:00+0000',
        },
        'stop__2': {
            'expected_eta_1': 1260,
            'expected_eta_2': 3060,
            'expected_eta_3': 420,
            'position': [30.02, 60.02],
            'router_times_called': 1,
            'fake_ts': '2020-05-28T12:45:00+0000',
        },
        'stop__3': {
            'expected_eta_1': 3360,
            'expected_eta_2': 240,
            'expected_eta_3': 1560,
            'position': [30.04, 60.04],
            'router_times_called': 1,
            'fake_ts': '2020-05-28T12:55:00+0000',
        },
        'stop__4': {
            'expected_eta_1': 4065,
            'expected_eta_2': 540,
            'expected_eta_3': 1860,
            'position': [30.05, 60.05],
            'router_times_called': 1,
            'fake_ts': '2020-05-28T13:00:00+0000',
        },
    }

    response = response.json()
    response['routes'][0]['schedule'] = sorted(
        response['routes'][0]['schedule'], key=lambda x: x['shuttle_id'],
    )

    assert response == {
        'info': {
            'id': stop_id,
            'position': stop_info[stop_id]['position'],
            'ya_transport_id': stop_id,
            'name_tanker_key': 'shuttle_control.stops.stop' + stop_id[-1],
        },
        'routes': [
            {
                'id': 'gkZxnYQ73QGqrKyz',
                'schedule': [
                    {
                        'eta': stop_info[stop_id]['expected_eta_1'],
                        'shuttle_id': 'gkZxnYQ73QGqrKyz',
                        'shuttle_state': 'enroute',
                    },
                ],
                'name': 'route1',
                'name_tanker_key': (
                    'shuttle_control.routes.route1.name_for_passenger'
                ),
            },
        ],
    }

    assert (
        mock_router.times_called == stop_info[stop_id]['router_times_called']
    )
