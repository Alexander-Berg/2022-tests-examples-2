import copy

import pytest

SETTINGS_CONFIG = {
    'moscow': [
        {
            'delivery_guarantees': [
                {
                    'orders_created_till': '1970-01-01T12:00:00+00:00',
                    'start_routing_at': '1970-01-01T12:00:00+00:00',
                    'pickup_till': '1970-01-01T13:00:00+00:00',
                    'deliver_till': '1970-01-01T16:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T13:00:00+00:00',
                },
            ],
            'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
            'taxi_classes': [],
            'fake_depot': {'lon': 0, 'lat': 0},
        },
        {
            'corp_client_ids': [
                '111',
                '333',
                '7ff7900803534212a3a66f4d0e114fc2',
            ],
            'delivery_guarantees': [
                {
                    'orders_created_till': '1970-01-01T02:00:00+00:00',
                    'start_routing_at': '1970-01-01T02:10:00+00:00',
                    'pickup_till': '1970-01-01T05:00:00+00:00',
                    'deliver_till': '1970-01-01T06:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T13:00:00+00:00',
                },
                {
                    'orders_created_till': '1970-01-01T19:00:00+00:00',
                    'start_routing_at': '1970-01-01T19:10:00+00:00',
                    'pickup_till': '1970-01-01T21:00:00+00:00',
                    'deliver_till': '1970-01-01T22:00:00+00:00',
                    'waybill_building_deadline': '1970-01-01T23:00:00+00:00',
                },
            ],
            'couriers': [{'park_id': 'park2', 'driver_id': 'driver2'}],
            'taxi_classes': [],
            'fake_depot': {'lon': 0, 'lat': 0},
        },
    ],
}


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=SETTINGS_CONFIG)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_get_intervals(taxi_cargo_sdd):
    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'route_points': [
                {'coordinates': {'lon': 37.1, 'lat': 55.1}},
                {'coordinates': {'lon': 37.5, 'lat': 55.5}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'available_intervals': [
            {
                'from': '2022-02-19T19:10:00+00:00',
                'to': '2022-02-19T22:00:00+00:00',
            },
            {
                'from': '2022-02-20T02:10:00+00:00',
                'to': '2022-02-20T06:00:00+00:00',
            },
        ],
    }


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=SETTINGS_CONFIG)
@pytest.mark.config(CARGO_SDD_DELIVERY_INTERVAL_BUILD_TIME=172800)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_custom_build_interval(taxi_cargo_sdd):
    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'route_points': [
                {'coordinates': {'lon': 37.1, 'lat': 55.1}},
                {'coordinates': {'lon': 37.5, 'lat': 55.5}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'available_intervals': [
            {
                'from': '2022-02-19T19:10:00+00:00',
                'to': '2022-02-19T22:00:00+00:00',
            },
            {
                'from': '2022-02-20T02:10:00+00:00',
                'to': '2022-02-20T06:00:00+00:00',
            },
            {
                'from': '2022-02-20T19:10:00+00:00',
                'to': '2022-02-20T22:00:00+00:00',
            },
            {
                'from': '2022-02-21T02:10:00+00:00',
                'to': '2022-02-21T06:00:00+00:00',
            },
        ],
    }


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=SETTINGS_CONFIG)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_no_zone_in_config(taxi_cargo_sdd):
    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'route_points': [
                {'coordinates': {'lon': 74.59, 'lat': 42.87}},
                {'coordinates': {'lon': 74.58, 'lat': 55.52}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'available_intervals': []}


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=SETTINGS_CONFIG)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_undefined_zone(taxi_cargo_sdd):
    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'route_points': [
                {'coordinates': {'lon': -166, 'lat': 37}},
                {'coordinates': {'lon': -166.01, 'lat': 36.99}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'available_intervals': []}


@pytest.mark.config(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=SETTINGS_CONFIG)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_default_config(taxi_cargo_sdd):
    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': 'c' * 32,
            'route_points': [
                {'coordinates': {'lon': 37.1, 'lat': 55.1}},
                {'coordinates': {'lon': 37.5, 'lat': 55.5}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'available_intervals': [
            {
                'from': '2022-02-19T12:00:00+00:00',
                'to': '2022-02-19T16:00:00+00:00',
            },
        ],
    }


@pytest.mark.config(CARGO_SDD_DELIVERY_INTERVAL_BUILD_TIME=172800)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_empty_intervals_for_corp(taxi_cargo_sdd, taxi_config):
    settings = copy.deepcopy(SETTINGS_CONFIG)
    settings['moscow'][1]['delivery_guarantees'] = []
    taxi_config.set(CARGO_SDD_ZONE_SETTINGS_BY_CLIENTS=settings)
    await taxi_cargo_sdd.invalidate_caches()

    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'route_points': [
                {'coordinates': {'lon': 37.1, 'lat': 55.1}},
                {'coordinates': {'lon': 37.5, 'lat': 55.5}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'available_intervals': []}


@pytest.mark.config(CARGO_SDD_USE_NEW_ZONE_CONFIG=True)
@pytest.mark.geoareas(filename='zones.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2022-02-19T10:23:00Z')
async def test_use_new_config(taxi_cargo_sdd, experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_sdd_delivery_settings_for_clients',
        consumers=['cargo-sdd/delivery-intervals'],
        clauses=[
            {
                'title': 'clause',
                'alias': 'alias',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'corp_client_id',
                                    'arg_type': 'string',
                                    'value': (
                                        '7ff7900803534212a3a66f4d0e114fc2'
                                    ),
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'settings': {
                        'delivery_guarantees': [
                            {
                                'orders_created_till': (
                                    '1970-01-01T02:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T01:10:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T05:00:00+00:00',
                                'deliver_till': '1970-01-01T06:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T13:00:00+00:00'
                                ),
                            },
                            {
                                'orders_created_till': (
                                    '1970-01-01T19:00:00+00:00'
                                ),
                                'start_routing_at': (
                                    '1970-01-01T18:10:00+00:00'
                                ),
                                'pickup_till': '1970-01-01T21:00:00+00:00',
                                'deliver_till': '1970-01-01T22:00:00+00:00',
                                'waybill_building_deadline': (
                                    '1970-01-01T23:00:00+00:00'
                                ),
                            },
                        ],
                        'couriers': [],
                        'copy_fake_courier': {
                            'count': 1,
                            'courier_pattern': {
                                'park_id': 'park1',
                                'driver_id': 'driver1',
                            },
                        },
                        'taxi_classes': [],
                        'fake_depot': {'lon': 0, 'lat': 0},
                    },
                },
            },
        ],
        default_value={
            'settings': {
                'delivery_guarantees': [],
                'couriers': [{'park_id': 'park1', 'driver_id': 'driver1'}],
                'taxi_classes': [],
                'fake_depot': {'lon': 0, 'lat': 0},
            },
        },
    )

    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery-intervals',
        json={
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'route_points': [
                {'coordinates': {'lon': 37.1, 'lat': 55.1}},
                {'coordinates': {'lon': 37.5, 'lat': 55.5}},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'available_intervals': [
            {
                'from': '2022-02-19T18:10:00+00:00',
                'to': '2022-02-19T22:00:00+00:00',
            },
            {
                'from': '2022-02-20T01:10:00+00:00',
                'to': '2022-02-20T06:00:00+00:00',
            },
        ],
    }
