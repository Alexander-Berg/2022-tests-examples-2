# encoding=utf-8
import copy
import json

import pytest

from . import error
from . import utils


PUT_ENDPOINT_URL = '/driver-profiles/personal'
PATCH_ENDPOINT_URL = '/driver-profiles/personal-patch'
ENDPOINT_URLS = [PUT_ENDPOINT_URL, PATCH_ENDPOINT_URL]
PARKS_USERS_LIST_URL = '/dispatcher_access_control/v1/parks/users/list'
DRIVER_UPDATED_TRIGGER_URL = (
    '/taximeter-xservice.taxi.yandex.net/' 'utils/driver-updated-trigger'
)

ALL_FIELDS = {
    'first_name',
    'middle_name',
    'last_name',
    'phones',
    'email',
    'address',
    'deaf',
    'driver_license',
    'tax_identification_number',
    'emergency_person_contacts',
    'identifications',
    'primary_state_registration_number',
    'bank_accounts',
    'professional_certificate_expiration_date',
    'road_penalties_record_issue_date',
    'background_criminal_record_issue_date',
    'sex',
    'permit_number',
}

AUTHOR_YA_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-Ip': '1.2.3.4',
}


def get_driver(db, park_id, driver_id):
    return db.dbdrivers.find_one({'park_id': park_id, 'driver_id': driver_id})


def add_license(driver_profile):
    driver_profile['driver_license']['normalized_number'] = driver_profile[
        'driver_license'
    ]['number']


def make_patch_request_if_need(request, endpoint):
    if endpoint == PATCH_ENDPOINT_URL:
        to_set = copy.deepcopy(request['driver_profile'])
        set_fields = {key for key in to_set}
        unset_fields = ALL_FIELDS - set_fields
        return {'driver_profile': {'set': to_set, 'unset': list(unset_fields)}}
    else:
        return request


PERSONAL = {
    'driver_profile': {
        'first_name': 'Andrew',
        'middle_name': 'Alex',
        'last_name': 'Miro',
        'phones': ['+79217652331', '+89031234567'],
        'email': 'asd@asd.ru',
        'address': 'Мск',
        'deaf': True,
        'driver_license': {
            'country': 'fra',
            'number': '123412345678',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
        'permit_number': 'SUPER_TAXI_DRIVER_LICENSE_1',
    },
}

MONGO_DRIVER_LICENSE = '123412345678'
MONGO_DRIVER_EMAIL = 'asd@asd.ru'

MONGO_DRIVER1 = {
    'park_id': '123',
    'driver_id': '0',
    'first_name': 'Andrew',
    'middle_name': 'Alex',
    'last_name': 'Miro',
    'phone_pd_ids': ['id_+79217652331', 'id_+89031234567'],
    'email': MONGO_DRIVER_EMAIL,
    'email_pd_id': 'id_' + MONGO_DRIVER_EMAIL,
    'address': 'Мск',
    'deaf': True,
    'license_country': 'fra',
    'license_number': MONGO_DRIVER_LICENSE,
    'license': MONGO_DRIVER_LICENSE,
    'license_normalized': MONGO_DRIVER_LICENSE,
    'driver_license_pd_id': 'id_' + MONGO_DRIVER_LICENSE,
    'license_driver_birth_date': '1939-09-01T00:00:00+0000',
    'license_expire_date': '2028-11-20T00:00:00+0000',
    'license_issue_date': '2018-11-20T00:00:00+0000',
    'work_status': 'working',
    'rule_id': 'rule_zero',
    'providers': ['yandex', 'park'],
    'balance_limit': 50,
    'hire_date': '2018-11-20T00:00:00+0000',
    'hiring_details': {
        'hiring_date': '2018-11-20T00:00:00+0000',
        'hiring_type': 'commercial',
    },
    'hiring_source': 'selfreg',
    'car_id': '12345',
    'comment': 'ads',
    'check_message': 'qwe',
    'permit_number': 'SUPER_TAXI_DRIVER_LICENSE_1',
    'platform_uid': 'driver_platform_uid_1',
}


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        return {}

    return mock_callback


OK_PARAMS = [
    (
        '123',
        {},
        {},
        {},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
        },
    ),
    (
        '123',
        {
            'driver_profile': {
                'tax_identification_number': '123',
                'emergency_person_contacts': [
                    {'phone': '+228'},
                    {'phone': '+322'},
                ],
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Msk',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18',
                        'expire_date': '2028-12-18',
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
            'park_id': '123',
            'identification_pd_ids': ['id_100500'],
            'emergency_person_contacts': [
                {'phone_pd_id': 'id_+228'},
                {'phone_pd_id': 'id_+322'},
            ],
            'tax_identification_number_pd_id': 'id_123',
            'primary_state_registration_number': '123',
            'bank_accounts': [
                {
                    'russian_central_bank_identifier_code': '345',
                    'correspondent_account': '4234',
                    'client_account': '12',
                },
            ],
        },
        {},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
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
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 1,
            'phones': 1,
            'tins': 1,
        },
    ),
    # test optional driver birth date
    (
        '123',
        {},
        {},
        {'driver_profile': {'driver_license': 'birth_date'}},
        'license_driver_birth_date',
        {
            'driver_profile': {
                'driver_license': {
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
        },
    ),
    # Romania fields test
    (
        '322',
        {
            'driver_profile': {
                'tax_identification_number': '123',
                'professional_certificate_expiration_date': '2019-12-27',
                'road_penalties_record_issue_date': '2017-12-27',
                'background_criminal_record_issue_date': '2017-12-27',
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Msk',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18',
                        'expire_date': '2028-12-18',
                    },
                ],
            },
        },
        {
            'park_id': '322',
            'identification_pd_ids': ['id_100500'],
            'tax_identification_number_pd_id': 'id_123',
            'professional_certificate_expiration_date': (
                '2019-12-27T00:00:00+0000'
            ),
            'road_penalties_record_issue_date': '2017-12-27T00:00:00+0000',
            'background_criminal_record_issue_date': (
                '2017-12-27T00:00:00+0000'
            ),
        },
        {},
        'platform_uid',
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'professional_certificate_expiration_date': (
                    '2019-12-27T00:00:00+0000'
                ),
                'road_penalties_record_issue_date': '2017-12-27T00:00:00+0000',
                'background_criminal_record_issue_date': (
                    '2017-12-27T00:00:00+0000'
                ),
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
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 1,
            'phones': 1,
            'tins': 1,
        },
    ),
    # Sex field
    (
        '322',
        {
            'driver_profile': {
                'tax_identification_number': '123',
                'sex': 'male',
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Msk',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18',
                        'expire_date': '2028-12-18',
                    },
                ],
            },
        },
        {
            'park_id': '322',
            'identification_pd_ids': ['id_100500'],
            'tax_identification_number_pd_id': 'id_123',
            'sex': 'male',
        },
        {},
        'platform_uid',
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'sex': 'male',
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
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 1,
            'phones': 1,
            'tins': 1,
        },
    ),
]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'park_id, extra_fields, extra_db_fields, '
    'remove_fields, remove_db_fields,'
    'response_replacement, mock_call_times',
    OK_PARAMS,
)
def test_put_ok(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        db,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        park_id,
        extra_fields,
        extra_db_fields,
        remove_fields,
        remove_db_fields,
        response_replacement,
        mock_call_times,
        mockserver,
):
    @mockserver.json_handler(
        '/contractor_profiles_manager/v1/' 'hiring-type-restriction/retrieve',
    )
    def mock_cpm_callback(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'is_restricted': True,
                    'available_hiring_type': 'commercial',
                    'hiring_date': '2018-11-20T00:00:00+0000',
                    'is_warning_expected': True,
                },
            ),
            200,
        )

    request_driver = utils.remove(
        utils.replace(PERSONAL, extra_fields), remove_fields,
    )
    expected_in_mongo = utils.remove(
        utils.replace(MONGO_DRIVER1, extra_db_fields), remove_db_fields,
    )

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': park_id, 'id': '0'},
        data=json.dumps(
            make_patch_request_if_need(request_driver, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert dispatcher_access_control.times_called == 1
    assert driver_updated_trigger.times_called == 1

    assert personal_driver_licenses_bulk_store.times_called == (
        mock_call_times['driver_licenses']
    )
    assert personal_emails_bulk_store.times_called == mock_call_times['emails']
    assert personal_identifications_bulk_store.times_called == (
        mock_call_times['identifications']
    )
    assert personal_phones_bulk_store.times_called == mock_call_times['phones']
    assert personal_tins_bulk_store.times_called == mock_call_times['tins']

    driver_in_mongo = utils.datetime_to_str(get_driver(db, park_id, '0'))
    assert driver_in_mongo.pop('_id') is not None
    assert driver_in_mongo.pop('updated_ts') is not None
    assert driver_in_mongo.pop('created_date') is not None
    assert driver_in_mongo.pop('modified_date') is not None
    assert driver_in_mongo == expected_in_mongo

    expected_response = copy.deepcopy(request_driver)
    expected_response['driver_profile']['id'] = '0'
    expected_response['driver_profile']['park_id'] = park_id
    expected_response['driver_profile']['hiring_details'] = {
        'hiring_date': '2018-11-20T00:00:00+0000',
        'hiring_type': 'commercial',
    }
    response_to_check = response.json()
    add_license(expected_response['driver_profile'])
    # we don't want to change format of returned dates right now
    expected_response = utils.replace(expected_response, response_replacement)
    assert response_to_check == expected_response


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'remove, projection, mongo_projection',
    [
        ({'driver_profile': 'deaf'}, {'driver_profile': 'deaf'}, 'deaf'),
        (
            {'driver_profile': 'address'},
            {'driver_profile': 'address'},
            'address',
        ),
        ({}, {'driver_profile': 'sex'}, 'sex'),
        (
            {'driver_profile': 'permit_number'},
            {'driver_profile': 'permit_number'},
            'permit_number',
        ),
    ],
)
def test_unset(
        taxi_parks,
        db,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        endpoint_url,
        remove,
        projection,
        mongo_projection,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(
            make_patch_request_if_need(
                utils.remove(PERSONAL, remove), endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text

    driver_in_mongo = utils.datetime_to_str(get_driver(db, '123', '0'))
    assert utils.projection(response.json(), projection) == {}
    assert utils.projection(driver_in_mongo, mongo_projection) == {}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_unset_extra_fields(
        taxi_parks,
        db,
        endpoint_url,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
):
    personal = {
        'driver_profile': {
            'first_name': 'Andrew',
            'middle_name': 'Alex',
            'last_name': 'Miro',
            'phones': [],
            'email': 'asd@asd.ru',
            'address': 'Мск',
            'deaf': True,
            'driver_license': {
                'country': 'fra',
                'number': '12345EE',
                'birth_date': '1939-09-01',
                'expiration_date': '2028-11-20',
                'issue_date': '2018-11-20',
            },
        },
    }

    projection = {
        'driver_profile': [
            'identifications',
            'tax_identification_number',
            'primary_state_registration_number',
            'bank_accounts',
        ],
    }

    mongo_projection = [
        'identification_pd_ids',
        'tax_identification_number_pd_id',
        'primary_state_registration_number',
        'bank_accounts',
    ]

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '7'},
        data=json.dumps(make_patch_request_if_need(personal, endpoint_url)),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text

    driver_in_mongo = utils.datetime_to_str(get_driver(db, '123', '7'))
    assert utils.projection(response.json(), projection) == {}
    assert utils.projection(driver_in_mongo, mongo_projection) == {}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_no_such_driver(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        endpoint_url,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': 'no_such'},
        data=json.dumps(PERSONAL),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'no_such_driver', 'no_such_driver',
    )


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'replacement, error_message',
    [
        ({'driver_profile': {'phones': ['+711', '+1000']}}, 'duplicate_phone'),
        (
            {
                'driver_profile': {
                    'driver_license': {'country': 'fra', 'number': 'DUP'},
                },
            },
            'duplicate_driver_license',
        ),
        (
            {'driver_profile': {'platform_uid': 'test_uid'}},
            'platform_uid cannot be modified',
        ),
    ],
)
def test_invalid(
        taxi_parks,
        endpoint_url,
        contractor_profiles_manager,
        replacement,
        error_message,
        personal_phones_bulk_find,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(PERSONAL, replacement), endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        error_message, error_message,
    )


@pytest.mark.experiments3(
    name='parks_disable_driver_creation_by_license',
    consumers=['parks/driver_profiles'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'parks/driver_profiles',
            'value': 1234,
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'replacement, response_code, response_json',
    [
        (
            {
                'driver_profile': {
                    'driver_license': {
                        'country': 'rus',
                        'number': '123412345678',
                    },
                },
            },
            400,
            error.make_error_response(
                'forbidden_driver_license', 'forbidden_driver_license',
            ),
        ),
    ],
)
def test_forbidden_license(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        replacement,
        response_code,
        response_json,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(PERSONAL, replacement), endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == response_code, response.text
    assert response.json() == response_json


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_cannot_change_removed_driver(
        db, mockserver, taxi_parks, endpoint_url,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': 'removed_driver'},
        json=PERSONAL,
        headers=AUTHOR_YA_HEADERS,
    )
    assert response.status_code == 400, response.text
    code = 'cannot_edit_removed_driver'
    assert response.json() == error.make_error_response(code, code)


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_cannot_change_readonly_driver(
        db, mockserver, taxi_parks, endpoint_url,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': 'readonly_driver'},
        json=PERSONAL,
        headers=AUTHOR_YA_HEADERS,
    )
    assert response.status_code == 400, response.text
    code = 'cannot_edit_readonly_driver'
    assert response.json() == error.make_error_response(code, code)


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'replacement',
    [
        ({'driver_profile': {'phones': ['+711', '+1000']}}),
        (
            {
                'driver_profile': {
                    'driver_license': {'country': 'fra', 'number': 'DUP'},
                },
            }
        ),
    ],
)
def test_dont_check_yourself_for_duplicates(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        endpoint_url,
        replacement,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '1'},
        data=json.dumps(
            make_patch_request_if_need(
                utils.replace(PERSONAL, replacement), endpoint_url,
            ),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text


CHANGES_PERSONAL = {
    'driver_profile': {
        'first_name': 'Andrew',
        'middle_name': 'Al',
        'last_name': 'Mir',
        'phones': ['+714680'],
        'email': 'asd@asd.ru',
        'address': 'Мск',
        'deaf': True,
        'driver_license': {
            'country': 'fra',
            'number': '12324680AAA',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
}

CHANGES_PERSONAL2 = {
    'driver_profile': {
        'first_name': 'Andrew',
        'middle_name': 'Al',
        'last_name': 'Mir',
        'phones': ['+714680'],
        'email': 'asd@asd.ru',
        'address': 'Мск',
        'driver_license': {
            'country': 'fra',
            'number': '12324680BBB',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
}

CHANGES_PERSONAL3 = {
    'driver_profile': {
        'first_name': 'Andrew',
        'middle_name': 'Al',
        'last_name': 'Mir',
        'phones': [],
        'email': 'asd@asd.ru',
        'address': 'Мск',
        'driver_license': {
            'country': 'fra',
            'number': '12345EE',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'id, personal, to_unset, expected',
    [
        (
            '4',
            CHANGES_PERSONAL,
            {},
            {
                'Deaf': {'current': 'True', 'old': ''},
                'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
                'driver_license_pd_id': {
                    'current': 'id_12324680AAA',
                    'old': '',
                },
                'phone_pd_ids': {
                    'current': '["id_+714680"]',
                    'old': '["id_+48123"]',
                },
                'HiringDetails': {
                    'current': '',
                    'old': (
                        '{"hiring_date":"2018-11-20T00:00:00+0000",'
                        '"hiring_type":"commercial"}'
                    ),
                },
            },
        ),
        (
            '4',
            CHANGES_PERSONAL,
            {'driver_profile': ['middle_name', 'deaf']},
            {
                'MiddleName': {'current': '', 'old': 'Al'},
                'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
                'driver_license_pd_id': {
                    'current': 'id_12324680AAA',
                    'old': '',
                },
                'phone_pd_ids': {
                    'current': '["id_+714680"]',
                    'old': '["id_+48123"]',
                },
                'HiringDetails': {
                    'current': '',
                    'old': (
                        '{"hiring_date":"2018-11-20T00:00:00+0000",'
                        '"hiring_type":"commercial"}'
                    ),
                },
            },
        ),
        # test series removing
        (
            '5',
            CHANGES_PERSONAL2,
            {},
            {
                'LicenseNumber': {'current': '12324680BBB', 'old': '24680BBB'},
                'LicenseSeries': {'current': '', 'old': '123'},
                'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
                'driver_license_pd_id': {
                    'current': 'id_12324680BBB',
                    'old': '',
                },
                'phone_pd_ids': {
                    'current': '["id_+714680"]',
                    'old': '["id_+48123"]',
                },
                'HiringDetails': {
                    'current': '',
                    'old': (
                        '{"hiring_date":"2018-11-20T00:00:00+0000",'
                        '"hiring_type":"commercial"}'
                    ),
                },
            },
        ),
        # test identification, tin, PSRN, bank_accounts
        (
            '7',
            CHANGES_PERSONAL3,
            {},
            {
                'identification_pd_ids': {
                    'old': '["id_100500"]',
                    'current': '',
                },
                'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
                'driver_license_pd_id': {'current': 'id_12345EE', 'old': ''},
                'tax_identification_number_pd_id': {
                    'old': 'id_123',
                    'current': '',
                },
                'primary_state_registration_number': {
                    'old': '123',
                    'current': '',
                },
                'bank_accounts': {
                    'old': (
                        '[{"client_account":"12",'
                        '"correspondent_account":"4234",'
                        '"russian_central_bank_identifier_code":"345"}]'
                    ),
                    'current': '',
                },
            },
        ),
    ],
)
@pytest.mark.sql('taximeter', 'SELECT 1')
def test_change_log(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        sql_databases,
        endpoint_url,
        id,
        personal,
        to_unset,
        expected,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    patched_personal = utils.remove(personal, to_unset)

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': id},
        data=json.dumps(
            make_patch_request_if_need(patched_personal, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert dispatcher_access_control.times_called == 1

    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        'SELECT * FROM changes_0 WHERE object_id=\'{}\' ' 'ORDER BY date DESC'
    ).format(id)
    cursor.execute(query)
    rows = cursor.fetchall()
    change = list(rows[0])
    assert change[0] == '123'
    # skip id and date
    change[8] = json.loads(change[8])
    assert change[3:] == [
        id,
        'MongoDB.Docs.Driver.DriverDoc',
        '1',
        'Boss',
        len(expected),
        expected,
        '1.2.3.4',
    ]


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(
    PARKS_MODIFICATIONS_WITH_ABSENT_USER_NAME={
        'enabled': True,
        'log_default_name': '-user-has-no-name-',
    },
)
@pytest.mark.sql('taximeter', 'SELECT 1')
def test_change_log_absent_user_name(
        taxi_parks,
        mockserver,
        endpoint_url,
        contractor_profiles_manager,
        driver_updated_trigger,
        sql_databases,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    @mockserver.json_handler(PARKS_USERS_LIST_URL)
    def mock_callback(request):
        return utils.make_users_list_response()

    expected = {
        'Deaf': {'current': 'True', 'old': ''},
        'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
        'driver_license_pd_id': {'current': 'id_12324680AAA', 'old': ''},
        'phone_pd_ids': {'current': '["id_+714680"]', 'old': '["id_+48123"]'},
        'HiringDetails': {
            'current': '',
            'old': (
                '{"hiring_date":"2018-11-20T00:00:00+0000",'
                '"hiring_type":"commercial"}'
            ),
        },
    }

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '4'},
        data=json.dumps(
            make_patch_request_if_need(CHANGES_PERSONAL, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1

    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        'SELECT * FROM changes_0 WHERE object_id=\'{}\' ' 'ORDER BY date DESC'
    ).format('4')
    cursor.execute(query)
    rows = cursor.fetchall()
    change = list(rows[0])
    assert change[0] == '123'
    # skip id and date
    change[8] = json.loads(change[8])
    assert change[3:] == [
        '4',
        'MongoDB.Docs.Driver.DriverDoc',
        '1',
        '-user-has-no-name-',
        len(expected),
        expected,
        '1.2.3.4',
    ]


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(
    PARKS_MODIFICATIONS_WITH_ABSENT_USER_NAME={
        'enabled': False,
        'log_default_name': '-user-has-no-name-',
    },
)
def test_change_log_absent_user_name_forbidden(
        taxi_parks,
        mockserver,
        contractor_profiles_manager,
        endpoint_url,
        personal_phones_bulk_find,
):
    @mockserver.json_handler(PARKS_USERS_LIST_URL)
    def mock_callback(request):
        return utils.make_users_list_response()

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '4'},
        data=json.dumps(
            make_patch_request_if_need(CHANGES_PERSONAL, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 500, response.text
    assert mock_callback.times_called == 1


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.now('2019-01-01T00:00:00Z')
def test_change_log_redis(
        taxi_parks,
        redis_store,
        testpoint,
        endpoint_url,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    @testpoint('unavailable_postgres')
    def unavailable_postgres(data):
        return {'unavailable_postgres': True}

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '4'},
        data=json.dumps(
            make_patch_request_if_need(CHANGES_PERSONAL, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200

    change = json.loads(
        list(redis_store.hgetall('EntityChangelog:Errors').values())[0],
    )
    assert change['change'].pop('id', None) is not None
    assert change == {
        'change': {
            # 'id' is poped
            'date': '2019-01-01T00:00:00+0000',
            'object_id': '4',
            'object_type': 'MongoDB.Docs.Driver.DriverDoc',
            'user_id': '1',
            'user_name': 'Boss',
            'ip': '1.2.3.4',
            'count': 5,
            'values': {
                'Deaf': {'current': 'True', 'old': ''},
                'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
                'driver_license_pd_id': {
                    'current': 'id_12324680AAA',
                    'old': '',
                },
                'phone_pd_ids': {
                    'current': '["id_+714680"]',
                    'old': '["id_+48123"]',
                },
                'HiringDetails': {
                    'current': '',
                    'old': (
                        '{"hiring_date":"2018-11-20T00:00:00+0000",'
                        '"hiring_type":"commercial"}'
                    ),
                },
            },
        },
        'date': '2019-01-01T00:00:00+0000',
        'db': '123',
        'exception': 'unavailable postgres emulated',
    }


PERSONAL2_LICENSE = '123412345AAA'
PERSONAL2_EMAIL = 'asd@asd.ru'
PERSONAL2_PHONES = ['+79217652331', '+89031234567']

PERSONAL2 = {
    'driver_profile': {
        'first_name': 'Andrew',
        'middle_name': 'Alex',
        'last_name': 'Miro',
        'phones': PERSONAL2_PHONES,
        'email': PERSONAL2_EMAIL,
        'address': 'Мск',
        'deaf': True,
        'driver_license': {
            'country': 'fra',
            'number': PERSONAL2_LICENSE,
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
}

MONGO_DRIVER2 = {
    'park_id': '123',
    'driver_id': '6',
    'first_name': 'Andrew',
    'middle_name': 'Alex',
    'last_name': 'Miro',
    'phone_pd_ids': list(map(lambda x: 'id_' + x, PERSONAL2_PHONES)),
    'email': PERSONAL2_EMAIL,
    'email_pd_id': 'id_' + PERSONAL2_EMAIL,
    'address': 'Мск',
    'deaf': True,
    'license_country': 'fra',
    'license_number': PERSONAL2_LICENSE,
    'license': PERSONAL2_LICENSE,
    'license_normalized': PERSONAL2_LICENSE,
    'driver_license_pd_id': 'id_' + PERSONAL2_LICENSE,
    'license_driver_birth_date': '1939-09-01T00:00:00+0000',
    'license_expire_date': '2028-11-20T00:00:00+0000',
    'license_issue_date': '2018-11-20T00:00:00+0000',
    'work_status': 'working',
    'rule_id': 'rule_zero',
    'providers': ['yandex', 'park'],
    'balance_limit': 50,
    'hire_date': '2018-11-20T00:00:00+0000',
    'hiring_details': {},
    'hiring_source': 'selfreg',
    'car_id': '12345',
    'comment': 'ads',
    'check_message': 'qwe',
}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'to_set, to_unset, mongo_set, mongo_unset',
    [
        (
            {'driver_profile': {'phones': ['+712345']}},
            {},
            {'phone_pd_ids': ['id_+712345']},
            {},
        ),
        (
            {'driver_profile': {'phones': ['+7123999']}},
            {'driver_profile': 'deaf'},
            {'phone_pd_ids': ['id_+7123999']},
            'deaf',
        ),
        (
            {
                'driver_profile': {
                    'driver_license': {'number': '10050012345AAA'},
                },
            },
            {},
            {
                'license_number': '10050012345AAA',
                'license': '10050012345AAA',
                'license_normalized': '10050012345AAA',
                'driver_license_pd_id': 'id_10050012345AAA',
            },
            {},
        ),
    ],
)
def test_driver_updated_trigger(
        mockserver,
        db,
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        endpoint_url,
        to_set,
        to_unset,
        mongo_set,
        mongo_unset,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    personal = utils.remove(utils.replace(PERSONAL2, to_set), to_unset)

    old_driver = utils.remove(
        utils.datetime_to_str(get_driver(db, '123', '6')),
        ['_id', 'modified_date', 'created_date'],
    )

    new_driver = utils.remove(
        utils.replace(MONGO_DRIVER2, mongo_set), mongo_unset,
    )

    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        request.get_data()  # to save request
        return '{}'

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '6'},
        data=json.dumps(make_patch_request_if_need(personal, endpoint_url)),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1

    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    trigger_request = json.loads(mock_request.get_data())
    assert trigger_request['old_driver'].pop('_id', None) is not None
    assert trigger_request['old_driver'].pop('modified_date', None) is not None
    assert trigger_request['old_driver'].pop('created_date', None) is not None
    assert trigger_request['new_driver'].pop('_id', None) is not None
    assert trigger_request['new_driver'].pop('modified_date', None) is not None
    assert trigger_request['new_driver'].pop('created_date', None) is not None
    assert trigger_request == {
        'old_driver': old_driver,
        'new_driver': new_driver,
    }


# same as test as the previous, exept using mock_personal_data
# to imitate bulk_find cant't find any records
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'to_set, to_unset, mongo_set, mongo_unset',
    [
        (
            {'driver_profile': {'phones': ['+712345']}},
            {},
            {'phone_pd_ids': ['id_+712345']},
            {},
        ),
        (
            {'driver_profile': {'phones': ['+7123999']}},
            {'driver_profile': 'deaf'},
            {'phone_pd_ids': ['id_+7123999']},
            'deaf',
        ),
    ],
)
def test_driver_updated_trigger2(
        mockserver,
        db,
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        endpoint_url,
        to_set,
        to_unset,
        mongo_set,
        mongo_unset,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        mock_personal_data,
):
    personal = utils.remove(utils.replace(PERSONAL2, to_set), to_unset)

    old_driver = utils.remove(
        utils.datetime_to_str(get_driver(db, '123', '6')),
        ['_id', 'modified_date', 'created_date'],
    )

    new_driver = utils.remove(
        utils.replace(MONGO_DRIVER2, mongo_set), mongo_unset,
    )

    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        request.get_data()  # to save request
        return '{}'

    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '6'},
        data=json.dumps(make_patch_request_if_need(personal, endpoint_url)),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1

    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    trigger_request = json.loads(mock_request.get_data())
    assert trigger_request['old_driver'].pop('_id', None) is not None
    assert trigger_request['old_driver'].pop('modified_date', None) is not None
    assert trigger_request['old_driver'].pop('created_date', None) is not None
    assert trigger_request['new_driver'].pop('_id', None) is not None
    assert trigger_request['new_driver'].pop('modified_date', None) is not None
    assert trigger_request['new_driver'].pop('created_date', None) is not None
    assert trigger_request == {
        'old_driver': old_driver,
        'new_driver': new_driver,
    }


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
def test_forbid_license_change(
        db,
        taxi_parks,
        endpoint_url,
        contractor_profiles_manager,
        dispatcher_access_control,
        personal_phones_bulk_find,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        taximeter_xservice_mock,
):
    taximeter_xservice_mock.set_driver_exams_retrieve_response(
        {'dkvu_exam': {'pass': {'status': 'pending'}}, 'biometry': {}},
    )
    mongo_before = get_driver(db, '123', '0')
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        data=json.dumps(make_patch_request_if_need(PERSONAL, endpoint_url)),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 400, response.text
    error_message = 'cannot_edit_driver_license_and_full_name_when_dkvu_passed'
    assert response.json() == error.make_error_response(
        error_message, error_message,
    )

    assert taximeter_xservice_mock.driver_exams_retrieve.times_called == 1
    mock_request = taximeter_xservice_mock.driver_exams_retrieve.next_call()[
        'request'
    ]
    assert mock_request.method == 'POST'
    assert json.loads(mock_request.get_data()) == {
        'locale': 'ru',
        'query': {'park': {'driver_profile': {'id': '0'}, 'id': '123'}},
    }
    assert 'application/json' in mock_request.headers['Content-Type']

    mongo_after = get_driver(db, '123', '0')
    assert mongo_after == mongo_before


SIGNALQ_PERSONAL_REQUEST = {
    'driver_profile': {
        'first_name': 'Ашот',
        'middle_name': 'Сигналкулович',
        'last_name': 'Камерный',
        'phones': [],
        'email': 'asd@asd.ru',
    },
}

SIGNALQ_PERSONAL_MONGO = {
    'driver_id': 'signalq_0',
    'first_name': 'Ашот',
    'last_name': 'Камерный',
    'middle_name': 'Сигналкулович',
    'park_id': 'only_signalq_park1',
    'password': '228',
    'providers': ['yandex'],
    'work_status': 'not_working',
    'email': 'asd@asd.ru',
    'email_pd_id': 'id_asd@asd.ru',
}


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_signalq_driver(
        taxi_parks,
        db,
        dispatcher_access_control,
        contractor_profiles_manager,
        driver_updated_trigger,
        endpoint_url,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': 'only_signalq_park1', 'id': 'signalq_0'},
        data=json.dumps(
            make_patch_request_if_need(SIGNALQ_PERSONAL_REQUEST, endpoint_url),
        ),
        headers=AUTHOR_YA_HEADERS,
    )

    assert response.status_code == 200, response.text

    driver_in_mongo = utils.datetime_to_str(
        get_driver(db, 'only_signalq_park1', 'signalq_0'),
    )
    assert driver_in_mongo.pop('_id') is not None
    assert driver_in_mongo.pop('updated_ts') is not None
    assert driver_in_mongo.pop('created_date') is not None
    assert driver_in_mongo.pop('modified_date') is not None
    assert driver_in_mongo == SIGNALQ_PERSONAL_MONGO

    expected_response = copy.deepcopy(SIGNALQ_PERSONAL_REQUEST)
    expected_response['driver_profile']['id'] = 'signalq_0'
    expected_response['driver_profile']['park_id'] = 'only_signalq_park1'
    response_to_check = response.json()

    if endpoint_url == PATCH_ENDPOINT_URL:
        expected_response['driver_profile'].pop('phones')

    assert response_to_check == expected_response
