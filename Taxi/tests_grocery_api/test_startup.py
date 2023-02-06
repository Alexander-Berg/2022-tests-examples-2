import datetime

import pytest

from . import experiments
from . import tests_headers

MOSCOW_LAVKA = {'region_id': 213, 'id': '12345678'}
RUSSIAN_LAVKA = {'region_id': 225, 'id': '87654321'}
ENABLED_MOSCOW = {'region_id': 213, 'enabled': True}
ENABLED_RUSSIA = {'region_id': 225, 'enabled': True}
DISABLED_RUSSIA = {'region_id': 225, 'enabled': False}
DISABLED_KAZAN = {'region_id': 43, 'enabled': False}


def get_demo_lavka_experiment(locations):
    return pytest.mark.experiments3(
        name='demo_lavka',
        consumers=['grocery-api/startup'],
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Россия',
                'value': {'demo_lavka_id': location['id']},
                'is_signal': False,
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': location['region_id'],
                        'arg_name': 'region_id',
                        'arg_type': 'int',
                    },
                },
                'is_paired_signal': False,
            }
            for location in locations
        ],
    )


def get_grocery_geo_onboarding(locations):
    return pytest.mark.experiments3(
        name='grocery_geo_onboarding',
        consumers=['grocery-api/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Россия',
                'value': {'enabled': location['enabled']},
                'is_signal': False,
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': location['region_id'],
                        'arg_name': 'region_id',
                        'arg_type': 'int',
                    },
                },
                'is_paired_signal': False,
            }
            for location in locations
        ],
    )


# When coordinates are received and lavka exists
async def test_happy_path(taxi_grocery_api, overlord_catalog, grocery_depots):
    """ Should return existing depot in this position """

    latitude = 10
    longitude = 10
    legacy_depot_id = '123456'
    country_iso3 = 'FRA'
    depot_id = '1337'
    region_id = 10502

    overlord_catalog.add_depot(
        location=[longitude, latitude],
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
        country_iso3=country_iso3,
        region_id=region_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int(legacy_depot_id),
        depot_id=depot_id,
        country_iso3=country_iso3,
        region_id=region_id,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['available'] is True
    assert body['exists'] is True
    assert body['depot_id'] == legacy_depot_id
    assert body['region_id'] == region_id
    assert body['country_iso3'] == country_iso3
    assert 'demo_lavka' not in body
    assert 'coming_soon' not in body


# When there is no lavka here, but it exists in the city
@get_demo_lavka_experiment([MOSCOW_LAVKA])
async def test_no_lavka_but_city_is_present(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return demo lavka for region_id obtained by geo """

    # Где-то в Москве
    latitude = 55.70
    longitude = 37.50

    lavka_location = {'location': [10, 10]}
    overlord_catalog.add_depot(
        legacy_depot_id=MOSCOW_LAVKA['id'], position=lavka_location,
    )
    grocery_depots.add_depot(
        depot_test_id=int(MOSCOW_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert body['demo_lavka'] == lavka_location
    assert body['country_iso3'] == 'RUS'
    assert body['region_id'] == 213
    assert 'depot_id' not in body


# When there is no lavka here, but it exists in the conutry
@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_no_lavka_but_country_is_present(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return demo lavka for country obtained by geo """

    # Барнаул, Алтайский Край
    latitude = 53.35
    longitude = 83.72

    lavka_location = {'location': [54, 84]}
    overlord_catalog.add_depot(
        legacy_depot_id=RUSSIAN_LAVKA['id'], position=lavka_location,
    )
    grocery_depots.add_depot(
        depot_test_id=int(RUSSIAN_LAVKA['id']),
        location=lavka_location['location'],
    )
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert body['demo_lavka'] == lavka_location
    assert body['country_iso3'] == 'RUS'
    assert body['region_id'] == 197
    assert 'depot_id' not in body


# When there is no lavka for this country
@get_demo_lavka_experiment([RUSSIAN_LAVKA])
async def test_no_lavka_in_the_country(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return nothing as there is no depots in this country """

    # Где-то в Монголии
    latitude = 43.13
    longitude = 104.2

    lavka_location = {'location': [54, 84]}
    overlord_catalog.add_depot(
        legacy_depot_id=RUSSIAN_LAVKA['id'], position={'location': [50, 70]},
    )
    grocery_depots.add_depot(
        depot_test_id=int(MOSCOW_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert 'country_iso3' not in body  # потому что неподдерживаемая страна
    assert 'demo_lavka' not in body
    assert 'depot_id' not in body


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_no_coordinates_city_ip(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return demo lavka for region_id obtained by ip """

    lavka_location = {'location': [50, 70]}
    overlord_catalog.add_depot(
        legacy_depot_id=MOSCOW_LAVKA['id'], position=lavka_location,
    )
    grocery_depots.add_depot(
        depot_test_id=int(MOSCOW_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup',
        headers={
            'X-Remote-IP': '81.195.17.222',  # Московский IP
            **tests_headers.HEADERS,
        },
        json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert body['country_iso3'] == 'RUS'
    assert body['region_id'] == 213
    assert body['demo_lavka'] == lavka_location
    assert 'depot_id' not in body


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_no_coordinates_country_ip(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return demo lavka for country obtained by ip """

    lavka_location = {'location': [50, 70]}

    overlord_catalog.add_depot(
        legacy_depot_id=RUSSIAN_LAVKA['id'], position=lavka_location,
    )
    grocery_depots.add_depot(
        depot_test_id=int(RUSSIAN_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup',
        headers={
            'X-Remote-IP': '5.101.23.13',  # Казанский IP
            **tests_headers.HEADERS,
        },
        json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert body['demo_lavka'] == lavka_location
    assert body['country_iso3'] == 'RUS'
    assert body['region_id'] == 43
    assert 'depot_id' not in body


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_no_lavka_in_the_country_by_ip(
        taxi_grocery_api, overlord_catalog,
):
    """ Should return nothing as there is no depots in this country """

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup',
        headers={
            'X-Remote-IP': '43.243.160.0',  # Монгольский IP
            **tests_headers.HEADERS,
        },
        json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert 'demo_lavka' not in body
    assert 'depot_id' not in body


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_no_ip(taxi_grocery_api, overlord_catalog):
    """ Should return nothing as user country and region_id are unknown """

    lavka_location = {'location': [50, 70]}
    overlord_catalog.add_depot(
        legacy_depot_id=RUSSIAN_LAVKA['id'], position=lavka_location,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup', headers=tests_headers.HEADERS, json={},
    )

    body = response.json()

    assert body['available'] is False
    assert body['exists'] is False
    assert 'demo_lavka' not in body
    assert 'depot_id' not in body


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_closed_lavka(taxi_grocery_api, overlord_catalog):
    """ Should return exists == True and available == False
    for existing closed depot """

    latitude = 10
    longitude = 10
    legacy_depot_id = '123456'
    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id=legacy_depot_id,
        state='closed',
    )
    overlord_catalog.set_depot_status('closed')

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['exists'] is True
    assert body['available'] is False
    assert 'demo_lavka' not in body
    assert 'coming_soon' not in body
    assert body['depot_id'] == legacy_depot_id


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
@get_grocery_geo_onboarding([ENABLED_RUSSIA])
async def test_coming_soon_depot(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return exists == True and available == False
    and coming_soon == True for existing coming soon depot.
    Also there should be demo lavka in response """

    latitude = 55
    longitude = 37
    legacy_depot_id = '123456'
    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id=legacy_depot_id,
        state='coming_soon',
    )
    overlord_catalog.set_depot_status('coming_soon')
    lavka_location = {'location': [50, 70]}
    overlord_catalog.add_depot(
        legacy_depot_id=RUSSIAN_LAVKA['id'], position=lavka_location,
    )
    grocery_depots.add_depot(
        depot_test_id=int(RUSSIAN_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['exists'] is True
    assert body['available'] is False
    assert body['demo_lavka'] == lavka_location
    assert body['coming_soon'] is True
    assert body['depot_id'] == legacy_depot_id


@get_demo_lavka_experiment([MOSCOW_LAVKA, RUSSIAN_LAVKA])
async def test_disabled_exp_coming_soon(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    """ Should return exists == False and available == False
    and no coming soon in response if geo onboarding is disalbed.
    Also there should be demo lavka in response """

    latitude = 55
    longitude = 37
    legacy_depot_id = '123456'
    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id=legacy_depot_id,
        state='coming_soon',
    )
    overlord_catalog.set_depot_status('coming_soon')

    lavka_location = {'location': [50, 70]}
    grocery_depots.add_depot(
        depot_test_id=int(RUSSIAN_LAVKA['id']),
        depot_id='1337',
        location=lavka_location['location'],
        status='coming_soon',
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()

    assert body['exists'] is False
    assert body['available'] is False
    assert body['demo_lavka'] == lavka_location
    assert 'coming_soon' not in body
    assert 'depot_id' not in body


@get_grocery_geo_onboarding([ENABLED_MOSCOW])
@pytest.mark.parametrize('depot_exists', [True, False])
async def test_onboarding_by_city(
        taxi_grocery_api, overlord_catalog, depot_exists,
):
    """ Should return onboarding value by city region_id
    Result shoud be independent of depot at this point """

    latitude = 55.747620
    longitude = 37.594233
    legacy_depot_id = '123456'
    if depot_exists:
        overlord_catalog.add_location(
            location=[longitude, latitude],
            depot_id='1337',
            legacy_depot_id=legacy_depot_id,
        )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()
    assert body['onboarding'] is True
    assert body['exists'] == depot_exists


@get_grocery_geo_onboarding([ENABLED_RUSSIA])
@pytest.mark.parametrize('depot_exists', [True, False])
async def test_onboarding_by_country(
        taxi_grocery_api, overlord_catalog, depot_exists,
):
    """ Should return onboarding value by country region_id
    Result shoud be independent of depot at this point """

    latitude = 55
    longitude = 37
    legacy_depot_id = '123456'
    if depot_exists:
        overlord_catalog.add_location(
            location=[longitude, latitude],
            depot_id='1337',
            legacy_depot_id=legacy_depot_id,
        )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()
    assert body['onboarding'] is True
    assert body['exists'] == depot_exists


@get_grocery_geo_onboarding([ENABLED_RUSSIA, DISABLED_KAZAN])
@pytest.mark.parametrize('depot_exists', [True, False])
async def test_onboarding_city_override(
        taxi_grocery_api, overlord_catalog, depot_exists,
):
    """ Onboarding config result by city overrides result by country
    Result shoud be independent of depot at this point """

    latitude = 55.784577
    longitude = 49.109118
    legacy_depot_id = '123456'
    if depot_exists:
        overlord_catalog.add_location(
            location=[longitude, latitude],
            depot_id='1337',
            legacy_depot_id=legacy_depot_id,
        )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()
    assert body['onboarding'] is False
    assert body['exists'] == depot_exists


# При значение эксперимента grocery_to_market_migration::enabled = true
# 1) если текущее время > grocery_to_market_migration:enforce_migration_date
# отдаем из ручки move_to_market = enforce
# 2) если текущее время < grocery_to_market_migration:enforce_migration_date
# отдаем из ручки move_to_market = invite
# если enabled=false move_to_market не отдается из ручки
@pytest.mark.parametrize(
    'current_time,migration_date,enabled,migration_value',
    [
        (
            '2021-11-17T10:00:00+00:00',
            '2021-11-17T11:00:00+00:00',
            False,
            'invite',
        ),
        (
            '2021-11-17T10:00:00+00:00',
            '2021-11-17T11:00:00+00:00',
            True,
            'invite',
        ),
        (
            '2021-11-17T12:00:00+00:00',
            '2021-11-17T11:00:00+00:00',
            True,
            'enforce',
        ),
        (
            '2021-11-17T13:00:00+00:00',
            '2021-11-17T13:00:00+03:00',
            True,
            'enforce',
        ),
        (
            '2021-11-17T11:00:00+00:00',
            '2021-11-17T15:00:00+03:00',
            True,
            'invite',
        ),
    ],
)
async def test_market_migration(
        taxi_grocery_api,
        overlord_catalog,
        mocked_time,
        experiments3,
        current_time,
        migration_date,
        enabled,
        migration_value,
):
    experiments3.add_experiment(
        name='grocery_to_market_migration',
        consumers=['grocery-api/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': enabled,
                    'enforce_migration_date': migration_date,
                },
            },
        ],
    )
    mocked_time.set(datetime.datetime.fromisoformat(current_time))
    latitude = 55.784577
    longitude = 49.109118
    legacy_depot_id = '123456'
    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id=legacy_depot_id,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    body = response.json()
    if not enabled:
        assert 'move_to_market' not in body
    else:
        assert body['move_to_market'] == migration_value


@pytest.mark.parametrize(
    'legacy_depot_id,migration_enabled', [('123', True), ('456', False)],
)
async def test_market_migration_depot_id(
        taxi_grocery_api,
        overlord_catalog,
        experiments3,
        legacy_depot_id,
        migration_enabled,
):
    """ grocery_to_market_migration experiment properly
    works with depot_id kwarg """

    experiments3.add_experiment(
        name='grocery_to_market_migration',
        consumers=['grocery-api/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Enabled for depot',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_type': 'string',
                        'arg_name': 'depot_id',
                        'value': '123',
                    },
                },
                'value': {
                    'enabled': True,
                    'enforce_migration_date': '2021-07-15T15:30:00+03:00',
                },
            },
        ],
    )

    latitude = 55.784577
    longitude = 49.109118
    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id=legacy_depot_id,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    assert ('move_to_market' in response.json()) == migration_enabled


async def test_market_migration_region_id(
        taxi_grocery_api, overlord_catalog, experiments3, grocery_depots,
):
    """ pass depot region_id to grocery_to_market_migration experiment"""

    region_id = 228
    experiments3.add_experiment(
        name='grocery_to_market_migration',
        consumers=['grocery-api/startup'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Enabled for depot region',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_type': 'int',
                        'arg_name': 'region_id',
                        'value': region_id,
                    },
                },
                'value': {
                    'enabled': True,
                    'enforce_migration_date': '2021-07-15T15:30:00+03:00',
                },
            },
            {
                'title': 'disabled for geobase region',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_type': 'int',
                        'arg_name': 'region_id',
                        'value': MOSCOW_LAVKA['region_id'],
                    },
                },
                'value': {
                    'enabled': False,
                    'enforce_migration_date': '2021-07-15T15:30:00+03:00',
                },
            },
        ],
    )

    latitude = 55.784577
    longitude = 49.109118
    depot_id = '1337'
    overlord_catalog.add_depot(
        location=[longitude, latitude],
        depot_id=depot_id,
        legacy_depot_id=MOSCOW_LAVKA['id'],
    )
    grocery_depots.add_depot(
        depot_test_id=int(MOSCOW_LAVKA['id']),
        depot_id=depot_id,
        location=[longitude, latitude],
        region_id=region_id,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={},
    )

    assert response.json()['move_to_market']


@get_demo_lavka_experiment([MOSCOW_LAVKA])
@pytest.mark.parametrize(
    'approximate_coordinate, depot_state, demo_lavka_in_response',
    [(True, 'open', False), (True, 'closed', True), (False, 'closed', False)],
)
async def test_approximate_coordinate(
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        approximate_coordinate,
        depot_state,
        demo_lavka_in_response,
):
    """ if approximate_coordinate in request - return
    store on if depot is active """

    latitude = 55.70
    longitude = 37.50

    lavka_location = {'location': [10, 10]}
    overlord_catalog.add_depot(legacy_depot_id=MOSCOW_LAVKA['id'])

    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id='1337',
    )
    overlord_catalog.set_depot_status(depot_state)
    grocery_depots.add_depot(
        depot_test_id=int(MOSCOW_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={'approximate_coordinate': approximate_coordinate},
    )

    assert response.status_code == 200
    assert ('demo_lavka' in response.json()) == demo_lavka_in_response


@pytest.mark.parametrize(
    'yandex_uid, personal_phone_id, newbie_scoring_enabled',
    [
        ('yandex-uid', 'personal-phone-id', False),
        ('yandex-uid', '', True),
        (None, 'personal-phone-id', True),
        ('yandex-uid', 'personal-phone-id', True),
    ],
)
async def test_score_newbie(
        taxi_grocery_api,
        taxi_config,
        processing,
        experiments3,
        yandex_uid,
        personal_phone_id,
        newbie_scoring_enabled,
):
    latitude = 10
    longitude = 10
    app_info = (
        'app_brand=yataxi,app_ver3=0,device_make=xiaomi,'
        'app_name=mobileweb_android,app_build=release,'
        'device_model=redmi 6,app_ver2=9,app_ver1=4,platform_ver1=9'
    )
    headers = {
        'X-Yandex-UID': yandex_uid,
        'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}',
        'X-Request-Application': app_info,
    }
    experiments.grocery_api_enable_newbie_scoring(
        experiments3=experiments3, enabled=newbie_scoring_enabled,
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=headers,
        json={},
    )
    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='users'))

    if newbie_scoring_enabled and yandex_uid and personal_phone_id:
        assert len(events) == 1
        event = events[0]

        assert event.payload['personal_phone_id'] == personal_phone_id
        assert event.payload['user_identity'] == {
            'yandex_uid': yandex_uid,
            'bound_yandex_uids': [],
        }
        assert event.payload['range'] == {'count': 1}
        assert event.payload['reason'] == 'score_newbie'
        assert 'event_policy' not in event.payload
    else:
        assert not events


# Проверяем, что создается офер и отдается в ответе ручки
@pytest.mark.parametrize(
    'need_offer,offer_in_response',
    [
        pytest.param(False, False, id='need_offer=False'),
        pytest.param(None, False, id='no need_offer'),
        pytest.param(True, True, id='need_offer=True'),
    ],
)
@pytest.mark.parametrize(
    'depot_state,has_depot',
    [
        pytest.param('open', True, id='open depot'),
        pytest.param(
            'coming_soon',
            True,
            marks=[get_demo_lavka_experiment([RUSSIAN_LAVKA])],
            id='no depot, has demo',
        ),
        pytest.param('coming_soon', False, id='no depot, no demo'),
    ],
)
async def test_create_offer(
        taxi_grocery_api,
        overlord_catalog,
        grocery_depots,
        need_offer,
        offer_in_response,
        depot_state,
        has_depot,
):

    latitude = 55
    longitude = 37
    legacy_depot_id = '123456'
    overlord_catalog.add_location(
        location=[longitude, latitude],
        depot_id='1337',
        legacy_depot_id=legacy_depot_id,
        state=depot_state,
    )
    overlord_catalog.set_depot_status(depot_state)
    lavka_location = {'location': [50, 70]}
    overlord_catalog.add_depot(
        legacy_depot_id=RUSSIAN_LAVKA['id'], position=lavka_location,
    )
    grocery_depots.add_depot(
        depot_test_id=int(RUSSIAN_LAVKA['id']),
        location=lavka_location['location'],
    )

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/startup?latitude={latitude}&longitude={longitude}',
        headers=tests_headers.HEADERS,
        json={'need_offer': need_offer},
    )

    assert not (
        ('offer_id' in response.json()) ^ (offer_in_response and has_depot)
    )
