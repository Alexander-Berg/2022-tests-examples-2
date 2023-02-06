import pytest

from testsuite.utils import ordered_object

from tests_fleet_parks import utils

ENDPOINT = 'v1/parks'

TEST_PARAMS = [
    (
        'park_valid1',
        200,
        {
            'id': 'park_valid1',
            'login': 'login1',
            'name': 'name1',
            'is_active': True,
            'city_id': 'city1',
            'locale': 'locale1',
            'tz_offset': 3,
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'is_workshift_enabled': True,
            'demo_mode': False,
            'has_pay_systems_integration': True,
            'country_id': 'cid1234',
            'description': 'top park, wow',
            'provider_config': {'clid': 'clid1', 'type': 'none'},
            'driver_hiring': {
                'park_phone': '88005553535',
                'park_address': 'some nice street',
                'park_email': 'nice_email@yandex.ru',
                'commercial_hiring_commission_max': '20.02',
                'commercial_hiring_commission_min': '4.0',
                'commercial_hiring_workshift_commission_max': '15.00',
                'commercial_hiring_workshift_commission_min': '10',
            },
            'geodata': {'lat': 10.0, 'lon': 20.0, 'zoom': 10},
        },
        'max-age=180',
    ),
    (
        'park_valid2',
        200,
        {
            'id': 'park_valid2',
            'login': 'login2',
            'name': 'name2',
            'city_id': 'city2',
            'is_active': True,
            'locale': 'locale2',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'is_workshift_enabled': False,
            'demo_mode': True,
            'has_pay_systems_integration': False,
            'country_id': '',
            'specifications': ['spec1', 'spec2'],
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
        },
        'max-age=180',
    ),
    ('park_valid3', 404, {}, None),
    ('park_unknown', 404, {}, None),
]


@pytest.mark.parametrize(
    'park_id, expected_code, expected_response, expected_cache_header',
    TEST_PARAMS,
)
async def test_required_field(
        taxi_fleet_parks,
        park_id,
        expected_code,
        expected_response,
        expected_cache_header,
):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.get(
        ENDPOINT, params={'park_id': park_id}, headers=headers,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_response
    assert response.headers.get('Cache-Control') == expected_cache_header


TEST_OPTIONAL_PARAMS = [
    (
        'park_valid4',
        {
            'id': 'park_valid4',
            'login': 'login4',
            'name': 'name4',
            'is_active': True,
            'city_id': 'city4',
            'locale': 'locale4',
            'is_billing_enabled': False,
            'is_franchising_enabled': True,
            'is_workshift_enabled': False,
            'demo_mode': False,
            'has_pay_systems_integration': False,
            'country_id': 'cid4',
            'org_name': 'org_name4',
            'owner': 'owner4',
            'providers': ['formula', 'yandex', 'park'],
            'provider_config': {
                'clid': 'clid4',
                'apikey': 'apikey4',
                'type': 'production',
            },
            'ui_mode': 'small_park',
            'driver_partner_source': 'self_assign',
            'fleet_type': 'uberdriver',
            'integration_drivers_url': 'http://park_valid4/sync/drivers.php',
            'integration_server_url': 'http://park_valid4/sync',
            'integration_events': ['carstatus', 'orderstatus'],
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
        },
    ),
]


@pytest.mark.parametrize('park_id, expected_response', TEST_OPTIONAL_PARAMS)
async def test_optional_field(taxi_fleet_parks, park_id, expected_response):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.get(
        ENDPOINT, params={'park_id': park_id}, headers=headers,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_response, ['providers'])
    assert response.headers['Cache-Control'] == 'max-age=180'


TEST_PROVIDER_CONFIG_PARAMS = [
    (
        'park_valid5',
        {
            'id': 'park_valid5',
            'login': 'login5',
            'name': 'name5',
            'is_active': False,
            'driver_hiring': {},
            'city_id': 'city5',
            'provider_config': {
                'clid': 'clid4',
                'type': 'aggregation',
                'aggregator_id': 'aggregator_id',
            },
            'description': 'park5 description',
            'locale': 'locale5',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'is_workshift_enabled': False,
            'demo_mode': False,
            'has_pay_systems_integration': False,
            'country_id': '',
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
        },
    ),
    (
        'park_valid6',
        {
            'id': 'park_valid6',
            'login': 'login6',
            'name': 'name6',
            'is_active': True,
            'city_id': 'city6',
            'provider_config': {
                'clid': 'clid6',
                'type': 'production',
                'aggregator_id': 'version6',
            },
            'description': 'park6 description',
            'locale': 'locale6',
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'is_workshift_enabled': False,
            'demo_mode': False,
            'has_pay_systems_integration': False,
            'country_id': '',
            'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
        },
    ),
]


@pytest.mark.config(TAXIMETER_PRODUCTION_PROVIDER_PARKS=['park_valid6'])
@pytest.mark.parametrize(
    'park_id, expected_response', TEST_PROVIDER_CONFIG_PARAMS,
)
async def test_provider_config(taxi_fleet_parks, park_id, expected_response):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.get(
        ENDPOINT, params={'park_id': park_id}, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
    assert response.headers['Cache-Control'] == 'max-age=180'
