import pytest

from testsuite.utils import ordered_object

from tests_fleet_parks import utils


ENDPOINT = 'v1/parks/list-by-clids'


TEST_OK_PARAMS = [
    (
        {'query': {'park': {'clids': ['clid1']}}},
        {
            'parks': [
                {
                    'id': 'park_valid1',
                    'login': 'login1',
                    'tz_offset': 3,
                    'name': 'name1',
                    'is_active': True,
                    'city_id': 'city1',
                    'locale': 'locale1',
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
            ],
        },
    ),
    (
        {'query': {'park': {'clids': ['clid4']}}},
        {
            'parks': [
                {
                    'city_id': 'city4',
                    'country_id': 'cid4',
                    'driver_partner_source': 'self_assign',
                    'fleet_type': 'uberdriver',
                    'id': 'park_valid4',
                    'integration_drivers_url': (
                        'http://park_valid4/sync/drivers.php'
                    ),
                    'integration_events': ['carstatus', 'orderstatus'],
                    'integration_server_url': 'http://park_valid4/sync',
                    'is_active': True,
                    'is_billing_enabled': False,
                    'is_franchising_enabled': True,
                    'is_workshift_enabled': False,
                    'demo_mode': False,
                    'has_pay_systems_integration': False,
                    'locale': 'locale4',
                    'login': 'login4',
                    'name': 'name4',
                    'org_name': 'org_name4',
                    'owner': 'owner4',
                    'provider_config': {
                        'apikey': 'apikey4',
                        'clid': 'clid4',
                        'type': 'production',
                    },
                    'providers': ['formula', 'yandex', 'park'],
                    'ui_mode': 'small_park',
                    'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
                },
                {
                    'city_id': 'city5',
                    'country_id': '',
                    'description': 'park5 description',
                    'id': 'park_valid5',
                    'is_active': False,
                    'driver_hiring': {},
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'is_workshift_enabled': False,
                    'demo_mode': False,
                    'has_pay_systems_integration': False,
                    'locale': 'locale5',
                    'login': 'login5',
                    'name': 'name5',
                    'provider_config': {
                        'clid': 'clid4',
                        'type': 'aggregation',
                    },
                    'geodata': {'lat': 0.0, 'lon': 0.0, 'zoom': 0},
                },
            ],
        },
    ),
    ({'query': {'park': {'clids': ['park_unknown']}}}, {'parks': []}),
]


@pytest.mark.parametrize('payload, expected_response', TEST_OK_PARAMS)
async def test_ok(taxi_fleet_parks, payload, expected_response):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.post(
        ENDPOINT, json=payload, headers=headers,
    )
    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), expected_response, ['parks.providers'],
    )


TEST_INVALID_PARAMS = [
    ({'query': {'park': {}}},),
    ({'query': {'park': {'clids': []}}},),
]


@pytest.mark.parametrize('payload', TEST_INVALID_PARAMS)
async def test_invalid_request(taxi_fleet_parks, payload):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}
    response = await taxi_fleet_parks.post(
        ENDPOINT, json=payload, headers=headers,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'
