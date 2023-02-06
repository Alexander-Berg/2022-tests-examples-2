# pylint: disable=import-error
import pytest
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


import tests_candidates.helpers


_DEFAULT_ROUTER_SELECT = [{'routers': ['linear-fallback']}]

_ANSWER_BOTH = 'pedestrian_search_answer.json'
_ANSWER_WITHOUT_CAR = 'pedestrian_search_without_car_answer.json'
_ANSWER_WITHOUT_PEDESTRIAN = 'pedestrian_search_without_pedestrian_answer.json'
_ANSWER_WITHOUT_ECONOM = 'pedestrian_search_without_econom_answer.json'


async def _initialize_positions(driver_positions, chain_busy_drivers):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.625344, 55.755430]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.625639, 55.754844]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.625618, 55.752399]},
        ],
    )

    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 0,
                'left_distance': 0,
                'destination': [37.625296, 55.759285],
                'order_id': 'order_id1',
                'approximate': False,
            },
        ],
    )


@pytest.mark.config(
    EXTRA_EXAMS_BY_ZONE={},
    ROUTER_SELECT=[
        {'routers': ['linear-fallback']},
        {'type': 'pedestrian', 'routers': ['yamaps']},
    ],
)
async def test_pedestrian_search(
        taxi_candidates,
        driver_positions,
        dispatch_settings,
        chain_busy_drivers,
        load_json,
        mockserver,
        taxi_config,
):
    def _proto_masstransit_summary(time, distance):
        response = ProtoMasstransitSummary.Summaries()
        item = response.summaries.add()
        item.weight.time.value = time
        item.weight.time.text = ''
        item.weight.walking_distance.value = distance
        item.weight.walking_distance.text = ''
        item.weight.transfers_count = 1
        return response.SerializeToString()

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_router(request):
        assert (
            request.query['rll']
            == '37.625618,55.752399~37.625615,55.752399~37.625620,'
            '55.752399~37.625621,55.752399~37.625620,55.752399'
            or request.query['rll']
            == '37.625618,55.752399~37.625296,55.759285~37.625129,55.757644'
        )

        return mockserver.make_response(
            response=_proto_masstransit_summary(time=683, distance=948),
            status=200,
            content_type='application/x-protobuf',
        )

    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [
                    {
                        'type': 'common_dispatch',
                        'priority': 0,
                        'values': {'PEDESTRIAN_DISABLED': True},
                    },
                ],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [
                    {
                        'type': 'common_dispatch',
                        'priority': 0,
                        'values': {
                            'PEDESTRIAN_ONLY': False,
                            'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                            'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                            'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                            'PEDESTRIAN_SETTINGS': {
                                '__default__': {
                                    'MAX_SEARCH_RADIUS': 5000,
                                    'MAX_ORDER_ROUTE_DISTANCE': 5000,
                                    'MAX_ORDER_ROUTE_TIME': 3600,
                                },
                            },
                        },
                    },
                ],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'order': {
            'request': {
                'source': {'geopoint': [37.625618, 55.752399]},
                'destinations': [
                    {'geopoint': [37.625615, 55.752399]},
                    {'geopoint': [37.625620, 55.752399]},
                    {'geopoint': [37.625621, 55.752399]},
                    {'geopoint': [37.625621, 55.752399]},
                    {'geopoint': [37.625621, 55.752399]},
                    {'geopoint': [37.625621, 55.752399]},
                    {'geopoint': [37.625621, 55.752399]},
                    {'geopoint': [37.625621, 55.752399]},
                    {'geopoint': [37.625620, 55.752399]},
                ],
            },
        },
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'courier'],
        'limit': 5,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(_ANSWER_BOTH),
    )
    assert actual == expected
    assert _mock_router.times_called == 2


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_pedestrian_multisearch(
        taxi_candidates, driver_positions, chain_busy_drivers, load_json,
):

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'courier'],
        'class_limits': {'econom': 5, 'courier': 5},
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(_ANSWER_BOTH),
    )
    assert actual == expected


@pytest.mark.parametrize(
    'courier_limits,answer_type',
    [
        (
            {
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_BOTH,
        ),
        (
            {
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 600,
                    },
                },
            },
            _ANSWER_WITHOUT_PEDESTRIAN,
        ),
        (
            {
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 1000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 1000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_PEDESTRIAN,
        ),
        (
            {
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_SEARCH_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_SEARCH_ROUTE_TIME': 3600,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_SEARCH_ROUTE_DISTANCE': 5000,
                        'MAX_SEARCH_ROUTE_TIME': 3600,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_BOTH,
        ),
        (
            {
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_SEARCH_ROUTE_DISTANCE': 10,
                'PEDESTRIAN_MAX_SEARCH_ROUTE_TIME': 3600,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_SEARCH_ROUTE_DISTANCE': 10,
                        'MAX_SEARCH_ROUTE_TIME': 3600,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_PEDESTRIAN,
        ),
        (
            {
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_SEARCH_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_SEARCH_ROUTE_TIME': 10,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_SEARCH_ROUTE_DISTANCE': 5000,
                        'MAX_SEARCH_ROUTE_TIME': 10,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_PEDESTRIAN,
        ),
        (
            {
                'PEDESTRIAN_ONLY': True,
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_CAR,
        ),
        (
            {
                'PEDESTRIAN_ONLY': False,
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_BOTH,
        ),
    ],
)
@pytest.mark.parametrize('by_transport', [True, False])
@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_pedestrian_search_limits(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings,
        load_json,
        courier_limits,
        answer_type,
        by_transport,
        taxi_config,
):
    taxi_config.set_values(
        dict(
            CANDIDATES_FEATURE_SWITCHES={
                'use_pedestrian_settings_by_transport': by_transport,
            },
        ),
    )
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [{'values': {'PEDESTRIAN_DISABLED': True}}],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [{'values': courier_limits}],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'destination': [37.642579, 55.734997],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'courier'],
        'limit': 5,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(answer_type),
    )
    assert actual == expected


@pytest.mark.parametrize(
    'courier_limits,answer_type',
    [
        (
            {
                'PEDESTRIAN_ONLY': True,
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_CAR,
        ),
        (
            {
                'PEDESTRIAN_ONLY': False,
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_ECONOM,
        ),
    ],
)
@pytest.mark.parametrize('by_transport', [True, False])
@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_pedestrian_search_pedestrian_only(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings,
        load_json,
        courier_limits,
        answer_type,
        by_transport,
        taxi_config,
):
    taxi_config.set_values(
        dict(
            CANDIDATES_FEATURE_SWITCHES={
                'use_pedestrian_settings_by_transport': by_transport,
            },
        ),
    )
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [{'values': {'PEDESTRIAN_DISABLED': True}}],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [{'values': courier_limits}],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'destination': [37.642579, 55.734997],
        'max_distance': 10000,
        'allowed_classes': ['courier'],
        'limit': 5,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(answer_type),
    )
    assert actual == expected


@pytest.mark.parametrize(
    'courier_limits,answer_type',
    [
        (
            {
                'PEDESTRIAN_ONLY': True,
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_CAR,
        ),
        (
            {
                'PEDESTRIAN_ONLY': False,
                'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                'PEDESTRIAN_SETTINGS': {
                    '__default__': {
                        'MAX_SEARCH_RADIUS': 5000,
                        'MAX_ORDER_ROUTE_DISTANCE': 5000,
                        'MAX_ORDER_ROUTE_TIME': 3600,
                    },
                },
            },
            _ANSWER_WITHOUT_ECONOM,
        ),
    ],
)
@pytest.mark.parametrize('by_transport', [True, False])
@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_pedestrian_multisearch_pedestrian_only(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings,
        load_json,
        courier_limits,
        answer_type,
        by_transport,
        taxi_config,
):
    taxi_config.set_values(
        dict(
            CANDIDATES_FEATURE_SWITCHES={
                'use_pedestrian_settings_by_transport': by_transport,
            },
        ),
    )
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [{'values': {'PEDESTRIAN_DISABLED': True}}],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [{'values': courier_limits}],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'destination': [37.642579, 55.734997],
        'max_distance': 10000,
        'allowed_classes': ['courier'],
        'class_limits': {'courier': 5},
    }
    response = await taxi_candidates.post('order-multisearch', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(answer_type),
    )
    assert actual == expected


@pytest.mark.parametrize('by_transport', [True, False])
@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT, EXTRA_EXAMS_BY_ZONE={},
)
async def test_pedestrian_path(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings,
        load_json,
        by_transport,
        taxi_config,
):
    taxi_config.set_values(
        dict(
            CANDIDATES_FEATURE_SWITCHES={
                'use_pedestrian_settings_by_transport': by_transport,
            },
        ),
    )
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [{'values': {'PEDESTRIAN_DISABLED': True}}],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [
                    {
                        'values': {
                            'PEDESTRIAN_ONLY': False,
                            'PEDESTRIAN_MAX_SEARCH_RADIUS': 5000,
                            'PEDESTRIAN_MAX_ORDER_ROUTE_DISTANCE': 5000,
                            'PEDESTRIAN_MAX_ORDER_ROUTE_TIME': 3600,
                            'PEDESTRIAN_SETTINGS': {
                                '__default__': {
                                    'MAX_SEARCH_RADIUS': 5000,
                                    'MAX_ORDER_ROUTE_DISTANCE': 5000,
                                    'MAX_ORDER_ROUTE_TIME': 3600,
                                },
                            },
                        },
                    },
                ],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'courier'],
        'limit': 5,
        'order': {
            'request': {
                'source': {'geopoint': [37.625129, 55.757644]},
                'destinations': [{'geopoint': [37.7, 55.8]}],
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(_ANSWER_WITHOUT_PEDESTRIAN),
    )
    assert actual == expected


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_FEATURE_SWITCHES={'use_pedestrian_settings_by_transport': True},
)
async def test_pedestrian_transport_type(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings,
        load_json,
):
    # should skip pedestrian courier by transport type, because other
    # pedestrian transport types settings are ok for the order
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [{'values': {'PEDESTRIAN_DISABLED': True}}],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [
                    {
                        'values': {
                            'PEDESTRIAN_ONLY': False,
                            'PEDESTRIAN_SETTINGS': {
                                '__default__': {
                                    'MAX_SEARCH_RADIUS': 5000,
                                    'MAX_ORDER_ROUTE_DISTANCE': 5000,
                                    'MAX_ORDER_ROUTE_TIME': 3600,
                                },
                                'pedestrian': {
                                    'MAX_SEARCH_RADIUS': 5000,
                                    'MAX_ORDER_ROUTE_DISTANCE': 5000,
                                    'MAX_ORDER_ROUTE_TIME': 600,
                                },
                            },
                        },
                    },
                ],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'destination': [37.642579, 55.734997],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'courier'],
        'limit': 5,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected=load_json(_ANSWER_WITHOUT_PEDESTRIAN),
    )
    assert actual == expected


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    EXTRA_EXAMS_BY_ZONE={},
    CANDIDATES_FEATURE_SWITCHES={'use_pedestrian_settings_by_transport': True},
)
async def test_pedestrian_skip_class(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        dispatch_settings,
        load_json,
):
    # should skip courier class in pedestrian search
    dispatch_settings(
        settings=[
            {
                'zone_name': '__default__',
                'tariff_name': '__default__',
                'parameters': [
                    {
                        'values': {
                            'PEDESTRIAN_ONLY': False,
                            'PEDESTRIAN_SETTINGS': {
                                '__default__': {
                                    'MAX_SEARCH_RADIUS': 5000,
                                    'MAX_ORDER_ROUTE_DISTANCE': 5000,
                                    'MAX_ORDER_ROUTE_TIME': 3600,
                                },
                            },
                        },
                    },
                ],
            },
            {
                'zone_name': '__default__',
                'tariff_name': 'courier',
                'parameters': [
                    {
                        'values': {
                            'PEDESTRIAN_ONLY': True,
                            'PEDESTRIAN_SETTINGS': {
                                '__default__': {
                                    'MAX_SEARCH_RADIUS': 5000,
                                    'MAX_ORDER_ROUTE_DISTANCE': 5000,
                                    'MAX_ORDER_ROUTE_TIME': 600,
                                },
                            },
                        },
                    },
                ],
            },
        ],
    )

    await _initialize_positions(driver_positions, chain_busy_drivers)

    body = {
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'destination': [37.642579, 55.734997],
        'max_distance': 10000,
        'allowed_classes': ['econom', 'courier'],
        'limit': 5,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'candidates': [
                {'dbid': 'dbid0', 'uuid': 'uuid0', 'classes': ['econom']},
            ],
        },
    )
    assert actual == expected
