# pylint: disable=too-many-lines
import datetime
import json

import pytest
from submodules.testsuite.testsuite.utils import ordered_object

from taxi.util import dates

from test_fleet_drivers_scoring import utils as global_utils
from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils


ENDPOINT = 'v1/drivers/scoring/retrieve'

DEBT_BOUNDS_CONFIG1 = {
    'FLEET_DRIVERS_SCORING_DEBT_BOUNDS': {
        '__default__': {'__default__': []},
        'rus': {'__default__': [-3000]},
    },
}
DEBT_BOUNDS_CONFIG2 = {
    'FLEET_DRIVERS_SCORING_DEBT_BOUNDS': {
        '__default__': {'__default__': []},
        'rus': {'__default__': [-6000, -3000]},
    },
}

LOCALIZED_NOW1 = dates.localize(defaults.NOW1)
LOCALIZED_NOW2 = dates.localize(defaults.NOW2)

HIRE_DATE1 = datetime.datetime.fromisoformat('1970-01-15T06:56:07.000')
FIRE_DATE1 = datetime.datetime.fromisoformat('1980-01-15T06:56:07.000')
HIRE_DATE3 = datetime.datetime.fromisoformat('2020-02-02T02:02:02.000')

JUST_ONE_DRIVER = {
    'revision': '0_1234567_4',
    'park_driver_profile_id': 'park1_driver1',
    'data': {
        'park_id': 'park1',
        'uuid': 'driver1',
        'license': {'pd_id': 'extra_super_driver_license1_pd'},
        'full_name': {
            'first_name': 'Лол',
            'middle_name': 'Лолович',
            'last_name': 'Лолов',
        },
        'rule_id': 'some_rule_id',
        'hiring_details': {
            'hiring_type': 'commercial',
            'hiring_date': '1970-01-15T06:56:07.000',
        },
        'hire_date': HIRE_DATE1.isoformat(),
        'fire_date': FIRE_DATE1.isoformat(),
        'check_message': 'next_door',
        'phone_pd_ids': [
            {'pd_id': 'extra_super_phone_pd1'},
            {'pd_id': 'extra_super_phone_pd2'},
        ],
        'email_pd_ids': [],
    },
}

DRIVER_PROFILE1 = {
    'driver_license': 'extra_super_driver_license1_pd',
    'profiles': [JUST_ONE_DRIVER],
}

JUST_SECOND_DRIVER = {
    'revision': '0_1234567_5',
    'park_driver_profile_id': 'park2_driver2',
    'data': {
        'park_id': 'park2',
        'uuid': 'driver2',
        'license': {
            'pd_id': 'extra_super_driver_license1_pd',
            'country': 'rus',
        },
        'license_driver_birth_date': '1960-06-06T06:06:06.006',
        'full_name': {
            'first_name': 'Лол',
            'middle_name': 'Лолович',
            'last_name': 'Лолов',
        },
        'rule_id': 'some_rule_id',
        'hiring_details': {
            'hiring_type': 'commercial',
            'hiring_date': '1970-01-15T06:56:07.000',
        },
        'phone_pd_ids': [
            {'pd_id': 'extra_super_phone_pd3'},
            {'pd_id': 'extra_super_phone_pd4'},
        ],
        'email_pd_ids': [],
    },
}

DRIVER_PROFILE1_2 = {
    'driver_license': 'extra_super_driver_license1_pd',
    'profiles': [JUST_ONE_DRIVER, JUST_SECOND_DRIVER],
}

JUST_THIRD_DRIVER = {
    'revision': '0_1234567_5',
    'park_driver_profile_id': 'park3_driver3',
    'data': {
        'park_id': 'park3',
        'uuid': 'driver3',
        'license': {'pd_id': 'extra_super_driver_license1_pd'},
        'full_name': {
            'first_name': 'Лол',
            'middle_name': 'Лолович',
            'last_name': 'Лолов',
        },
        'rule_id': 'some_rule_id',
        'hiring_details': {
            'hiring_type': 'commercial',
            'hiring_date': HIRE_DATE3.isoformat(),
        },
        'hire_date': HIRE_DATE3.isoformat(),
        'fire_date': FIRE_DATE1.isoformat(),
        'work_status': 'working',
        'phone_pd_ids': [{'pd_id': 'extra_super_phone_pd1'}],
        'email_pd_ids': [],
    },
}

DRIVER_PROFILE1_3 = {
    'driver_license': 'extra_super_driver_license1_pd',
    'profiles': [JUST_ONE_DRIVER, JUST_SECOND_DRIVER, JUST_THIRD_DRIVER],
}

VEHICLE_BINDING1 = {
    'park_driver_profile_id': 'park1_driver1',
    'data': {'car_id': 'vehicle1'},
}
VEHICLE_BINDING2 = {
    'park_driver_profile_id': 'park2_driver2',
    'data': {'car_id': 'vehicle2'},
}

VEHICLE1 = {
    'park_id_car_id': 'park1_vehicle1',
    'data': {
        'number': 'A123AA777',
        'color': 'super_color',
        'model': 'Camry',
        'brand': 'Toyota',
        'year': '2020',
    },
}
VEHICLE2 = {
    'park_id_car_id': 'park2_vehicle2',
    'data': {
        'number': 'B77',
        'color': 'great_color',
        'model': 'Corolla',
        'brand': 'Toyota',
        'year': '2020',
    },
}

RESPONSE_PARK_DRIVER_PROFILE1 = {
    'hire_date': dates.localize(HIRE_DATE1).isoformat(),
    'fire_date': dates.localize(FIRE_DATE1).isoformat(),
    'check_message': 'next_door',
}
RESPONSE_PARK_DRIVER_PROFILE3 = {
    'hire_date': dates.localize(HIRE_DATE3).isoformat(),
}

RESPONSE_LIST_BALANCE1 = {
    'driver_profile_id': 'driver1',
    'balances': [
        {
            'accrued_at': '2020-03-03T18:00:00+00:00',
            'total_balance': '-5123.12',
        },
    ],
}
RESPONSE_LIST_BALANCE2 = {
    'driver_profile_id': 'driver2',
    'balances': [
        {
            'accrued_at': '2020-03-03T18:00:00+00:00',
            'total_balance': '-3000.123',
        },
    ],
}
RESPONSE_LIST_BALANCE3 = {
    'driver_profile_id': 'driver3',
    'balances': [
        {'accrued_at': '2020-05-05T05:00:00+00:00', 'total_balance': '2222.2'},
    ],
}
RESPONSE_LIST_BALANCE1_2 = {
    'driver_profile_id': 'driver1',
    'balances': [
        {'accrued_at': '2020-03-03T18:00:00+00:00', 'total_balance': '-0.001'},
    ],
}

RESPONSE_PERSONAL_PHONES1 = [
    {'id': 'extra_super_phone_pd1', 'value': '+79876'},
    {'id': 'extra_super_phone_pd2', 'value': '+70001234567'},
]
RESPONSE_PERSONAL_PHONES2 = [
    {'id': 'extra_super_phone_pd3', 'value': '+70001333333'},
    {'id': 'extra_super_phone_pd4', 'value': '+77'},
]

RESPONSE_TERRITORIES1 = {
    '_id': 'rus',
    'currency': 'RUB',
    'currency_rules': {'fraction': 0},
}

RESPONSE_PARK_NAME1 = {'name': 'super_park1', 'is_individual': False}
RESPONSE_PARK_NAME2 = {'name': 'super_park2', 'is_individual': False}
RESPONSE_PARK_NAME3 = {'name': 'super_park3', 'is_individual': False}

RESPONSE_VEHICLE1 = {
    'plate_number': 'A***AA777',
    'brand': 'Toyota',
    'model': 'Camry',
    'year': '2020',
    'color': 'super_color',
}
RESPONSE_VEHICLE2 = {
    'plate_number': '**********',
    'brand': 'Toyota',
    'model': 'Corolla',
    'year': '2020',
    'color': 'great_color',
}

RESPONSE_PERSONAL_DATA1 = {
    'first_name': 'Лол',
    'last_name': 'Л.',
    'phones': ['**********', '+7*******567'],
}
RESPONSE_PERSONAL_DATA2 = {
    'first_name': 'Лол',
    'last_name': 'Л.',
    'phones': ['+7*******333', '**********'],
}
RESPONSE_PERSONAL_DATA3 = {
    'first_name': 'Лол',
    'last_name': 'Л.',
    'phones': ['**********'],
}

AFFILIATED_PROFILE = {'is_affiliated': False}

RESPONSE_EXAMS1 = {'dkk': {'is_blocked': False}}

RESPONSE_BALANCE1 = {'has_debt': True, 'bounds': {'to': '-3000'}}
RESPONSE_BALANCE2 = {'has_debt': True, 'bounds': {'from': '-3000'}}
RESPONSE_BALANCE3 = {'has_debt': False}
RESPONSE_BALANCE4 = {'has_debt': True}
RESPONSE_BALANCE5 = {
    'has_debt': True,
    'bounds': {'from': '-6000', 'to': '-3000'},
}

UNIQUE_DRIVERS_RESPONSE_OK = {
    'uniques': [
        {
            'park_driver_profile_id': 'park1_driver1',
            'data': {'unique_driver_id': 'udid1'},
        },
    ],
}

RESPONSE_DRIVER_RATING = {'unique_driver_id': 'udid1', 'rating': '4.321'}

RESPONSE_DRIVER_PHOTOS = {
    'status': 404,
    'response': {'code': '404', 'message': 'no driver photo'},
}
RESPONSE_DRIVER_PHOTOS_OK = {'photos': [{'type': 'avatar', 'url': 'some_url'}]}

RESPONSE_INTERNAL_SERVER_ERROR = {
    'code': '500',
    'message': 'Internal Server Error',
}


RESPONSE_DRIVER_ORDERS1 = {
    'orders': [
        {
            'id': 'extra_super_order_id1',
            'short_id': 1,
            'status': 'complete',
            'created_at': '2010-10-10T10:10:10+03:00',
            'booked_at': '2010-10-10T10:10:10+03:00',
            'provider': 'platform',
            'amenities': [],
            'address_from': {'address': 'address', 'lat': 1.23, 'lon': 4.56},
            'route_points': [],
            'events': [],
        },
    ],
    'limit': 1,
}
RESPONSE_DRIVER_ORDERS2 = {
    'orders': [
        {
            'id': 'extra_super_order_id2',
            'short_id': 2,
            'status': 'complete',
            'created_at': '2010-10-11T11:11:11+03:00',
            'booked_at': '2010-10-11T11:11:11+03:00',
            'provider': 'platform',
            'amenities': [],
            'address_from': {'address': 'address', 'lat': 1.23, 'lon': 4.56},
            'route_points': [],
            'events': [],
        },
    ],
    'limit': 1,
}
RESPONSE_DRIVER_ORDERS3 = {'orders': [], 'limit': 1}


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW1.isoformat())
async def test_ok_profile(
        patch,
        pgsql,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [VEHICLE1]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}, ('park2', 'driver2'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    assert not global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='day', rate_type='free',
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    day_rates = global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='day', rate_type='free',
    )
    assert len(day_rates) == 1
    assert day_rates[0]['rate_limit'] == 10

    week_rates = global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='week', rate_type='free',
    )
    assert len(week_rates) == 1
    assert week_rates[0]['rate_limit'] is None

    assert response.status == 200, response.text

    assert _mock_driver_profiles.retrieve_by_license.times_called == 1
    retrieve_by_license_request = (
        _mock_driver_profiles.retrieve_by_license.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(retrieve_by_license_request) == {
        'driver_license_in_set': ['extra_super_driver_license1_pd'],
    }

    assert _mock_driver_profiles.vehicle_bindings.times_called == 1
    vehicle_bindings_request = (
        _mock_driver_profiles.vehicle_bindings.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(vehicle_bindings_request) == {
        'id_in_set': ['park1_driver1'],
    }

    assert _mock_fleet_vehicles.vehicles_retrieve.times_called == 1
    fleet_vehicles_request = (
        _mock_fleet_vehicles.vehicles_retrieve.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(fleet_vehicles_request) == {
        'id_in_set': ['park1_vehicle1'],
    }

    assert _mock_fleet_parks.parks_list.times_called == 2
    fleet_parks_request = _mock_fleet_parks.parks_list.next_call()[
        'request'
    ].get_data()
    assert json.loads(fleet_parks_request) == {
        'query': {'park': {'ids': ['park1']}},
    }

    assert _mock_taximeter_xservice.exams_retrieve.times_called == 1
    exams_retrieve = _mock_taximeter_xservice.exams_retrieve.next_call()[
        'request'
    ].get_data()
    assert json.loads(exams_retrieve) == {
        'locale': 'ru',
        'query': {
            'park': {'driver_profile': {'id': 'driver1'}, 'id': 'park1'},
        },
    }

    assert _mock_personal.bulk_retrieve.times_called == 1
    phones = _mock_personal.bulk_retrieve.next_call()['request'].get_data()
    ordered_object.assert_eq(
        json.loads(phones),
        {
            'items': [
                {'id': 'extra_super_phone_pd1'},
                {'id': 'extra_super_phone_pd2'},
            ],
        },
        paths=['items'],
    )

    assert _mock_territories.countries_retrieve.times_called == 1
    country = _mock_territories.countries_retrieve.next_call()[
        'request'
    ].get_data()
    assert json.loads(country) == {'_id': 'rus'}

    assert _mock_fleet_transactions_api.balances_list.times_called == 1
    balance = _mock_fleet_transactions_api.balances_list.next_call()[
        'request'
    ].get_data()
    ordered_object.assert_eq(
        json.loads(balance),
        {
            'query': {
                'park': {
                    'id': 'park1',
                    'driver_profile': {'ids': ['driver1']},
                },
                'balance': {'accrued_ats': [LOCALIZED_NOW1.isoformat()]},
            },
        },
        paths=[''],
    )
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    assert _mock_driver_ratings.driver_ratings.times_called == 1

    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE1,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'vehicle': RESPONSE_VEHICLE1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW1.isoformat())
async def test_ok_multiply_profiles(
        taxi_fleet_drivers_scoring_web,
        pgsql,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [
            {
                'parks': [
                    defaults.RESPONSE_FLEET_PARKS1,
                    defaults.RESPONSE_FLEET_PARKS2,
                    defaults.RESPONSE_FLEET_PARKS3,
                ],
            },
        ]
        * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1_3]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1, VEHICLE_BINDING2]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [VEHICLE1, VEHICLE2]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {
            ('park1', 'driver1'): {},
            ('park2', 'driver2'): {},
            ('park3', 'driver3'): {},
        },
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1 + RESPONSE_PERSONAL_PHONES2},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {
            ('park1', 'driver1'): {
                'driver_profiles': [RESPONSE_LIST_BALANCE1],
            },
            ('park2', 'driver2'): {
                'driver_profiles': [RESPONSE_LIST_BALANCE2],
            },
            ('park3', 'driver3'): {
                'driver_profiles': [RESPONSE_LIST_BALANCE3],
            },
        },
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text

    assert _mock_driver_profiles.retrieve_by_license.times_called == 1
    retrieve_by_license_request = (
        _mock_driver_profiles.retrieve_by_license.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(retrieve_by_license_request) == {
        'driver_license_in_set': ['extra_super_driver_license1_pd'],
    }

    assert _mock_driver_profiles.vehicle_bindings.times_called == 1
    vehicle_bindings_request = (
        _mock_driver_profiles.vehicle_bindings.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(vehicle_bindings_request) == {
        'id_in_set': ['park1_driver1', 'park2_driver2', 'park3_driver3'],
    }

    assert _mock_fleet_vehicles.vehicles_retrieve.times_called == 1
    fleet_vehicles_request = (
        _mock_fleet_vehicles.vehicles_retrieve.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(fleet_vehicles_request) == {
        'id_in_set': ['park1_vehicle1', 'park2_vehicle2'],
    }

    assert _mock_fleet_parks.parks_list.times_called == 2
    fleet_parks_requests = [
        json.loads(
            _mock_fleet_parks.parks_list.next_call()['request'].get_data(),
        )
        for _ in range(2)
    ]
    assert fleet_parks_requests == [
        {'query': {'park': {'ids': ['park1']}}},
        {'query': {'park': {'ids': ['park1', 'park2', 'park3']}}},
    ]

    assert _mock_taximeter_xservice.exams_retrieve.times_called == 3
    exams_requests = [
        json.loads(
            _mock_taximeter_xservice.exams_retrieve.next_call()[
                'request'
            ].get_data(),
        )
        for _ in range(3)
    ]
    ordered_object.assert_eq(
        exams_requests,
        [
            {
                'locale': 'ru',
                'query': {
                    'park': {
                        'driver_profile': {'id': 'driver1'},
                        'id': 'park1',
                    },
                },
            },
            {
                'locale': 'ru',
                'query': {
                    'park': {
                        'driver_profile': {'id': 'driver2'},
                        'id': 'park2',
                    },
                },
            },
            {
                'locale': 'ru',
                'query': {
                    'park': {
                        'driver_profile': {'id': 'driver3'},
                        'id': 'park3',
                    },
                },
            },
        ],
        paths=[''],
    )

    assert _mock_personal.bulk_retrieve.times_called == 1
    phones = _mock_personal.bulk_retrieve.next_call()['request'].get_data()
    ordered_object.assert_eq(
        json.loads(phones),
        {
            'items': [
                {'id': 'extra_super_phone_pd1'},
                {'id': 'extra_super_phone_pd2'},
                {'id': 'extra_super_phone_pd3'},
                {'id': 'extra_super_phone_pd4'},
            ],
        },
        paths=['items'],
    )

    assert _mock_territories.countries_retrieve.times_called == 1
    country_request = _mock_territories.countries_retrieve.next_call()[
        'request'
    ].get_data()
    assert json.loads(country_request) == {'_id': 'rus'}

    assert _mock_fleet_transactions_api.balances_list.times_called == 3
    balance_requests = [
        json.loads(
            _mock_fleet_transactions_api.balances_list.next_call()[
                'request'
            ].get_data(),
        )
        for _ in range(3)
    ]
    ordered_object.assert_eq(
        balance_requests,
        [
            {
                'query': {
                    'park': {
                        'id': 'park1',
                        'driver_profile': {'ids': ['driver1']},
                    },
                    'balance': {'accrued_ats': [LOCALIZED_NOW1.isoformat()]},
                },
            },
            {
                'query': {
                    'park': {
                        'id': 'park2',
                        'driver_profile': {'ids': ['driver2']},
                    },
                    'balance': {'accrued_ats': [LOCALIZED_NOW1.isoformat()]},
                },
            },
            {
                'query': {
                    'park': {
                        'id': 'park3',
                        'driver_profile': {'ids': ['driver3']},
                    },
                    'balance': {'accrued_ats': [LOCALIZED_NOW1.isoformat()]},
                },
            },
        ],
        paths=[''],
    )
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    assert _mock_driver_ratings.driver_ratings.times_called == 1

    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME3,
                    'balance': RESPONSE_BALANCE3,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE3,
                    'personal_data': RESPONSE_PERSONAL_DATA3,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE1,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'vehicle': RESPONSE_VEHICLE1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
                {
                    'park': RESPONSE_PARK_NAME2,
                    'balance': RESPONSE_BALANCE2,
                    'personal_data': RESPONSE_PERSONAL_DATA2,
                    'vehicle': RESPONSE_VEHICLE2,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **defaults.RATE_LIMIT_CONFIG1, **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_no_driver(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {
            'profiles_by_license': [
                {
                    'driver_license': 'extra_super_driver_license1_pd',
                    'profiles': [],
                },
            ],
        },
    )
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    assert _mock_driver_profiles.retrieve_by_license.times_called == 1
    assert _mock_driver_profiles.vehicle_bindings.times_called == 0
    assert _mock_fleet_vehicles.vehicles_retrieve.times_called == 0
    assert _mock_fleet_parks.parks_list.times_called == 1
    assert _mock_taximeter_xservice.exams_retrieve.times_called == 0
    assert _mock_personal.bulk_retrieve.times_called == 0
    assert _mock_fleet_transactions_api.balances_list.times_called == 0
    assert _mock_territories.countries_retrieve.times_called == 0
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 0
    assert _mock_driver_ratings.driver_ratings.times_called == 0
    assert _mock_driver_photos.get_photos.times_called == 0

    response_json = await response.json()
    assert response_json == {}


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_no_car_binding(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {
            'profiles': [
                {'park_driver_profile_id': 'park1_driver1', 'data': {}},
            ],
        },
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    assert _mock_fleet_vehicles.vehicles_retrieve.times_called == 0
    assert _mock_personal.bulk_retrieve.times_called == 1
    assert _mock_fleet_transactions_api.balances_list.times_called == 1
    assert _mock_territories.countries_retrieve.times_called == 1
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    assert _mock_driver_ratings.driver_ratings.times_called == 1

    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE1,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_no_vehicle_info(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text

    assert _mock_fleet_vehicles.vehicles_retrieve.times_called == 1
    assert _mock_personal.bulk_retrieve.times_called == 1
    assert _mock_fleet_transactions_api.balances_list.times_called == 1
    assert _mock_territories.countries_retrieve.times_called == 1
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    assert _mock_driver_ratings.driver_ratings.times_called == 1

    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE1,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.parametrize(
    'exams_response, exams',
    [
        (
            {
                'dkk_exam': {
                    'summary': {
                        'deadline_date': '2020-02-02T10:02:28.953Z',
                        'is_blocked': False,
                        'reason': 'string',
                    },
                },
            },
            {'dkk': {'is_blocked': False}},
        ),
        (
            {
                'dkk_exam': {
                    'summary': {
                        'deadline_date': '2020-02-02T10:02:28.953Z',
                        'is_blocked': True,
                        'reason': 'string',
                    },
                },
            },
            {'dkk': {'is_blocked': True}},
        ),
        ({'dkk_exam': {}}, {'dkk': {'is_blocked': False}}),
        ({}, {'dkk': {'is_blocked': False}}),
    ],
)
async def test_exams(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        exams_response,
        exams,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): exams_response},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE1,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': exams,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_driver_no_debt(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {
            ('park1', 'driver1'): {
                'driver_profiles': [RESPONSE_LIST_BALANCE1_2],
            },
        },
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_transactions_api.balances_list.times_called == 1
    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE3,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **defaults.RATE_LIMIT_CONFIG1, **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_driver_no_debt_bounds_config(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_transactions_api.balances_list.times_called == 1
    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE4,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG2,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_driver_two_debt_bounds(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_transactions_api.balances_list.times_called == 1
    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE5,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG2,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW2.isoformat())
async def test_rates_below_limit(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_parks.parks_list.times_called == 2
    assert response.status == 200, response.text

    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE5,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG2,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW2.isoformat())
async def test_day_rate_limit_reached(
        taxi_fleet_drivers_scoring_web, _mock_fleet_parks,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS3]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park3'},
    )
    assert _mock_fleet_parks.parks_list.times_called == 1
    assert response.status == 429, response.text

    response_json = await response.json()
    assert response_json == {
        'code': '429',
        'message': 'Rate limit achieved for park park3',
    }


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG2,
    **defaults.RATE_LIMIT_CONFIG2,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.parametrize(
    'park_id, response_fleet_parks',
    [
        ('park1', defaults.RESPONSE_FLEET_PARKS1),
        ('park3', defaults.RESPONSE_FLEET_PARKS3),
    ],
)
@pytest.mark.now(defaults.NOW2.isoformat())
async def test_week_rate_limit_reached(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        park_id,
        response_fleet_parks,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [response_fleet_parks]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': park_id},
    )
    assert _mock_fleet_parks.parks_list.times_called == 1
    assert response.status == 429, response.text

    response_json = await response.json()
    assert response_json == {
        'code': '429',
        'message': f'Rate limit achieved for park {park_id}',
    }


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_freeze_rate_limit.sql'],
)
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG2,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW2.isoformat())
@pytest.mark.parametrize(
    'license_pd_id, day_amount, week_amount',
    [
        # test case: park paid for the license_pd_id1 report and
        #            there is a done report
        ('license_pd_id1', 1, 2),
        # test case: park paid for the license_pd_id2 report but
        #            there is not a done report
        ('license_pd_id2', 2, 3),
        # test case: park did not pay for the license_pd_id3 report
        ('license_pd_id3', 2, 3),
    ],
)
async def test_freeze_free_rate_limit(
        taxi_fleet_drivers_scoring_web,
        pgsql,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        license_pd_id,
        day_amount,
        week_amount,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [{'park_id_car_id': 'park1_vehicle1'}]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={'query': {'driver': {'license_pd_id': license_pd_id}}},
        params={'park_id': 'park1'},
    )
    assert response.status == 200, response.text

    rate_limit = global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='day', rate_type='free',
    )
    assert len(rate_limit) == 1
    assert rate_limit[0]['amount'] == day_amount

    rate_limit = global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='week', rate_type='free',
    )
    assert len(rate_limit) == 1
    assert rate_limit[0]['amount'] == week_amount


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
async def test_wrong_park_id(
        taxi_fleet_drivers_scoring_web, _mock_fleet_parks,
):
    _mock_fleet_parks.set_parks_list_responses([{'parks': []}])

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )
    assert _mock_fleet_parks.parks_list.times_called == 1
    assert response.status == 400, response.text

    response_json = await response.json()
    assert response_json == {
        'code': '400',
        'message': 'Park park1 was not found',
    }


@pytest.mark.config(
    **defaults.RATE_LIMIT_CONFIG1, **defaults.SCORING_ENABLED_CONFIG2,
)
@pytest.mark.parametrize(
    'park_id, response_fleet_parks',
    [
        ('park1', defaults.RESPONSE_FLEET_PARKS1),
        ('park2', defaults.RESPONSE_FLEET_PARKS2),
    ],
)
async def test_scoring_enabled(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        park_id,
        response_fleet_parks,
):
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {
            'profiles_by_license': [
                {
                    'driver_license': 'extra_super_driver_license1_pd',
                    'profiles': [],
                },
            ],
        },
    )
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [response_fleet_parks]}] * 2,
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': park_id},
    )

    assert _mock_fleet_parks.parks_list.times_called == 1

    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {}


@pytest.mark.parametrize(
    'park_id, response_fleet_parks, fleet_parks_call_number',
    [
        ('park3', defaults.RESPONSE_FLEET_PARKS3, 0),
        ('park4', defaults.RESPONSE_FLEET_PARKS4, 1),
    ],
)
@pytest.mark.config(
    **defaults.RATE_LIMIT_CONFIG1, **defaults.SCORING_ENABLED_CONFIG2,
)
async def test_scoring_disabled_for_parks(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        park_id,
        response_fleet_parks,
        fleet_parks_call_number,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [response_fleet_parks]}],
    )

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': park_id},
    )

    assert _mock_fleet_parks.parks_list.times_called == fleet_parks_call_number

    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == {
        'code': '400',
        'message': f'Scoring is disabled for park {park_id}',
    }


@pytest.mark.config(
    **defaults.RATE_LIMIT_CONFIG1, **defaults.SCORING_ENABLED_CONFIG3,
)
async def test_scoring_disabled(
        taxi_fleet_drivers_scoring_web, _mock_fleet_parks,
):
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_parks.parks_list.times_called == 0
    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == {'code': '400', 'message': 'Scoring is disabled'}


@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_scoring_filter_request_country_id(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
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
    profiles = {
        'driver_license': 'extra_super_driver_license1_pd',
        'profiles': [JUST_SECOND_DRIVER, JUST_ONE_DRIVER],
    }
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [profiles]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [VEHICLE1]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {
        'found_driver_info': {
            'driver_profiles': [
                {
                    'park': RESPONSE_PARK_NAME1,
                    'balance': RESPONSE_BALANCE1,
                    'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                    'personal_data': RESPONSE_PERSONAL_DATA1,
                    'vehicle': RESPONSE_VEHICLE1,
                    'exams': RESPONSE_EXAMS1,
                    'affiliated_profile': AFFILIATED_PROFILE,
                },
            ],
            'rating': {'current': '4.321'},
            'general_personal_data': {
                'first_name': 'Лол',
                'last_name': 'Лолов',
            },
        },
    }


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW1.isoformat())
@pytest.mark.parametrize(
    'get_photos_response, expected_photos',
    [
        (
            {
                'status': 200,
                'response': {
                    'photos': [{'type': 'avatar', 'url': 'some_url'}],
                },
            },
            {'photos': {'driver_avatar_photo_url': 'some_url'}},
        ),
        (
            {
                'status': 200,
                'response': {
                    'photos': [{'type': 'portrait', 'url': 'some_url'}],
                },
            },
            {},
        ),
        (
            {
                'status': 404,
                'response': {'code': '404', 'message': 'no photos'},
            },
            {},
        ),
    ],
)
async def test_unique_driver_info(
        patch,
        pgsql,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        get_photos_response,
        expected_photos,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [VEHICLE1]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**get_photos_response)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    retrieve_by_profiles_request = (
        _mock_unique_drivers.retrieve_by_profiles.next_call()['request'].json
    )
    assert retrieve_by_profiles_request == {
        'profile_id_in_set': ['park1_driver1'],
    }

    assert _mock_driver_photos.get_photos.times_called == 1
    get_photos_request = _mock_driver_photos.get_photos.next_call()['request']
    assert {k: v for k, v in get_photos_request.query.items()} == {
        'unique_driver_id': 'udid1',
    }

    response_json = await response.json()

    found_driver_info = {
        'driver_profiles': [
            {
                'park': RESPONSE_PARK_NAME1,
                'balance': RESPONSE_BALANCE1,
                'park_driver_profile': RESPONSE_PARK_DRIVER_PROFILE1,
                'personal_data': RESPONSE_PERSONAL_DATA1,
                'vehicle': RESPONSE_VEHICLE1,
                'exams': RESPONSE_EXAMS1,
                'affiliated_profile': AFFILIATED_PROFILE,
            },
        ],
        'rating': {'current': '4.321'},
        'general_personal_data': {'first_name': 'Лол', 'last_name': 'Лолов'},
    }
    found_driver_info.update(**expected_photos)

    assert response_json == {'found_driver_info': found_driver_info}


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW1.isoformat())
@pytest.mark.parametrize(
    'driver_work_parks, driver_last_orders, expected_response',
    [
        (
            # two no request parks:
            # park1 last driver order date < park2 last driver order date ->
            # general_personal_data from 2nd driver profile
            [
                {
                    'parks': [
                        defaults.RESPONSE_FLEET_PARKS1,
                        defaults.RESPONSE_FLEET_PARKS2,
                    ],
                },
            ],
            {
                'park1': RESPONSE_DRIVER_ORDERS1,
                'park2': RESPONSE_DRIVER_ORDERS2,
            },
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'general_personal_data': {
                        'birth_date': '1960-06-06',
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                        'license_country': 'rus',
                    },
                },
            },
        ),
        (
            # two no request parks:
            # park1 last driver order date > park2 last driver order date ->
            # general_personal_data from 1st driver profile
            [
                {
                    'parks': [
                        defaults.RESPONSE_FLEET_PARKS1,
                        defaults.RESPONSE_FLEET_PARKS2,
                    ],
                },
            ],
            {
                'park1': RESPONSE_DRIVER_ORDERS2,
                'park2': RESPONSE_DRIVER_ORDERS1,
            },
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                    },
                },
            },
        ),
        (
            # two no request parks:
            # in park1 driver has no orders ->
            # general_personal_data from 2nd driver profile
            [
                {
                    'parks': [
                        defaults.RESPONSE_FLEET_PARKS1,
                        defaults.RESPONSE_FLEET_PARKS2,
                    ],
                },
            ],
            {
                'park1': RESPONSE_DRIVER_ORDERS3,
                'park2': RESPONSE_DRIVER_ORDERS2,
            },
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                        'birth_date': '1960-06-06',
                        'license_country': 'rus',
                    },
                },
            },
        ),
        (
            # two no request parks:
            # in both parks driver has no orders
            [
                {
                    'parks': [
                        defaults.RESPONSE_FLEET_PARKS1,
                        defaults.RESPONSE_FLEET_PARKS2,
                    ],
                },
            ],
            {
                'park1': RESPONSE_DRIVER_ORDERS3,
                'park2': RESPONSE_DRIVER_ORDERS3,
            },
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                    },
                },
            },
        ),
    ],
)
async def test_driver_orders(
        patch,
        pgsql,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        _mock_driver_orders,
        driver_work_parks,
        driver_last_orders,
        expected_response,
):
    parks_list_responses = [{'parks': [defaults.RESPONSE_FLEET_PARKS3]}]
    parks_list_responses.extend(driver_work_parks)
    _mock_fleet_parks.set_parks_list_responses(parks_list_responses)
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1_2]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [VEHICLE1]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}, ('park2', 'driver2'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1 + RESPONSE_PERSONAL_PHONES2},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {
            ('park1', 'driver1'): {
                'driver_profiles': [RESPONSE_LIST_BALANCE1],
            },
            ('park2', 'driver2'): {
                'driver_profiles': [RESPONSE_LIST_BALANCE2],
            },
        },
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)
    _mock_driver_orders.set_orders_resp(driver_last_orders)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park3'},
    )

    assert _mock_driver_orders.orders.times_called == len(driver_last_orders)

    response_json = await response.json()
    assert response_json == expected_response


CLIENT_QOS_CONFIG = {'__default__': {'attempts': 1, 'timeout-ms': 5}}


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
    FLEET_TRANSACTIONS_API_CLIENT_QOS=CLIENT_QOS_CONFIG,
    XSERVICE_CLIENT_QOS=CLIENT_QOS_CONFIG,
    DRIVER_ORDERS_CLIENT_QOS=CLIENT_QOS_CONFIG,
    DRIVER_PHOTOS_CLIENT_QOS=CLIENT_QOS_CONFIG,
)
@pytest.mark.now(defaults.NOW1.isoformat())
@pytest.mark.parametrize(
    'fleet_transactions_api_responses, taximeter_xservice_responses,'
    'driver_orders_responses, driver_photos_responses, expected_response',
    [
        (
            # test case: fleet-transactions-api internal server error
            {
                ('park1', 'driver1'): RESPONSE_INTERNAL_SERVER_ERROR,
                ('park2', 'driver2'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE2],
                },
            },
            {
                ('park1', 'driver1'): RESPONSE_EXAMS1,
                ('park2', 'driver2'): RESPONSE_EXAMS1,
            },
            {
                'park1': RESPONSE_DRIVER_ORDERS1,
                'park2': RESPONSE_DRIVER_ORDERS2,
            },
            RESPONSE_DRIVER_PHOTOS_OK,
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'exams': RESPONSE_EXAMS1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'photos': {'driver_avatar_photo_url': 'some_url'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                        'birth_date': '1960-06-06',
                        'license_country': 'rus',
                    },
                },
            },
        ),
        (
            # test case: taximeter-xservice internal server error
            {
                ('park1', 'driver1'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE1],
                },
                ('park2', 'driver2'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE2],
                },
            },
            {
                ('park1', 'driver1'): RESPONSE_INTERNAL_SERVER_ERROR,
                ('park2', 'driver2'): RESPONSE_EXAMS1,
            },
            {
                'park1': RESPONSE_DRIVER_ORDERS1,
                'park2': RESPONSE_DRIVER_ORDERS2,
            },
            RESPONSE_DRIVER_PHOTOS_OK,
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'exams': RESPONSE_EXAMS1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'photos': {'driver_avatar_photo_url': 'some_url'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                        'birth_date': '1960-06-06',
                        'license_country': 'rus',
                    },
                },
            },
        ),
        (
            # test case: driver-orders internal server error
            {
                ('park1', 'driver1'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE1],
                },
                ('park2', 'driver2'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE2],
                },
            },
            {
                ('park1', 'driver1'): RESPONSE_EXAMS1,
                ('park2', 'driver2'): RESPONSE_EXAMS1,
            },
            {
                'park1': RESPONSE_DRIVER_ORDERS1,
                'park2': RESPONSE_INTERNAL_SERVER_ERROR,
            },
            RESPONSE_DRIVER_PHOTOS_OK,
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'exams': RESPONSE_EXAMS1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'photos': {'driver_avatar_photo_url': 'some_url'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                    },
                },
            },
        ),
        (
            # test case: driver-photos internal server error
            {
                ('park1', 'driver1'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE1],
                },
                ('park2', 'driver2'): {
                    'driver_profiles': [RESPONSE_LIST_BALANCE2],
                },
            },
            {
                ('park1', 'driver1'): RESPONSE_EXAMS1,
                ('park2', 'driver2'): RESPONSE_EXAMS1,
            },
            {
                'park1': RESPONSE_DRIVER_ORDERS1,
                'park2': RESPONSE_DRIVER_ORDERS2,
            },
            RESPONSE_INTERNAL_SERVER_ERROR,
            {
                'found_driver_info': {
                    'driver_profiles': [
                        {
                            'park': RESPONSE_PARK_NAME1,
                            'balance': RESPONSE_BALANCE1,
                            'park_driver_profile': (
                                RESPONSE_PARK_DRIVER_PROFILE1
                            ),
                            'exams': RESPONSE_EXAMS1,
                            'personal_data': RESPONSE_PERSONAL_DATA1,
                            'vehicle': RESPONSE_VEHICLE1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                        {
                            'park': RESPONSE_PARK_NAME2,
                            'balance': RESPONSE_BALANCE2,
                            'personal_data': RESPONSE_PERSONAL_DATA2,
                            'exams': RESPONSE_EXAMS1,
                            'affiliated_profile': AFFILIATED_PROFILE,
                        },
                    ],
                    'rating': {'current': '4.321'},
                    'general_personal_data': {
                        'first_name': 'Лол',
                        'last_name': 'Л.',
                        'birth_date': '1960-06-06',
                        'license_country': 'rus',
                    },
                },
            },
        ),
    ],
)
async def test_fallbacks(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        _mock_driver_orders,
        fleet_transactions_api_responses,
        taximeter_xservice_responses,
        driver_orders_responses,
        driver_photos_responses,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [
            {
                'parks': [
                    defaults.RESPONSE_FLEET_PARKS1,
                    defaults.RESPONSE_FLEET_PARKS2,
                    defaults.RESPONSE_FLEET_PARKS3,
                ],
            },
        ]
        * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1_2]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {'profiles': [VEHICLE_BINDING1]},
    )
    _mock_fleet_vehicles.set_vehicles_retrieve_response(
        {'vehicles': [VEHICLE1]},
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        taximeter_xservice_responses,
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1 + RESPONSE_PERSONAL_PHONES2},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        fleet_transactions_api_responses,
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(driver_photos_responses)
    _mock_driver_orders.set_orders_resp(driver_orders_responses)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park3'},
    )

    assert _mock_fleet_transactions_api.balances_list.times_called == 2
    assert _mock_taximeter_xservice.exams_retrieve.times_called == 2
    assert _mock_driver_orders.orders.times_called == 2
    assert _mock_driver_photos.get_photos.times_called == 1

    assert await response.json() == expected_response


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW1.isoformat())
@pytest.mark.parametrize(
    'affiliation_state, debts_response, expected_response',
    [
        pytest.param(
            'active',
            {'debt_lower_bound': {'amount': '100', 'currency': 'RUB'}},
            {
                'is_affiliated': True,
                'balance': {'bounds': {'from': '-3000'}, 'has_debt': True},
            },
            id='active affiliation with debt',
        ),
        pytest.param(
            'park_recalled',
            {'debt_lower_bound': {'amount': '0', 'currency': 'RUB'}},
            {'is_affiliated': False, 'balance': {'has_debt': False}},
            id='inactive affiliation without debt',
        ),
        pytest.param(
            'park_recalled',
            {},
            {'is_affiliated': False},
            id='inactive no debt provided',
        ),
    ],
)
async def test_affiliated_debt(
        patch,
        pgsql,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        _mock_driver_orders,
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
    _mock_driver_profiles.set_vehicle_bindings_response(
        {
            'profiles': [
                {'park_driver_profile_id': 'park1_driver1', 'data': {}},
            ],
        },
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

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
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text

    response_json = await response.json()
    drivers = response_json['found_driver_info']['driver_profiles']
    assert len(drivers) == 1, drivers
    assert drivers[0]['affiliated_profile'] == expected_response, drivers


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rates.sql'])
@pytest.mark.config(
    **DEBT_BOUNDS_CONFIG1,
    **defaults.RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW1.isoformat())
async def test_is_individual(
        patch,
        pgsql,
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_driver_profiles,
        _mock_fleet_vehicles,
        _mock_taximeter_xservice,
        _mock_personal,
        _mock_fleet_transactions_api,
        _mock_territories,
        _mock_unique_drivers,
        _mock_driver_ratings,
        _mock_driver_photos,
        _mock_fleet_rent,
        _mock_driver_orders,
):
    fleet_parks_response = {
        'id': 'park1',
        'login': 'login1',
        'name': 'super_park1',
        'is_active': True,
        'city_id': 'city1',
        'locale': 'locale1',
        'is_billing_enabled': False,
        'is_franchising_enabled': False,
        'demo_mode': False,
        'country_id': 'rus',
        'provider_config': {'clid': 'clid1', 'type': 'production'},
        'driver_partner_source': 'yandex',
        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    }
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [fleet_parks_response]}] * 2,
    )
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [DRIVER_PROFILE1]},
    )
    _mock_driver_profiles.set_vehicle_bindings_response(
        {
            'profiles': [
                {'park_driver_profile_id': 'park1_driver1', 'data': {}},
            ],
        },
    )
    _mock_taximeter_xservice.set_exams_retrieve_responses(
        {('park1', 'driver1'): {}},
    )
    _mock_personal.set_bulk_retrieve_response(
        {'items': RESPONSE_PERSONAL_PHONES1},
    )
    _mock_fleet_transactions_api.set_balances_list_responses(
        {('park1', 'driver1'): {'driver_profiles': [RESPONSE_LIST_BALANCE1]}},
    )
    _mock_territories.set_countries_retrieve_response(RESPONSE_TERRITORIES1)
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        UNIQUE_DRIVERS_RESPONSE_OK,
    )
    _mock_driver_ratings.set_driver_rating_response(RESPONSE_DRIVER_RATING)
    _mock_driver_photos.set_get_photos_resp(**RESPONSE_DRIVER_PHOTOS)

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers=utils.TVM_HEADERS,
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text

    response_json = await response.json()
    drivers = response_json['found_driver_info']['driver_profiles']
    assert len(drivers) == 1, drivers
    assert drivers[0]['park'] == {'is_individual': True, 'name': 'super_park1'}
