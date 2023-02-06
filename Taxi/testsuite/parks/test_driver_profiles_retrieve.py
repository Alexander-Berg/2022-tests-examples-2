# encoding=utf-8
import itertools
import json

import pytest

from taxi_tests.utils import ordered_object


ENDPOINT_URL = '/driver-profiles/retrieve'
UNIQUE_DRIVERS_URL = '/unique_drivers/v1/driver/uniques/retrieve_by_profiles'
DRIVER_RATINGS_URL = '/driver-ratings/v2/driver/rating'
DRIVER_METRICS_URL = '/driver_metrics_storage/v2/activity_values/list'
DRIVER_STATUS_URL = '/driver_categories_api_codegen/v2/driver/restrictions'
BALANCE_URL = '/fleet_transactions_api/v1/parks/driver-profiles/balances/list'


@pytest.fixture
def unique_drivers(mockserver):
    @mockserver.json_handler(UNIQUE_DRIVERS_URL)
    def unique_driver_id_mock_callback(request):
        request.get_data()
        return {
            'uniques': [
                {
                    'park_driver_profile_id': 'xxx',
                    'data': {'unique_driver_id': 'unique_id'},
                },
            ],
        }

    return unique_driver_id_mock_callback


@pytest.fixture
def driver_ratings(mockserver):
    @mockserver.json_handler(DRIVER_RATINGS_URL)
    def ratings_retrieve_mock_callback(request):
        request.get_data()
        return {'unique_driver_id': 'unique_id', 'rating': '3.5'}

    return ratings_retrieve_mock_callback


@pytest.fixture
def driver_status_handler(mockserver):
    @mockserver.json_handler(DRIVER_STATUS_URL)
    def mock_callback(request):
        request.get_data()
        return {
            'categories': [
                {'jdoc': {}, 'name': 'econom'},
                {'jdoc': {}, 'name': 'comfortplus'},
                {'jdoc': {}, 'name': 'business2'},
            ],
        }

    return mock_callback


OK_PARAMS = [
    # 1
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                },
            },
            'fields': {
                'account': [
                    'id',
                    'type',
                    'balance',
                    'balance_limit',
                    'currency',
                ],
                'car': [
                    'is_readonly',
                    'brand',
                    'model',
                    'callsign',
                    'normalized_number',
                ],
                'driver_profile': [
                    'id',
                    'is_readonly',
                    'car_id',
                    'hiring_details',
                    'park_id',
                    'first_name',
                    'last_name',
                    'created_date',
                    'modified_date',
                    'driver_license',
                    'license_country',
                    'license_driver_birth_date',
                    'license_expire_date',
                    'license_issue_date',
                    'license_normalized',
                    'professional_certificate_expiration_date',
                    'road_penalties_record_issue_date',
                    'background_criminal_record_issue_date',
                    'license_experience',
                    'sex',
                ],
                'taximeter_disable_status': ['disabled', 'disable_message'],
            },
        },
        {
            'accounts': [
                {
                    'id': 'superDriver',
                    'type': 'current',
                    'balance': '13.7200',
                    'balance_limit': '50.0000',
                    'currency': 'EUR',
                },
            ],
            'car': {
                'is_readonly': False,
                'brand': 'Mercedes-Benz',
                'model': 'AMG G63',
                'callsign': 'гелик',
                'normalized_number': 'B7770P77',
            },
            'driver_profile': {
                'id': 'superDriver',
                'car_id': 'Gelendewagen',
                'hiring_details': {'hiring_date': '2019-05-06T15:47:00+0000'},
                'professional_certificate_expiration_date': (
                    '2019-12-27T00:00:00+0000'
                ),
                'license_experience': {'total_since': '2019-12-27'},
                'sex': 'male',
                'road_penalties_record_issue_date': '2019-12-27T00:00:00+0000',
                'background_criminal_record_issue_date': (
                    '2019-12-27T00:00:00+0000'
                ),
                'park_id': '222333',
                'first_name': 'Антон',
                'last_name': 'Тодуа',
                'created_date': '2018-11-19T10:04:14.517+0000',
                'modified_date': '2018-11-02T11:04:14.517+0000',
                'driver_license': {
                    'birth_date': '1994-01-01T07:15:13+0000',
                    'normalized_number': '7211050505',
                    'number': '7211050505',
                },
                'is_readonly': True,
            },
            'taximeter_disable_status': {
                'disable_message': 'bad guy',
                'disabled': True,
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 2
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                },
            },
            'fields': {'current_status': ['status', 'status_updated_at']},
        },
        {'current_status': {'status': 'offline'}, 'driver_profile': {}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'driver_profile': {'id': 'driver2'},
                },
            },
            'fields': {
                'current_status': ['status', 'status_updated_at'],
                'taximeter_disable_status': ['disabled', 'disable_message'],
            },
        },
        {
            'current_status': {
                'status': 'busy',
                'status_updated_at': '2018-12-17T00:00:02+0000',
            },
            'driver_profile': {},
            'taximeter_disable_status': {
                'disabled': False,
                'disable_message': '',
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 3
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                    'car': {
                        'categories_filter': ['business', 'mkk', 'maybach'],
                    },
                },
            },
            'fields': {'car': ['category']},
        },
        {'car': {'category': ['business', 'mkk']}, 'driver_profile': {}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 4
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                    'car': {'categories_filter': ['business', 'maybach']},
                },
            },
            'fields': {'car': ['category']},
        },
        {'car': {'category': ['business']}, 'driver_profile': {}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 5, test fields for car rent
    (
        {
            'query': {
                'park': {
                    'id': 'status_park',
                    'driver_profile': {'id': 'driver2'},
                },
            },
            'fields': {
                'driver_profile': [
                    'bank_accounts',
                    'primary_state_registration_number',
                    'tax_identification_number',
                    'identifications',
                ],
            },
        },
        {'driver_profile': {}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 6
    (
        {
            'query': {
                'park': {
                    'id': 'rent_fields_park',
                    'driver_profile': {'id': 'driver1'},
                },
            },
            'fields': {
                'driver_profile': [
                    'bank_accounts',
                    'primary_state_registration_number',
                    'tax_identification_number',
                    'identifications',
                ],
            },
        },
        {
            'driver_profile': {
                'tax_identification_number': '123',
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Msk',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18T00:00:00+0000',
                        'expire_date': '2028-12-18T00:00:00+0000',
                    },
                ],
                'primary_state_registration_number': '123',
                'bank_accounts': [
                    {
                        'russian_central_bank_identifier_code': '345',
                        'correspondent_account': '4234',
                        'client_account': '12',
                    },
                ],
            },
        },
        {
            'tin': 1,
            'phone': 1,
            'identification': 1,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 7
    (
        {
            'query': {
                'park': {
                    'id': 'rent_fields_park',
                    'driver_profile': {'id': 'driver1'},
                },
            },
            'fields': {'driver_profile': ['emergency_person_contacts']},
        },
        {
            'driver_profile': {
                'emergency_person_contacts': [
                    {'phone': '+322'},
                    {'phone': '+228'},
                ],
            },
        },
        {
            'tin': 0,
            'phone': 2,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
        },
    ),
    # 8
    (
        {
            'query': {
                'park': {
                    'id': 'rent_fields_park',
                    'driver_profile': {'id': 'driver2'},
                },
            },
            'fields': {
                'driver_profile': [
                    'bank_accounts',
                    'primary_state_registration_number',
                    'tax_identification_number',
                    'identifications',
                ],
            },
        },
        {
            'driver_profile': {
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Msk',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18T00:00:00+0000',
                        'expire_date': '2028-12-18T00:00:00+0000',
                    },
                    {
                        'type': 'national',
                        'number': '100501',
                        'address': 'Msk',
                        'postal_code': '123a13',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 24',
                        'issue_date': '2018-12-18T00:00:00+0000',
                        'expire_date': '2028-12-18T00:00:00+0000',
                    },
                ],
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 1,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 9
    (
        {
            'query': {
                'park': {
                    'id': 'rent_fields_park',
                    'driver_profile': {'id': 'driver1'},
                },
            },
            'fields': {
                'driver_profile': ['emergency_person_contacts', 'phones'],
            },
        },
        {
            'driver_profile': {
                'emergency_person_contacts': [
                    {'phone': '+322'},
                    {'phone': '+228'},
                ],
                'phones': ['+123'],
            },
        },
        {
            'tin': 0,
            'phone': 2,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
        },
    ),
    # 10, test driver ratings
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                },
            },
            'fields': {'rating': ['average_rating', 'ratings_count']},
        },
        {'driver_profile': {}, 'rating': {'average_rating': '3.5'}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 1,
            'driver_rating': 1,
            'driver_status': 0,
        },
    ),
    # 11, test driver categories
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                },
            },
            'fields': {'driver_categories': ['disabled_by_driver']},
        },
        {
            'driver_profile': {},
            'driver_categories': {'disabled_by_driver': []},
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 1,
        },
    ),
    # 12
    (
        {
            'query': {
                'park': {
                    'id': 'park_with_common_settings',
                    'driver_profile': {'id': 'superDriver_econom'},
                },
            },
            'fields': {
                'driver_categories': ['disabled_by_driver', 'affiliation'],
            },
        },
        {
            'driver_profile': {},
            'driver_categories': {
                'disabled_by_driver': ['comfort_plus', 'econom'],
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 1,
        },
    ),
    # 13
    (
        {
            'query': {
                'park': {
                    'id': 'park_with_allowed_comfortplus',
                    'driver_profile': {'id': 'superDriver_econom'},
                },
            },
            'fields': {'driver_categories': ['disabled_by_driver']},
        },
        {
            'driver_profile': {},
            'driver_categories': {'disabled_by_driver': ['comfort_plus']},
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 1,
        },
    ),
    # 14, courier
    (
        {
            'query': {
                'park': {
                    'id': 'couriers_park',
                    'driver_profile': {'id': 'courier_xxx'},
                },
            },
            'fields': {
                'car': ['id', 'is_readonly'],
                'driver_profile': [
                    'id',
                    'courier_type',
                    'driver_license',
                    'affiliation',
                ],
            },
        },
        {
            'driver_profile': {
                'id': 'courier_xxx',
                'courier_type': 'walking_courier',
                'driver_license': {
                    'birth_date': '1994-01-01T07:15:13+0000',
                    'normalized_number': 'COURIER123',
                    'number': 'COURIER123',
                    'country': 'rus',
                },
            },
            'car': {'id': 'fake_car', 'is_readonly': True},
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 15, affiliation field tests
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {'id': 'driver_ie_1_affiliation'},
                },
            },
            'fields': {'car': ['id'], 'driver_profile': ['id', 'affiliation']},
        },
        {
            'driver_profile': {
                'affiliation': {
                    'id': 'f0201c13b0274180900025559b3d2cf8',
                    'original_driver_id': 'driver_ie_1_original',
                    'original_park_id': 'park_ie_1',
                    'partner_source': 'individual_entrepreneur',
                    'state': 'active',
                },
                'id': 'driver_ie_1_affiliation',
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 16
    (
        {
            'query': {
                'park': {
                    'id': '1488',
                    'driver_profile': {'id': 'driver_se_1_affiliation'},
                },
            },
            'fields': {'car': ['id'], 'driver_profile': ['id', 'affiliation']},
        },
        {
            'driver_profile': {
                'affiliation': {
                    'id': '22d4b27fb0fa4fdeb1f676a63343754e',
                    'original_driver_id': 'driver_se_1_original',
                    'original_park_id': 'park_se_1',
                    'partner_source': 'self_employed',
                    'state': 'accepted',
                },
                'id': 'driver_se_1_affiliation',
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 17
    (
        {
            'query': {
                'park': {'id': '1488', 'driver_profile': {'id': 'driverSS2'}},
            },
            'fields': {
                'car': ['id'],
                'driver_profile': ['id', 'platform_uid'],
            },
        },
        {
            'driver_profile': {
                'id': 'driverSS2',
                'platform_uid': 'driverSS2_uid',
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 18, chairs
    # no car test
    (
        {
            'query': {
                'park': {
                    'id': 'chairs_park',
                    'driver_profile': {'id': 'driver_no_car'},
                },
            },
            'fields': {'child_chairs': ['some_field']},
        },
        {'driver_profile': {}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 19, park chairs only
    (
        {
            'query': {
                'park': {
                    'id': 'chairs_park',
                    'driver_profile': {'id': 'driver_park_chairs'},
                },
            },
            'fields': {'child_chairs': ['some_field']},
        },
        {
            'driver_profile': {},
            'child_chairs': {
                'total_chairs_count': 1,
                'confirmed_chairs': [
                    {'brand': 'Спасатель', 'confirmed_categories': [1, 2]},
                ],
                'total_boosters_count': 1,
                'confirmed_boosters_count': 1,
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 20, with driver chairs
    (
        {
            'query': {
                'park': {
                    'id': 'chairs_park',
                    'driver_profile': {'id': 'driver_with_chairs'},
                },
            },
            'fields': {'child_chairs': ['some_field']},
        },
        {
            'driver_profile': {},
            'child_chairs': {
                'total_chairs_count': 2,
                'confirmed_chairs': [
                    {'brand': 'Спасатель', 'confirmed_categories': [1, 2]},
                    {'brand': 'Яндекс', 'confirmed_categories': [1]},
                ],
                'total_boosters_count': 2,
                'confirmed_boosters_count': 2,
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 21, driver without confirmed chairs
    (
        {
            'query': {
                'park': {
                    'id': 'chairs_park',
                    'driver_profile': {'id': 'no_driver_confirmed'},
                },
            },
            'fields': {'child_chairs': ['some_field']},
        },
        {
            'driver_profile': {},
            'child_chairs': {
                'total_chairs_count': 2,
                'confirmed_chairs': [
                    {'brand': 'Спасатель', 'confirmed_categories': [1, 2]},
                ],
                'total_boosters_count': 2,
                'confirmed_boosters_count': 1,
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 22, driver cannot find car
    (
        {
            'query': {
                'park': {
                    'id': 'chairs_park',
                    'driver_profile': {'id': 'cannot_find_car'},
                },
            },
            'fields': {'child_chairs': ['some_field']},
        },
        {
            'driver_profile': {},
            'child_chairs': {
                'total_chairs_count': 0,
                'confirmed_chairs': [],
                'total_boosters_count': 0,
                'confirmed_boosters_count': 0,
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 23, test driver phones
    (
        {
            'query': {
                'park': {
                    'id': '222333',
                    'driver_profile': {'id': 'superDriver'},
                },
            },
            'fields': {'driver_profile': ['phones']},
        },
        {'driver_profile': {'phones': ['+79104607457', '+79575775757']}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 24, digital_lightbox
    (
        {
            'query': {
                'park': {
                    'id': 'digital_lightbox_park',
                    'driver_profile': {'id': 'driver1'},
                },
            },
            'fields': {'car': ['amenities'], 'driver_profile': ['id']},
        },
        {
            'driver_profile': {'id': 'driver1'},
            'car': {'amenities': ['digital_lightbox']},
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 25, permit_number
    (
        {
            'query': {
                'park': {'id': '1488', 'driver_profile': {'id': 'driver'}},
            },
            'fields': {'driver_profile': ['id', 'permit_number']},
        },
        {
            'driver_profile': {
                'id': 'driver',
                'permit_number': 'SUPER_TAXI_DRIVER_LICENSE_1',
            },
        },
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
    # 26, no permit_number
    (
        {
            'query': {
                'park': {
                    'id': 'park_ie_1',
                    'driver_profile': {'id': 'driver_ie_1_original'},
                },
            },
            'fields': {'driver_profile': ['id', 'permit_number']},
        },
        {'driver_profile': {'id': 'driver_ie_1_original'}},
        {
            'tin': 0,
            'phone': 1,
            'identification': 0,
            'unique_driver': 0,
            'driver_rating': 0,
            'driver_status': 0,
        },
    ),
]


@pytest.mark.redis_store(
    ['hset', 'status_park:STATUS_DRIVERS', 'driver2', 2],
    ['sadd', 'status_park:STATUS_DRIVERS:INTEGRATOR', 'driver2'],
    [
        'hset',
        'DATECHANGE_STATUS_DRIVERS:status_park',
        'driver2',
        '"2018-12-17T00:00:02.00000Z"',
    ],
    ['hmset', 'Driver:DisableMessage:222333', {'superDriver': 'bad guy'}],
    ['sadd', '222333:Driver:Disabled', 'superDriver'],
    ['sadd', 'status_park:Driver:Disabled', 'driver'],
    [
        'hmset',
        'Driver:DisableMessage:status_park',
        {'stuff_driver': 'you will not see this'},
    ],
)
@pytest.mark.parametrize(
    'request_json, expected_response, mock_call_times', OK_PARAMS,
)
@pytest.mark.config(TVM_ENABLED=True, TVM_DISABLE_CHECK=['parks'])
def test_ok(
        taxi_parks,
        personal_tins_bulk_retrieve,
        personal_identifications_bulk_retrieve,
        personal_phones_bulk_retrieve,
        unique_drivers,
        driver_ratings,
        driver_status_handler,
        request_json,
        expected_response,
        mock_call_times,
        tvm2_client,
):
    tvm2_client.set_ticket(
        json.dumps({'2011280': {'ticket': 'ticket-unique-drivers'}}),
    )

    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == 200, response.text
    assert personal_tins_bulk_retrieve.times_called == mock_call_times['tin']
    assert personal_identifications_bulk_retrieve.times_called == (
        mock_call_times['identification']
    )
    add_phone_calls = (
        1
        if 'driver_profile' in request_json['fields']
        and 'phones' in request_json['fields']['driver_profile']
        and 'emergency_person_contacts'
        not in request_json['fields']['driver_profile']
        else 0
    )
    assert personal_phones_bulk_retrieve.times_called == (
        mock_call_times['phone'] + add_phone_calls
    )
    assert unique_drivers.times_called == mock_call_times['unique_driver']
    if mock_call_times['unique_driver'] == 1:
        mock_request = unique_drivers.next_call()['request']
        assert mock_request.method == 'POST'
        assert mock_request.args.to_dict() == {'consumer': 'parks'}
        assert json.loads(mock_request.get_data()) == {
            'profile_id_in_set': ['222333_superDriver'],
        }
    assert driver_ratings.times_called == mock_call_times['driver_rating']
    if mock_call_times['driver_rating'] == 1:
        mock_request = driver_ratings.next_call()['request']
        assert mock_request.method == 'GET'
        assert not mock_request.get_data()
        assert mock_request.args.get('unique_driver_id') == 'unique_id'
        assert mock_request.headers.get('X-Ya-Service-Name') == 'parks'
    paths = [
        'child_chairs.confirmed_chairs',
        'child_chairs.confirmed_chairs.confirmed_categories',
    ]
    assert ordered_object.order(
        response.json(), paths,
    ) == ordered_object.order(expected_response, paths)


@pytest.mark.redis_store(
    ['hset', 'park1:STATUS_DRIVERS', 'driver1', 1],
    ['sadd', 'park1:Driver:Disabled', 'driver1'],
    ['hset', 'park1:STATUS_DRIVERS', 'driver2', 1],
    ['sadd', 'park1:Driver:Disabled', 'driver2'],
)
@pytest.mark.parametrize(
    'driver_id, expected_response',
    [
        (
            'driver2',
            {
                'accounts': [{'balance': '100.0000'}],
                'car': {'normalized_number': 'B7780P77'},
                'driver_profile': {
                    'id': 'driver2',
                    'last_name': 'Petrov',
                    'is_readonly': False,
                    'is_removed_by_request': False,
                },
                'taximeter_disable_status': {'disabled': True},
                'current_status': {'status': 'busy'},
            },
        ),
        (
            'driver1',
            {
                'accounts': [],
                'car': {'normalized_number': 'B7780P77'},
                'driver_profile': {
                    'id': 'driver1',
                    'is_readonly': True,
                    'is_removed_by_request': True,
                },
                'taximeter_disable_status': {},
                'current_status': {},
            },
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True, TVM_DISABLE_CHECK=['parks'])
def test_removed(
        config,
        taxi_parks,
        personal_tins_bulk_retrieve,
        personal_identifications_bulk_retrieve,
        personal_phones_bulk_retrieve,
        unique_drivers,
        driver_ratings,
        driver_status_handler,
        driver_id,
        expected_response,
        tvm2_client,
):
    tvm2_client.set_ticket(
        json.dumps({'2011280': {'ticket': 'ticket-unique-drivers'}}),
    )

    response = taxi_parks.post(
        ENDPOINT_URL,
        json={
            'query': {
                'park': {'id': 'park1', 'driver_profile': {'id': driver_id}},
            },
            'fields': {
                'account': ['balance'],
                'car': ['normalized_number'],
                'driver_profile': [
                    'id',
                    'is_readonly',
                    'is_removed_by_request',
                    'last_name',
                ],
                'taximeter_disable_status': ['disabled'],
                'current_status': ['status'],
            },
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


OK_RATING_REQUEST = {
    'query': {
        'park': {'id': '222333', 'driver_profile': {'id': 'superDriver'}},
    },
    'fields': {'rating': ['average_rating', 'ratings_count']},
}
OK_RATING_PARAMS = [
    (
        {'unique_driver_id': 'unique_id', 'rating': '3.5'},
        {'average_rating': '3.5'},
    ),
    (
        {'unique_driver_id': 'unique_id', 'rating': '3.0000'},
        {'average_rating': '3.0000'},
    ),
]


@pytest.mark.parametrize('driver_ratings_response, rating', OK_RATING_PARAMS)
def test_rating_ok(
        taxi_parks,
        mockserver,
        unique_drivers,
        driver_ratings_response,
        rating,
):
    @mockserver.json_handler(DRIVER_RATINGS_URL)
    def driver_ratings_mock_callback(request):
        request.get_data()
        return driver_ratings_response

    response = taxi_parks.post(
        ENDPOINT_URL, data=json.dumps(OK_RATING_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'driver_profile': {}, 'rating': rating}
    assert driver_ratings_mock_callback.times_called >= 1


@pytest.mark.parametrize('driver_ratings_code', [400, 401, 403, 404, 500, 502])
def test_driver_ratings_error(
        taxi_parks, mockserver, unique_drivers, driver_ratings_code,
):
    @mockserver.json_handler(DRIVER_RATINGS_URL)
    def driver_ratings_mock_callback(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'code': str(driver_ratings_code),
                    'message': 'driver_ratings_message',
                },
            ),
            driver_ratings_code,
        )

    response = taxi_parks.post(
        ENDPOINT_URL, data=json.dumps(OK_RATING_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'driver_profile': {}, 'rating': {}}
    assert driver_ratings_mock_callback.times_called >= 1


OK_DRIVER_METRICS_REQUEST = {
    'query': {
        'park': {'id': '222333', 'driver_profile': {'id': 'superDriver'}},
    },
    'fields': {'driver_metrics': ['activity']},
}
OK_DRIVER_METRICS_PARAMS = [
    (
        {'items': [{'unique_driver_id': 'unique_id', 'value': 90}]},
        {'activity': '90'},
    ),
    ({'items': [{'unique_driver_id': 'unique_id'}]}, {}),
    ({'items': []}, {}),
]


@pytest.mark.parametrize(
    'driver_metrics_response, driver_metrics', OK_DRIVER_METRICS_PARAMS,
)
def test_driver_metrics_ok(
        taxi_parks,
        mockserver,
        unique_drivers,
        driver_metrics_response,
        driver_metrics,
):
    @mockserver.json_handler(DRIVER_METRICS_URL)
    def driver_metrics_mock_callback(request):
        request.get_data()
        return driver_metrics_response

    response = taxi_parks.post(
        ENDPOINT_URL, data=json.dumps(OK_DRIVER_METRICS_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'driver_profile': {},
        'driver_metrics': driver_metrics,
    }
    assert driver_metrics_mock_callback.times_called >= 1


@pytest.mark.parametrize('driver_metrics_code', [400, 401, 403, 404, 500, 502])
def test_driver_metrics_error(
        taxi_parks, mockserver, unique_drivers, driver_metrics_code,
):
    @mockserver.json_handler(DRIVER_METRICS_URL)
    def driver_metrics_mock_callback(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'code': str(driver_metrics_code),
                    'message': 'driver_metrics_message',
                },
            ),
            driver_metrics_code,
        )

    response = taxi_parks.post(
        ENDPOINT_URL, data=json.dumps(OK_DRIVER_METRICS_REQUEST),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'driver_profile': {}, 'driver_metrics': {}}
    assert driver_metrics_mock_callback.times_called >= 1


@pytest.mark.parametrize('unique_drivers_code', [400, 401, 404, 500, 502])
def test_unique_drivers_error(taxi_parks, mockserver, unique_drivers_code):
    @mockserver.json_handler(UNIQUE_DRIVERS_URL)
    def unique_drivers_mock_callback(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'code': str(unique_drivers_code),
                    'message': 'unique_drivers_message',
                },
            ),
            unique_drivers_code,
        )

    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': '222333',
                        'driver_profile': {'id': 'superDriver'},
                    },
                },
                'fields': {
                    'driver_profile': ['id'],
                    'driver_metrics': ['activity'],
                    'rating': ['average_rating', 'ratings_count'],
                },
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'driver_profile': {'id': 'superDriver'},
        'driver_metrics': {},
        'rating': {},
    }
    assert unique_drivers_mock_callback.times_called >= 1


@pytest.mark.parametrize('driver_status_error_code', [400, 401, 404, 500])
def test_driver_status_errors(
        taxi_parks, mockserver, driver_status_error_code,
):
    @mockserver.json_handler(DRIVER_STATUS_URL)
    def ratings_callback(request):
        return mockserver.make_response(
            json.dumps({}), driver_status_error_code,
        )

    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': '222333',
                        'driver_profile': {'id': 'superDriver'},
                    },
                },
                'fields': {'driver_categories': ['disabled_by_driver']},
            },
        ),
    )

    assert response.status_code == 500, response.text


BAD_REQUEST_PARAMS = [
    ({}, 'query must be present'),
    ({'query': {}}, 'query.park must be present'),
    ({'query': {'park': {}}}, 'query.park.id must be present'),
    (
        {'query': {'park': {'id': ''}}},
        'query.park.id must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'x'}}},
        'query.park.driver_profile must be present',
    ),
    (
        {'query': {'park': {'id': 'x', 'driver_profile': {}}}},
        'query.park.driver_profile.id must be present',
    ),
    (
        {'query': {'park': {'id': 'x', 'driver_profile': {'id': ''}}}},
        'query.park.driver_profile.id '
        'must be a non-empty utf-8 string without BOM',
    ),
    (
        {'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}}},
        'fields must be present',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'account': ['a', 'balance', 'c', 'balance']},
        },
        'fields.account must contain unique strings (error at `balance`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'car': ['qqq', 'vvv', 'qqq']},
        },
        'fields.car must contain unique strings (error at `qqq`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'driver_profile': ['imei', 'car_id', 'imei']},
        },
        'fields.driver_profile must contain unique strings (error at `imei`)',
    ),
    (
        {
            'query': {'park': {'id': 'x', 'driver_profile': {'id': 'y'}}},
            'fields': {'account': [], 'driver_profile': []},
        },
        'fields must contain at least one field',
    ),
    (
        {
            'query': {
                'park': {
                    'id': 'x',
                    'driver_profile': {'id': 'y'},
                    'car': {'categories_filter': ['abra']},
                },
            },
        },
        'query.park.car.categories_filter each element must be one of: '
        '`business`, `cargo`, `child_tariff`, `comfort`, `comfort_plus`, '
        '`courier`, `demostand`, `econom`, `eda`, `express`, `lavka`, '
        '`limousine`, `maybach`, `minibus`, `minivan`, `mkk`, '
        '`mkk_antifraud`, `night`, `personal_driver`, `pool`, `premium_suv`, '
        '`premium_van`, `promo`, `selfdriving`, `standart`, `start`, '
        '`suv`, `trucking`, `ultimate`, `vip`, `wagon`',
    ),
]


@pytest.mark.parametrize('request_json,error_text', BAD_REQUEST_PARAMS)
def test_bad_request(taxi_parks, request_json, error_text):
    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == 400
    assert response.json() == {'error': {'text': error_text}}


def test_bad_request_bad_pd_id(
        config, taxi_parks, personal_phones_bulk_retrieve,
):
    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': '222333badpd',
                        'driver_profile': {'id': 'BadPhonesPdIdDriver'},
                    },
                },
                'fields': {'driver_profile': ['phones']},
            },
        ),
    )

    assert response.status_code == 500, response.error_text


def test_park_not_found(taxi_parks):
    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': 'abra',
                        'driver_profile': {'id': 'superDriver'},
                    },
                },
                'fields': {'driver_profile': ['id']},
            },
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        'error': {'text': 'park with id `abra` not found'},
    }


def test_driver_profile_not_found(taxi_parks):
    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': '1488',
                        'driver_profile': {'id': 'superDriver'},
                    },
                },
                'fields': {'driver_profile': ['id']},
            },
        ),
    )

    assert response.status_code == 404
    assert response.json() == {'error': {'text': 'driver profile not found'}}


@pytest.mark.parametrize('pd_error_code', [400, 401, 404, 500])
def test_failed_pd_request(
        taxi_parks,
        personal_identifications_bulk_retrieve,
        mockserver,
        pd_error_code,
):
    @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
    def mock_callback(request):
        return mockserver.make_response('some error', pd_error_code)

    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': 'rent_fields_park',
                        'driver_profile': {'id': 'driver1'},
                    },
                },
                'fields': {
                    'driver_profile': [
                        'bank_accounts',
                        'primary_state_registration_number',
                        'tax_identification_number',
                        'identifications',
                    ],
                },
            },
        ),
    )

    assert response.status_code == 500, response.text


@pytest.mark.now('2020-05-22T18:35:00+0000')
@pytest.mark.config(PARKS_DISABLE_BILLING_BALANCE=False)
@pytest.mark.parametrize('balance_value', ['12345.0000', '-3333.0000'])
def test_billing_balance(taxi_parks, mockserver, balance_value):
    @mockserver.json_handler(BALANCE_URL)
    def mock_callback(request):
        request.get_data()
        return {
            'driver_profiles': [
                {
                    'driver_profile_id': 'superDriver',
                    'balances': [
                        {
                            'accrued_at': '2020-05-22T18:35:00+00:00',
                            'total_balance': balance_value,
                        },
                    ],
                },
            ],
        }

    response = taxi_parks.post(
        ENDPOINT_URL,
        data=json.dumps(
            {
                'query': {
                    'park': {
                        'id': '222333',
                        'driver_profile': {'id': 'superDriver'},
                    },
                },
                'fields': {
                    'account': [
                        'id',
                        'type',
                        'balance',
                        'balance_limit',
                        'currency',
                    ],
                },
            },
        ),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'accounts': [
            {
                'id': 'superDriver',
                'type': 'current',
                'balance': balance_value,
                'balance_limit': '50.0000',
                'currency': 'EUR',
            },
        ],
        'driver_profile': {},
    }

    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == {
        'query': {
            'park': {
                'id': '222333',
                'driver_profile': {'ids': ['superDriver']},
            },
            'balance': {'accrued_ats': ['2020-05-22T18:35:00+00:00']},
        },
    }


TEST_USE_PD_PHONES_PARAMS = [
    (
        {
            'query': {
                'park': {
                    'id': '222333badpd',
                    'driver_profile': {'id': 'BadPhonesPdIdDriver'},
                },
            },
            'fields': {'driver_profile': ['phones']},
        },
        500,
        {'driver_profile': {'phones': ['+79575665757']}},
        '',
    ),
    (
        {
            'query': {
                'park': {
                    'id': '222333badpd',
                    'driver_profile': {'id': 'NoPhonesDriver'},
                },
            },
            'fields': {'driver_profile': ['phones']},
        },
        200,
        {'driver_profile': {'phones': ['+79211237321', '89031237321']}},
        '',
    ),
]


@pytest.mark.parametrize(
    'request_json, expected_code, expected_response, ' 'expected_error',
    TEST_USE_PD_PHONES_PARAMS,
)
def test_use_pd_phones(
        taxi_parks,
        request_json,
        expected_code,
        expected_response,
        expected_error,
        mock_personal_data,
        tvm2_client,
):
    tvm2_client.set_ticket(
        json.dumps({'2011280': {'ticket': 'ticket-unique-drivers'}}),
    )

    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == expected_response


@pytest.fixture
def mock_personal_data2(mockserver):
    class PersonalData2Context:
        def __init__(self):
            self.retrieve_response = {'items': []}

        def set_retrieve_response(self, data):
            self.retrieve_response = data

    context = PersonalData2Context()

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        return context.retrieve_response

    return context


def test_personal_retrieve_permutations(
        config, taxi_parks, mock_personal_data2, tvm2_client,
):
    request_json = {
        'query': {
            'park': {
                'id': 'rent_fields_park',
                'driver_profile': {'id': 'driver1'},
            },
        },
        'fields': {'driver_profile': ['emergency_person_contacts', 'phones']},
    }

    expected_response = {
        'driver_profile': {
            'emergency_person_contacts': [
                {'phone': '+322'},
                {'phone': '+228'},
            ],
            'phones': ['+123'],
        },
    }

    pairs = [
        {'id': 'id_+123', 'value': '+123'},
        {'id': 'id_+228', 'value': '+228'},
        {'id': 'id_+322', 'value': '+322'},
    ]

    pd_resp = {'items': [{'id': 'id_+123', 'value': '+123'}]}
    mock_personal_data2.set_retrieve_response(pd_resp)

    response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))
    assert response.status_code == 500

    for perm in itertools.permutations(pairs):
        pd_resp = {'items': perm}
        mock_personal_data2.set_retrieve_response(pd_resp)

        response = taxi_parks.post(ENDPOINT_URL, data=json.dumps(request_json))

        assert response.status_code == 200
        assert response.json() == expected_response
