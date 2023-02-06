import datetime

import pytest

from . import configs


def calc_geojson_sqare_around_point(point, delta=1):
    return (
        '{"coordinates": [[['
        + str(point['lon'] - delta)
        + ','
        + str(point['lat'] - delta)
        + '], '
        '['
        + str(point['lon'] - delta)
        + ','
        + str(point['lat'] + delta)
        + '], '
        '['
        + str(point['lon'] + delta)
        + ','
        + str(point['lat'] + delta)
        + '], '
        '['
        + str(point['lon'] + delta)
        + ','
        + str(point['lat'] - delta)
        + '], '
        '['
        + str(point['lon'] - delta)
        + ','
        + str(point['lat'] - delta)
        + ']]], "type": "Polygon"}'
    )


USER_LOCATION = {'lon': 37.61, 'lat': 55.75}

DEFAULT_TIME = datetime.datetime.fromtimestamp(
    1650600373 / 1000.0, tz=datetime.timezone.utc,
)

FUTURE_TIME = datetime.datetime.fromtimestamp(
    (1650600373 / 1000.0) + 100, tz=datetime.timezone.utc,
)


def insert_into_geooffer_zones(
        cursor,
        zone_id,
        zone_type,
        zone_geojson,
        status,
        updated=DEFAULT_TIME,
        created=DEFAULT_TIME,
):
    cursor.execute(
        'INSERT INTO grocery_delivery_conditions.geooffer_zones '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (zone_id, zone_type, zone_geojson, status, updated, created),
    )


@pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': False,
        'calc_route_to_pin': False,
        'get_geo_offer_zone': True,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_geooffer_type_in_exp_kwargs(
        taxi_grocery_delivery_conditions, experiments3, pgsql,
):
    geo_offer_zone_id = '1'
    geo_offer_zone_type = '271'
    zone_geojson = calc_geojson_sqare_around_point(USER_LOCATION)

    cursor = pgsql['grocery_delivery_conditions'].cursor()
    insert_into_geooffer_zones(
        cursor, geo_offer_zone_id, geo_offer_zone_type, zone_geojson, 'active',
    )

    experiments3.add_config(
        name='grocery_delivery_conditions_user_type',
        consumers=['grocery-delivery-conditions/user_order_info_extended'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'type': 'string'},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_delivery_conditions_user_type',
    )

    json = {'position': USER_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['meta']['geo_offer_zone']['id'] == geo_offer_zone_id
    assert (
        response.json()['meta']['geo_offer_zone']['type']
        == geo_offer_zone_type
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    matched_kwargs = match_tries[0].kwargs

    assert matched_kwargs['geo_offer_zone_type'] == geo_offer_zone_type


@pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': False,
        'calc_route_to_pin': False,
        'get_geo_offer_zone': True,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_geooffer_type_in_exp_kwargs_two_var_chose_newest(
        taxi_grocery_delivery_conditions, experiments3, pgsql,
):
    geo_offer_zone_id = '1'
    geo_offer_zone_type = '271'
    zone_geojson = calc_geojson_sqare_around_point(USER_LOCATION)

    cursor = pgsql['grocery_delivery_conditions'].cursor()

    insert_into_geooffer_zones(
        cursor,
        zone_id='2',
        zone_type='382',
        zone_geojson=zone_geojson,
        status='active',
        updated=DEFAULT_TIME,
    )

    # зона создана в то же время, но время обновления раньше
    insert_into_geooffer_zones(
        cursor,
        geo_offer_zone_id,
        geo_offer_zone_type,
        zone_geojson,
        'active',
        updated=FUTURE_TIME,
    )

    experiments3.add_config(
        name='grocery_delivery_conditions_user_type',
        consumers=['grocery-delivery-conditions/user_order_info_extended'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'type': 'string'},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_delivery_conditions_user_type',
    )

    json = {'position': USER_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['meta']['geo_offer_zone']['id'] == geo_offer_zone_id
    assert (
        response.json()['meta']['geo_offer_zone']['type']
        == geo_offer_zone_type
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    matched_kwargs = match_tries[0].kwargs

    assert matched_kwargs['geo_offer_zone_type'] == geo_offer_zone_type


@pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': False,
        'calc_route_to_pin': False,
        'get_geo_offer_zone': True,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_geooffer_type_not_in_exp_kwargs_zone_inactive(
        taxi_grocery_delivery_conditions, experiments3, pgsql,
):
    geo_offer_zone_id = '1'
    geo_offer_zone_type = '271'
    zone_geojson = calc_geojson_sqare_around_point(USER_LOCATION)

    cursor = pgsql['grocery_delivery_conditions'].cursor()
    insert_into_geooffer_zones(
        cursor,
        geo_offer_zone_id,
        geo_offer_zone_type,
        zone_geojson,
        'inactive',
    )

    experiments3.add_config(
        name='grocery_delivery_conditions_user_type',
        consumers=['grocery-delivery-conditions/user_order_info_extended'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'type': 'string'},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_delivery_conditions_user_type',
    )

    json = {'position': USER_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert 'geo_offer_zone' not in response.json()['meta']

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    matched_kwargs = match_tries[0].kwargs

    assert 'geo_offer_zone_type' not in matched_kwargs


@pytest.mark.experiments3(
    name='grocery_delivery_conditions_calc_settings',
    consumers=['grocery-delivery-conditions/user_order_info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'check_taxi_price': False,
        'calc_route_to_pin': False,
        'get_geo_offer_zone': True,
        'get_surge': False,
        'get_delivery_eta': False,
    },
    is_config=True,
)
@configs.EXP3_STORE_SETTINGS
@configs.EXP3_DELIVERY_CONDITIONS
async def test_geooffer_type_not_in_exp_kwargs_zone_user_isnt_in_active_zone(
        taxi_grocery_delivery_conditions, experiments3, pgsql,
):
    geo_offer_zone_id = '1'
    geo_offer_zone_type = '271'
    zone_centre = {
        'lon': USER_LOCATION['lon'] + 10,
        'lat': USER_LOCATION['lat'] + 10,
    }
    zone_geojson = calc_geojson_sqare_around_point(zone_centre)

    cursor = pgsql['grocery_delivery_conditions'].cursor()
    insert_into_geooffer_zones(
        cursor, geo_offer_zone_id, geo_offer_zone_type, zone_geojson, 'active',
    )

    experiments3.add_config(
        name='grocery_delivery_conditions_user_type',
        consumers=['grocery-delivery-conditions/user_order_info_extended'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'type': 'string'},
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_delivery_conditions_user_type',
    )

    json = {'position': USER_LOCATION, 'meta': {}}

    headers = {'X-Yandex-UID': '12345'}

    response = await taxi_grocery_delivery_conditions.post(
        '/internal/v1/grocery-delivery-conditions/v1/match-create',
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert 'geo_offer_zone' not in response.json()['meta']

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    matched_kwargs = match_tries[0].kwargs

    assert 'geo_offer_zone_type' not in matched_kwargs
