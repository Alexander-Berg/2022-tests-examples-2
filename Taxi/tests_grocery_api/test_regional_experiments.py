import copy

import pytest

from testsuite.utils import ordered_object

from . import tests_headers


RUSSIA_COUNTRY_ID = 225
GBR_COUNTRY_ID = 102
FR_COUNTRY_ID = 124

# Moscow
DEFAULT_LOCATION = [37.6, 55.7]
DEFAULT_REGION_ID = 213
DEFAULT_COUNTRY_ID = RUSSIA_COUNTRY_ID
DEFAULT_ISO = 'ru'

LOCALIZED_VALUE = {'ru': 'Локализован', 'en': 'Localized', 'he': 'מקומי'}


def _prepare_predicate(country_iso2=None, region_id=None):
    if country_iso2 is None and region_id is None:
        return {'type': 'true'}

    country_iso2_predicate = None
    if country_iso2 is not None:
        country_iso2_predicate = {
            'init': {
                'arg_name': 'country_iso2',
                'arg_type': 'string',
                'value': country_iso2,
            },
            'type': 'eq',
        }

    region_id_predicate = None
    if region_id is not None:
        region_id_predicate = {
            'init': {
                'arg_name': 'region_id',
                'arg_type': 'int',
                'value': region_id,
            },
            'type': 'eq',
        }

    if region_id_predicate is not None and country_iso2_predicate is not None:
        return {
            'init': {
                'predicates': [region_id_predicate, country_iso2_predicate],
            },
            'type': 'all_of',
        }
    if country_iso2_predicate is not None:
        return country_iso2_predicate
    return region_id_predicate


def _add_config(
        experiments3,
        expected_result,
        should_match,
        *,
        name,
        value,
        country_iso2=None,
        region_id=None,
        # configs always have default value
        default_value={},
):
    experiments3.add_config(
        name=name,
        consumers=['grocery-api/regional-experiments'],
        clauses=[
            {
                'title': 'does-not-matter',
                'predicate': _prepare_predicate(country_iso2, region_id),
                'value': value,
            },
        ],
        default_value=default_value,
    )
    expected_result.append(
        {
            'cache_status': 'no_cache',
            'name': name,
            'value': value if should_match else default_value,
        },
    )


def _add_experiment(
        experiments3,
        expected_result,
        should_match,
        *,
        name,
        value,
        country_iso2=None,
        region_id=None,
        default_value=None,
):
    experiments3.add_experiment(
        name=name,
        consumers=['grocery-api/regional-experiments'],
        clauses=[
            {
                'title': 'does-not-matter',
                'predicate': _prepare_predicate(country_iso2, region_id),
                'value': value,
            },
        ],
        default_value=default_value,
    )
    if should_match:
        expected_result.append(
            {'cache_status': 'no_cache', 'name': name, 'value': value},
        )
    elif default_value is not None:
        expected_result.append(
            {'cache_status': 'no_cache', 'name': name, 'value': default_value},
        )


def _prepare_tests(experiments3):
    result = []
    # checks that config can be matched by region_id
    # and country_iso2 kwargs

    _add_config(
        experiments3,
        result,
        True,
        name='config_by_region_and_country',
        value={'conf_arg1': 'conf_val1'},
        country_iso2=DEFAULT_ISO,
        region_id=DEFAULT_REGION_ID,
    )
    # checks that config returns default value on mismatch
    _add_config(
        experiments3,
        result,
        False,
        name='config_by_bad_region',
        value={'conf_arg2': 'conf_val2'},
        region_id=123456,
    )
    _add_config(
        experiments3,
        result,
        False,
        name='config_by_bad_country',
        value={'conf_arg3': 'conf_val3'},
        country_iso2='aa',
        default_value={'conf_default_arg1': 'conf_default_value1'},
    )
    # checks that experiment can be matched by region_id
    # and country_iso2 kwargs
    _add_experiment(
        experiments3,
        result,
        True,
        name='experiment_by_region_and_country',
        value={'exp_arg1': 'exp_val1'},
        country_iso2=DEFAULT_ISO,
        region_id=DEFAULT_REGION_ID,
    )
    # checks that experiment returns default value on mismatch
    # if it is set
    _add_experiment(
        experiments3,
        result,
        False,
        name='experiment_by_bad_region',
        value={'exp_arg2': 'exp_arg2'},
        region_id=123456,
    )
    _add_experiment(
        experiments3,
        result,
        False,
        name='experiment_by_bad_country',
        value={'exp_arg3': 'exp_arg3'},
        country_iso2='aa',
        default_value={'exp_default_arg1': 'exp_default_val1'},
    )
    return result


async def test_geo_info_from_depot(
        taxi_grocery_api, overlord_catalog, experiments3, grocery_depots,
):
    """ Checks case when region_id and country_iso2
    were extracted from depot_info """

    location = [10, 10]
    depot_id = 'test-depot'
    overlord_catalog.add_depot(legacy_depot_id='123', depot_id=depot_id)
    overlord_catalog.add_location(
        location=location, legacy_depot_id='123', depot_id=depot_id,
    )
    grocery_depots.add_depot(
        depot_test_id=int('123'),
        depot_id=depot_id,
        region_id=DEFAULT_REGION_ID,
        country_iso2=DEFAULT_ISO,
        location=location,
    )

    expected_result = _prepare_tests(experiments3)

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=tests_headers.HEADERS,
        json={'position': {'lon': location[0], 'lat': location[1]}},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json()['typed_experiments']['items'], expected_result, [''],
    )


async def test_geo_info_by_position(taxi_grocery_api, experiments3):
    """ Checks case when region_id and country_iso2
    were resolved by position """

    location = DEFAULT_LOCATION

    expected_result = _prepare_tests(experiments3)

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=tests_headers.HEADERS,
        json={'position': {'lon': location[0], 'lat': location[1]}},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json()['typed_experiments']['items'], expected_result, [''],
    )


async def test_geo_info_by_ip(taxi_grocery_api, experiments3):
    """ Checks case when region_id and country_iso2
    were resolved by ip address """

    expected_result = _prepare_tests(experiments3)

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers={**tests_headers.HEADERS, 'X-Remote-IP': '141.8.167.197'},
        json={},
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json()['typed_experiments']['items'], expected_result, [''],
    )


@pytest.mark.parametrize(
    'location, region_id',
    [
        pytest.param(DEFAULT_LOCATION, DEFAULT_COUNTRY_ID, id='msk_ru'),
        pytest.param([30, 59.9], DEFAULT_COUNTRY_ID, id='spb_ru'),
        pytest.param([131.88, 43.11], DEFAULT_COUNTRY_ID, id='vlk_ru'),
        pytest.param([0, 51], GBR_COUNTRY_ID, id='london_gb'),
        pytest.param([-4.25, 55.86], GBR_COUNTRY_ID, id='glasgow_gb'),
        pytest.param([2.35, 48.85], FR_COUNTRY_ID, id='paris_fr'),
    ],
)
async def test_regional_id_by_pos(
        taxi_grocery_api, experiments3, location, region_id,
):

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=tests_headers.HEADERS,
        json={'position': {'lon': location[0], 'lat': location[1]}},
    )
    assert response.status_code == 200
    assert response.json()['region_id'] == region_id


@pytest.mark.parametrize(
    'ip_addr, region_id',
    [
        pytest.param('141.8.167.197', DEFAULT_COUNTRY_ID, id='ru'),
        pytest.param('193.63.94.20', GBR_COUNTRY_ID, id='gbr'),
    ],
)
async def test_regional_id_by_ip(
        taxi_grocery_api, experiments3, ip_addr, region_id,
):
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers={**tests_headers.HEADERS, 'X-Remote-IP': ip_addr},
        json={},
    )
    assert response.json()['region_id'] == region_id


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='some-config-with-l10n',
    consumers=['grocery-api/regional-experiments'],
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'l10n': [
                    {
                        'key': 'simple-key',
                        'tanker': {
                            'key': 'simple_key',
                            'keyset': 'virtual_catalog',
                        },
                        'default': 'Should not return default',
                    },
                    {
                        'key': 'key-not-found',
                        'tanker': {
                            'key': 'key_not_found',
                            'keyset': 'virtual_catalog',
                        },
                        'default': 'Should return default',
                    },
                ],
            },
        },
    ],
    default_value=True,
)
@pytest.mark.translations(virtual_catalog={'simple_key': LOCALIZED_VALUE})
@pytest.mark.parametrize('locale', [None, 'ru', 'en', 'he'])
@pytest.mark.parametrize('fallback_locale', ['ru', 'en'])
async def test_localization(
        taxi_grocery_api, experiments3, locale, fallback_locale, taxi_config,
):
    """ values in l10n key should be localized """

    taxi_config.set(
        GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={
            '__default__': fallback_locale,
        },
    )

    location = DEFAULT_LOCATION

    headers = copy.deepcopy(tests_headers.HEADERS)
    if locale:
        headers['X-Request-Language'] = locale

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=headers,
        json={'position': {'lon': location[0], 'lat': location[1]}},
    )
    assert response.status_code == 200
    if not locale:
        locale = fallback_locale

    expected_result = [
        {
            'cache_status': 'no_cache',
            'name': 'some-config-with-l10n',
            'value': {
                'l10n': {
                    'key-not-found': 'Should return default',
                    'simple-key': LOCALIZED_VALUE[locale],
                },
            },
        },
    ]

    ordered_object.assert_eq(
        response.json()['typed_experiments']['items'], expected_result, [''],
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='some-config-with-cache',
    consumers=['grocery-api/regional-experiments'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'yandex_uid',
                    'arg_type': 'string',
                    'value': 'regional-experiments-uid',
                },
                'type': 'eq',
            },
            'title': 'clause 1',
            'value': {'enabled': False},
        },
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    trait_tags=['cache-on-clients'],
    default_value=True,
)
async def test_client_cache(taxi_grocery_api, experiments3):
    """ experiments client cache works properly """

    location = DEFAULT_LOCATION

    headers = copy.deepcopy(tests_headers.HEADERS)
    headers['X-Request-Language'] = 'ru'

    # First request
    request_body = {'position': {'lon': location[0], 'lat': location[1]}}

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200
    response_items = response.json()['typed_experiments']['items']
    assert len(response_items) == 1
    assert response_items[0]['cache_status'] == 'updated'
    assert response_items[0]['name'] == 'some-config-with-cache'
    assert response_items[0]['value'] == {'enabled': True}
    assert 'version' in response_items[0]

    # Let's send experiment and version in order
    # to mock in-app client cache
    request_body['typed_experiments'] = {
        'items': [
            {
                'name': response_items[0]['name'],
                'version': response_items[0]['version'],
            },
        ],
    }

    # Request with known experiments
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200
    response_items = response.json()['typed_experiments']['items']
    assert len(response_items) == 1
    assert response_items[0]['cache_status'] == 'not_modified'
    assert response_items[0]['name'] == 'some-config-with-cache'
    assert 'value' not in response_items[0]
    assert 'version' not in response_items[0]

    # Request with known experiments, but different locale
    headers = copy.deepcopy(tests_headers.HEADERS)
    headers['X-Request-Language'] = 'en'

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200
    response_items = response.json()['typed_experiments']['items']
    assert len(response_items) == 1
    assert response_items[0]['cache_status'] == 'updated'
    assert response_items[0]['name'] == 'some-config-with-cache'
    assert response_items[0]['value'] == {'enabled': True}
    assert 'version' in response_items[0]

    # Request with known experiments, but different clause matched
    headers = copy.deepcopy(tests_headers.HEADERS)
    headers['X-Request-Language'] = 'ru'
    headers['X-Yandex-UID'] = 'regional-experiments-uid'

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/v1/regional-experiments',
        headers=headers,
        json=request_body,
    )
    assert response.status_code == 200
    response_items = response.json()['typed_experiments']['items']
    assert len(response_items) == 1
    assert response_items[0]['cache_status'] == 'updated'
    assert response_items[0]['name'] == 'some-config-with-cache'
    assert response_items[0]['value'] == {'enabled': False}
    assert 'version' in response_items[0]
