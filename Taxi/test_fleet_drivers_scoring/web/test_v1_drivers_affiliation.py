import pytest

from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils


ENDPOINT = '/fleet/fleet-drivers-scoring/v1/drivers/affiliations'

DEBT_BOUNDS_CONFIG1 = {
    'FLEET_DRIVERS_SCORING_DEBT_BOUNDS': {
        '__default__': {'__default__': []},
        'rus': {'__default__': [-3000]},
    },
}

JUST_ONE_DRIVER = {
    'revision': '0_1234567_4',
    'park_driver_profile_id': 'park1_driver1',
    'data': {'park_id': 'park1', 'uuid': 'driver1'},
}

DRIVER_PROFILE1 = {
    'driver_license': 'extra_super_driver_license1_pd',
    'profiles': [JUST_ONE_DRIVER],
}

JUST_SECOND_DRIVER = {
    'revision': '0_1234567_5',
    'park_driver_profile_id': 'park2_driver2',
    'data': {'park_id': 'park2', 'uuid': 'driver2'},
}

DRIVER_PROFILE1_2 = {
    'driver_license': 'extra_super_driver_license1_pd',
    'profiles': [JUST_ONE_DRIVER, JUST_SECOND_DRIVER],
}

RESPONSE_PERSONAL_PHONES1 = [
    {'id': 'extra_super_phone_pd1', 'value': '+79876'},
    {'id': 'extra_super_phone_pd2', 'value': '+70001234567'},
]

RESPONSE_TERRITORIES1 = {
    '_id': 'rus',
    'currency': 'RUB',
    'currency_rules': {'fraction': 0},
}

HEADERS = {
    'Accept-Language': '',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
}


@pytest.fixture
def _mock_phones_find(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _personal_phone_find(request):
        return {'id': '123', 'value': request.json['value']}


@pytest.mark.config(**DEBT_BOUNDS_CONFIG1)
@pytest.mark.now(defaults.NOW1.isoformat())
@pytest.mark.parametrize(
    'affiliation_state, debts_response, expected_response',
    [
        pytest.param(
            None,
            None,
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'affiliated_profile': {'is_affiliated': False},
                            'park': {
                                'name': 'super_park1',
                                'is_individual': False,
                            },
                        },
                    ],
                },
            },
            id='no affiliation',
        ),
        pytest.param(
            'active',
            {'debt_lower_bound': {'amount': '100', 'currency': 'RUB'}},
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'affiliated_profile': {
                                'is_affiliated': True,
                                'balance': {
                                    'bounds': {'from': '-3000'},
                                    'has_debt': True,
                                },
                            },
                            'park': {
                                'name': 'super_park1',
                                'is_individual': False,
                            },
                        },
                    ],
                },
            },
            id='active affiliation with debt',
        ),
        pytest.param(
            'park_recalled',
            {'debt_lower_bound': {'amount': '0', 'currency': 'RUB'}},
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'affiliated_profile': {
                                'is_affiliated': False,
                                'balance': {'has_debt': False},
                            },
                            'park': {
                                'name': 'super_park1',
                                'is_individual': False,
                            },
                        },
                    ],
                },
            },
            id='inactive affiliation without debt',
        ),
        pytest.param(
            'park_recalled',
            {},
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'affiliated_profile': {'is_affiliated': False},
                            'park': {
                                'name': 'super_park1',
                                'is_individual': False,
                            },
                        },
                    ],
                },
            },
            id='inactive no debt provided',
        ),
    ],
)
async def test_ok_profile(
        patch,
        pgsql,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_personal,
        _mock_territories,
        _mock_fleet_rent,
        _mock_phones_find,
        affiliation_state,
        debts_response,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)

    if affiliation_state:
        affiliation = {
            'record_id': 'record_id1',
            'park_id': 'park_id',
            'local_driver_id': 'local_driver_id1',
            'original_driver_park_id': 'original_driver_park_id1',
            'original_driver_id': 'original_driver_id1',
            'creator_uid': 'creator_uid',
            'created_at': '2020-01-01T03:00:00+03:00',
            'modified_at': '2020-01-01T03:00:00+03:00',
            'state': 'active',
        }
        affiliation['state'] = affiliation_state

        _mock_fleet_rent.set_affiliation({'records': [affiliation]})
        _mock_fleet_rent.set_debt(debts_response)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**HEADERS, **utils.TVM_HEADERS, 'X-Park-Id': 'park1'},
        json={'license_number': 'license'},
    )

    response_json = await response.json()
    assert response_json == expected_response


async def test_another_country(
        patch,
        pgsql,
        mockserver,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_personal,
        _mock_territories,
        _mock_phones_find,
):
    _mock_fleet_parks.set_parks_list_responses(
        [
            {
                'parks': [
                    defaults.RESPONSE_FLEET_PARKS1,
                    defaults.RESPONSE_FLEET_PARKS2_AUS_COUNTRY,
                ],
            },
        ]
        * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**HEADERS, **utils.TVM_HEADERS, 'X-Park-Id': 'park2'},
        json={'license_number': 'license'},
    )

    response_json = await response.json()
    assert response_json == {'found_driver_info': {'driver_profiles': []}}


async def test_driver_not_found(
        patch,
        pgsql,
        mockserver,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_phones_find,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _personal_phone_find(request):
        return mockserver.make_response(status=404, json={})

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**HEADERS, **utils.TVM_HEADERS, 'X-Park-Id': 'park1'},
        json={'license_number': 'license'},
    )

    response_json = await response.json()
    assert response_json == {}
