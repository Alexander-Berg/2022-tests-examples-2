# pylint: disable=import-error
import pytest
import yandex.maps.proto.masstransit.summary_pb2 as masstransit


def _make_router_response():
    response = masstransit.Summaries()
    item = response.summaries.add()
    item.weight.time.value = 500
    item.weight.time.text = ''
    item.weight.walking_distance.value = 1200
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


@pytest.mark.config(ROUTER_BICYCLE_MAPS_ENABLED=True)
@pytest.mark.config(ROUTER_PEDESTRIAN_MAPS_ENABLED=True)
@pytest.mark.parametrize(
    [
        'transport_type',
        'expected_pedestrian_called',
        'expected_bicycle_called',
    ],
    [['pedestrian', 1, 0], ['bicycle', 0, 1]],
)
async def test_basic_route(
        mockserver,
        taxi_grocery_routing,
        grocery_depots,
        transport_type,
        expected_pedestrian_called,
        expected_bicycle_called,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_make_router_response(),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-bicycle-router/v2/summary')
    def _mock_bicycle_router(request):
        return mockserver.make_response(
            response=_make_router_response(),
            status=200,
            content_type='application/x-protobuf',
        )

    depot = grocery_depots.add_depot(depot_test_id=1)

    response = await taxi_grocery_routing.post(
        '/internal/grocery-routing/v1/route',
        json={
            # pylint: disable=protected-access
            'source': depot._zones[0]._zone_center,
            'destination': {'lat': -10, 'lon': -10},
            'transport_type': transport_type,
        },
        params={'intent': 'test_intent'},
    )

    assert response.status == 200
    assert response.json() == {'distance': 1200, 'eta': 500}
    assert _mock_pedestrian_router.times_called == expected_pedestrian_called
    assert _mock_bicycle_router.times_called == expected_bicycle_called

    response = await taxi_grocery_routing.post(
        '/internal/grocery-routing/v1/route',
        json={
            # pylint: disable=protected-access
            'source': depot._zones[0]._zone_center,
            'destination': {'lat': -10.0001, 'lon': -10},
            'transport_type': transport_type,
        },
        params={'intent': 'test_intent'},
    )

    assert response.status == 200
    assert response.json() == {'distance': 1200, 'eta': 500}
    assert _mock_pedestrian_router.times_called == expected_pedestrian_called
    assert _mock_bicycle_router.times_called == expected_bicycle_called

    await taxi_grocery_routing.invalidate_caches()

    response = await taxi_grocery_routing.post(
        '/internal/grocery-routing/v1/route',
        json={
            # pylint: disable=protected-access
            'source': depot._zones[0]._zone_center,
            'destination': {'lat': -10.0001, 'lon': -10.0001},
            'transport_type': transport_type,
        },
        params={'intent': 'test_intent'},
    )

    assert response.status == 200
    assert response.json() == {'distance': 1200, 'eta': 500}
    assert _mock_pedestrian_router.times_called == expected_pedestrian_called
    assert _mock_bicycle_router.times_called == expected_bicycle_called


@pytest.mark.config(ROUTER_BICYCLE_MAPS_ENABLED=True)
@pytest.mark.config(ROUTER_PEDESTRIAN_MAPS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    name='grocery_routing_settings',
    consumers=['grocery_routing/routing'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enable_routing': False},
)
async def test_routing_disabled(
        mockserver, taxi_grocery_routing, grocery_depots,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_make_router_response(),
            status=200,
            content_type='application/x-protobuf',
        )

    depot = grocery_depots.add_depot(depot_test_id=1)

    response = await taxi_grocery_routing.post(
        '/internal/grocery-routing/v1/route',
        json={
            # pylint: disable=protected-access
            'source': depot._zones[0]._zone_center,
            'destination': {'lat': -10, 'lon': -10},
            'transport_type': 'pedestrian',
        },
        params={'intent': 'test_intent'},
    )

    assert response.status == 404
    assert _mock_pedestrian_router.times_called == 0


@pytest.mark.config(ROUTER_BICYCLE_MAPS_ENABLED=True)
@pytest.mark.config(ROUTER_PEDESTRIAN_MAPS_ENABLED=True)
@pytest.mark.parametrize(
    [
        'transport_type',
        'expected_pedestrian_called',
        'expected_bicycle_called',
    ],
    [['pedestrian', 1, 0]],
)
async def test_route_exception_429(
        mockserver,
        taxi_grocery_routing,
        grocery_depots,
        transport_type,
        expected_pedestrian_called,
        expected_bicycle_called,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_make_router_response(),
            status=429,
            content_type='application/x-protobuf',
        )

    depot = grocery_depots.add_depot(depot_test_id=1)

    response = await taxi_grocery_routing.post(
        '/internal/grocery-routing/v1/route',
        json={
            # pylint: disable=protected-access
            'source': depot._zones[0]._zone_center,
            'destination': {'lat': -10, 'lon': -10},
            'transport_type': transport_type,
        },
        params={'intent': 'test_intent'},
    )

    assert response.status == 429
