# encoding=utf-8
import copy
import json
import uuid

import pytest

from . import error
from . import utils


ENDPOINT_URL = '/driver-profiles/create'
ENDPOINT_INTERNAL_URL = '/internal/driver-profiles/create'
PARKS_USERS_LIST_URL = '/dispatcher_access_control/v1/parks/users/list'

DRIVER_UPDATED_TRIGGER_URL = (
    '/taximeter-xservice.taxi.yandex.net/' 'utils/driver-updated-trigger'
)

ENDPOINT_URLS = (ENDPOINT_URL, ENDPOINT_INTERNAL_URL)

NOW = '2021-10-04T12:00:00+00:00'
PARK_ID = '123'

AUTHOR_YA_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-Ip': '1.2.3.4',
}
AUTHOR_DRIVER_HEADERS = {'X-YaTaxi-Driver-Id': 'driver-author'}
AUTHOR_FLEET_API_HEADERS = {
    'X-Fleet-API-Client-ID': 'antontodua',
    'X-Fleet-API-Key-ID': '17',
    'X-Real-Ip': '8.7.6.5',
}
CHANGE_LOG_AUTHOR_PARAMS = [
    (AUTHOR_YA_HEADERS, '1', 'Boss', '1.2.3.4'),
    (AUTHOR_DRIVER_HEADERS, 'driver-author', 'Driver', ''),
    (AUTHOR_FLEET_API_HEADERS, '17', 'API7 Key 17', '8.7.6.5'),
]

AUTHOR_YA_TEAM_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-team-11',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Real-Ip': '1.2.3.4',
}

AUTHOR_YA_UNREAL_HEADERS = {
    'X-Ya-User-Ticket': 'unreal_user_ticket',
    'X-Ya-User-Ticket-Provider': 'unreal_user_ticket_provider',
    'X-Real-Ip': '12.34.56.78',
}

BASE_DRIVER = {
    'accounts': [{'balance_limit': '50.0000', 'type': 'current'}],
    'driver_profile': {
        'first_name': 'Andrew',
        'middle_name': 'Andrewich',
        'last_name': 'Andrewson',
        'phones': ['+71234567'],
        'email': 'asd@asd.ru',
        'driver_license': {
            'country': 'rus',
            'number': '123412345678',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
        'work_rule_id': 'rule_zero',
        'providers': ['yandex', 'park'],
        'hire_date': '2018-11-20',
        'payment_service_id': '123457',
    },
}


def get_driver(db, park_id, license):
    if license is not None:
        return db.dbdrivers.find_one({'park_id': park_id, 'license': license})
    return db.dbdrivers.find_one({'park_id': park_id, 'license': None})


def add_license(driver_profile):
    driver_profile['driver_license']['normalized_number'] = driver_profile[
        'driver_license'
    ]['number']


def add_hiring_details_date(driver_profile):
    driver_profile['hiring_details'] = utils.replace(
        driver_profile.get('hiring_details'),
        {'hiring_date': '2019-11-20T00:00:00+0000'},
    )


def get_idempotency_header(token=None):
    if token is None:
        token = uuid.uuid1().hex * 4  # 128 ASCII symbols
    return {'X-Idempotency-Token': token}


def build_data(endpoint_url, data=BASE_DRIVER, headers=AUTHOR_YA_HEADERS):
    if endpoint_url == ENDPOINT_URL:
        return data
    if headers == AUTHOR_YA_HEADERS:
        return {**data, **CHANGELOG_AUTHOR}
    return {**data, **CHANGELOG_AUTHOR_YA_TEAM}


def build_headers(endpoint_url, headers=AUTHOR_YA_HEADERS, token=None):
    if endpoint_url == ENDPOINT_URL:
        return {**headers, **get_idempotency_header(token)}
    return get_idempotency_header(token)


NEWDRIVER1_LICENSE = '123412345678'
NEWDRIVER1_EMAIL = 'asd@asd.ru'
NEWDRIVER1_PHONES = ['+79217652331', '+89031234567']

NEWDRIVER1 = {
    'accounts': [{'balance_limit': '50.0000', 'type': 'current'}],
    'driver_profile': {
        'first_name': 'Андрей',
        'middle_name': 'Алексеевич',
        'last_name': 'Мироненко',
        'phones': NEWDRIVER1_PHONES,
        'email': NEWDRIVER1_EMAIL,
        'address': 'Мск',
        'deaf': True,
        'balance_deny_onlycard': True,
        'driver_license': {
            'country': 'rus',
            'number': NEWDRIVER1_LICENSE,
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
        'work_status': 'working',  # should be ignored
        'work_rule_id': 'rule_zero',
        'providers': ['yandex', 'park'],
        'hire_date': '2018-11-20',
        'hiring_source': 'selfreg',
        'car_id': '12345',
        'comment': 'ads',
        'check_message': 'qwe',
        'payment_service_id': '123456',
        'permit_number': 'new_permit_number',
        'profession_id': 'taxi/driver',
    },
}

MONGO_DRIVER1 = {
    'park_id': PARK_ID,
    'first_name': 'Андрей',
    'middle_name': 'Алексеевич',
    'last_name': 'Мироненко',
    'phone_pd_ids': list(map(lambda x: 'id_' + x, NEWDRIVER1_PHONES)),
    'email': NEWDRIVER1_EMAIL,
    'email_pd_id': 'id_' + NEWDRIVER1_EMAIL,
    'address': 'Мск',
    'deaf': True,
    'balance_deny_onlycard': True,
    'license_country': 'rus',
    'license_number': NEWDRIVER1_LICENSE,
    'license': NEWDRIVER1_LICENSE,
    'license_normalized': NEWDRIVER1_LICENSE,
    'driver_license_pd_id': 'id_' + NEWDRIVER1_LICENSE,
    'license_driver_birth_date': '1939-09-01T00:00:00+0000',
    'license_expire_date': '2028-11-20T00:00:00+0000',
    'license_issue_date': '2018-11-20T00:00:00+0000',
    'work_status': 'working',
    'rule_id': 'rule_zero',
    'providers': ['yandex', 'park'],
    'balance_limit': 50,
    'hire_date': '2018-11-20T00:00:00+0000',
    'hiring_source': 'selfreg',
    'car_id': '12345',
    'comment': 'ads',
    'check_message': 'qwe',
    'password': '123456',
    'orders_provider': {
        'cargo': False,
        'eda': False,
        'lavka': False,
        'taxi': True,
        'taxi_walking_courier': False,
        'retail': False,
    },
    'permit_number': 'new_permit_number',
}

CHANGELOG_AUTHOR = {
    'author': {
        'consumer': 'some_service_name',
        'identity': {
            'client_ip': '1.2.3.4',
            'id': '11',
            'type': 'passport_user',
        },
    },
}

CHANGELOG_AUTHOR_YA_TEAM = {
    'author': {
        'consumer': 'some_service_name',
        'identity': {
            'client_ip': '1.2.3.4',
            'id': '11',
            'type': 'passport_yandex_team',
        },
    },
}

CHANGELOG_AUTHOR_PLATFORM = {
    'author': {
        'consumer': 'some_service_name',
        'identity': {'type': 'unknown_author'},
    },
}

CHANGELOG_PARAMS = [
    (PARK_ID, {}, {}),
    (PARK_ID, {}, {}),
    (
        PARK_ID,
        {
            'driver_profile': {
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Ms k',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18',
                        'expire_date': '2028-12-18',
                    },
                ],
                'tax_identification_number': '777',
                'emergency_person_contacts': [
                    {'phone': '+79102923118'},
                    {'phone': '+79611012472'},
                ],
                'license_experience': {'total_since': '2018-12-27'},
                'primary_state_registration_number': '123',
                'bank_accounts': [
                    {
                        'russian_central_bank_identifier_code': 'w345',
                        'correspondent_account': 'w4234',
                        'client_account': 'w12',
                    },
                ],
                'platform_uid': 'driver_platform_uid_1',
            },
        },
        {
            'identification_pd_ids': {'current': '["id_100500"]', 'old': ''},
            'emergency_person_contacts': {
                'current': (
                    '[{"phone_pd_id":"id_+79102923118"},'
                    '{"phone_pd_id":"id_+79611012472"}]'
                ),
                'old': '',
            },
            'tax_identification_number_pd_id': {
                'current': 'id_777',
                'old': '',
            },
            'license_experience': {
                'old': '',
                'current': '{"total":"2018-12-27T00:00:00+0000"}',
            },
            'primary_state_registration_number': {'current': '123', 'old': ''},
            'bank_accounts': {
                'current': (
                    '[{"client_account":"w12",'
                    '"correspondent_account":"w4234",'
                    '"russian_central_bank_identifier_code":'
                    '"w345"}]'
                ),
                'old': '',
            },
        },
    ),
    # Romania fields test
    (
        '322',
        {
            'driver_profile': {
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'address': 'Ms k',
                        'postal_code': '123a12',
                        'issuer_country': 'rus',
                        'issuer_organization': 'UVD 23',
                        'issue_date': '2018-12-18',
                        'expire_date': '2028-12-18',
                    },
                ],
                'tax_identification_number': '777',
                'professional_certificate_expiration_date': '2019-12-27',
                'road_penalties_record_issue_date': '2019-12-27',
                'background_criminal_record_issue_date': '2019-10-01',
                'primary_state_registration_number': '123',
            },
        },
        {
            'ParkId': {'current': '322', 'old': ''},
            'professional_certificate_expiration_date': {
                'current': '2019-12-27T00:00:00+0000',
                'old': '',
            },
            'road_penalties_record_issue_date': {
                'current': '2019-12-27T00:00:00+0000',
                'old': '',
            },
            'background_criminal_record_issue_date': {
                'current': '2019-10-01T00:00:00+0000',
                'old': '',
            },
            'identification_pd_ids': {'current': '["id_100500"]', 'old': ''},
            'tax_identification_number_pd_id': {
                'current': 'id_777',
                'old': '',
            },
            'primary_state_registration_number': {'current': '123', 'old': ''},
        },
    ),
]


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        request.get_data()  # to save request
        return {}

    return mock_callback


OK_PARAMS = [
    (
        PARK_ID,
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
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    (
        PARK_ID,
        {'driver_profile': {'tax_identification_number': '123'}},
        {'tax_identification_number_pd_id': 'id_123'},
        {},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 1,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    (
        PARK_ID,
        {
            'driver_profile': {
                'emergency_person_contacts': [
                    {'phone': '+79102923118'},
                    {'phone': '+79611012472'},
                ],
            },
        },
        {
            'emergency_person_contacts': [
                {'phone_pd_id': 'id_+79102923118'},
                {'phone_pd_id': 'id_+79611012472'},
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
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    (
        PARK_ID,
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
                        'issue_date': '2018-12-18',
                        'expire_date': '2028-12-18',
                    },
                ],
            },
        },
        {'identification_pd_ids': ['id_100500']},
        {},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
                'balance_deny_onlycard': True,
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
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    (
        PARK_ID,
        {
            'driver_profile': {
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
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    (
        PARK_ID,
        {
            'driver_profile': {
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'issuer_country': 'rus',
                        'issue_date': '2018-12-18',
                    },
                ],
            },
        },
        {'identification_pd_ids': ['id_100500']},
        {},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
                'identifications': [
                    {
                        'type': 'national',
                        'number': '100500',
                        'issuer_country': 'rus',
                        'issue_date': '2018-12-18T00:00:00+0000',
                    },
                ],
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 1,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    (
        PARK_ID,
        {
            'driver_profile': {
                'emergency_person_contacts': [
                    {'phone': '+79102923118'},
                    {'phone': '+79611012472'},
                ],
            },
        },
        {
            'emergency_person_contacts': [
                {'phone_pd_id': 'id_+79102923118'},
                {'phone_pd_id': 'id_+79611012472'},
            ],
        },
        {'driver_profile': {'phones'}},
        {'phone_pd_ids'},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # test optional driver birth date
    (
        PARK_ID,
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
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # Romania fields tests
    (
        '322',
        {
            'driver_profile': {
                'professional_certificate_expiration_date': '2019-12-27',
                'road_penalties_record_issue_date': '2019-12-27',
                'background_criminal_record_issue_date': '2019-10-01',
            },
        },
        {
            'park_id': '322',
            'professional_certificate_expiration_date': (
                '2019-12-27T00:00:00+0000'
            ),
            'road_penalties_record_issue_date': '2019-12-27T00:00:00+0000',
            'background_criminal_record_issue_date': (
                '2019-10-01T00:00:00+0000'
            ),
        },
        {},
        {},
        {
            'driver_profile': {
                'professional_certificate_expiration_date': (
                    '2019-12-27T00:00:00+0000'
                ),
                'road_penalties_record_issue_date': '2019-12-27T00:00:00+0000',
                'background_criminal_record_issue_date': (
                    '2019-10-01T00:00:00+0000'
                ),
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # couriers
    (
        'couriers_park',
        {'driver_profile': {'phones': ['+7003']}},
        {'park_id': 'couriers_park', 'phone_pd_ids': ['id_+7003']},
        {},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # license_experience field
    (
        '322',
        {
            'driver_profile': {
                'license_experience': {'total_since': '2017-12-27'},
            },
        },
        {
            'park_id': '322',
            'license_experience': {'total': '2017-12-27T00:00:00+0000'},
        },
        {},
        {},
        {
            'driver_profile': {
                'license_experience': {'total_since': '2017-12-27'},
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # sex field test
    (
        '322',
        {'driver_profile': {'sex': 'male'}},
        {'park_id': '322', 'sex': 'male'},
        {},
        {},
        {
            'driver_profile': {
                'sex': 'male',
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # optional work rule test
    (
        '322',
        {
            'driver_profile': {
                'providers': [],
                'balance_deny_onlycard': False,
            },
            'accounts': [{'balance_limit': '0.0000', 'type': 'current'}],
        },
        {
            'park_id': '322',
            'providers': [],
            'balance_deny_onlycard': False,
            'balance_limit': 0,
        },
        {'driver_profile': 'work_rule_id'},
        'rule_id',
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # test platform_uid
    (
        '322',
        {'driver_profile': {'platform_uid': 'driver1_test_uid'}},
        {'park_id': '322', 'platform_uid': 'driver1_test_uid'},
        {},
        {},
        {
            'driver_profile': {
                'platform_uid': 'driver1_test_uid',
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 1,
            'contractor_profession_initialize': 1,
        },
    ),
    # test no profession
    (
        PARK_ID,
        {},
        {},
        {'driver_profile': ['profession_id']},
        {},
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
            },
        },
        {
            'driver_licenses': 1,
            'emails': 1,
            'identifications': 0,
            'phones': 1,
            'tins': 0,
            'phones_find': 1,
            'contractor_profession_validate': 0,
            'contractor_profession_initialize': 0,
        },
    ),
]


@pytest.mark.now('2019-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'park_id, extra_fields, extra_db_fields, '
    'remove_fields, remove_db_fields,'
    'response_replacement, mock_call_times',
    OK_PARAMS,
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_post_ok(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        db,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        personal_phones_bulk_find,
        park_id,
        extra_fields,
        extra_db_fields,
        remove_fields,
        remove_db_fields,
        response_replacement,
        mock_call_times,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    request_driver = utils.remove(
        utils.replace(NEWDRIVER1, extra_fields), remove_fields,
    )
    expected_in_mongo = utils.remove(
        utils.replace(MONGO_DRIVER1, extra_db_fields), remove_db_fields,
    )
    idempotency_token = uuid.uuid1().hex

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': park_id},
        data=json.dumps(build_data(endpoint_url, request_driver)),
        headers=build_headers(
            endpoint_url, AUTHOR_YA_HEADERS, idempotency_token,
        ),
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

    assert personal_phones_bulk_find.times_called == (
        mock_call_times['phones_find']
    )

    assert contractor_profession.validate.times_called == (
        mock_call_times['contractor_profession_validate']
    )
    assert contractor_profession.initialize.times_called == (
        mock_call_times['contractor_profession_initialize']
    )

    driver_in_mongo = utils.datetime_to_str(
        get_driver(db, park_id, '123412345678'),
    )
    assert driver_in_mongo.pop('_id', None) is not None
    assert driver_in_mongo.pop('updated_ts', None) is not None
    assert driver_in_mongo.pop('created_date', None) is not None
    assert driver_in_mongo.pop('modified_date', None) is not None
    assert driver_in_mongo.pop('driver_id', None) is not None
    assert driver_in_mongo.pop('idempotency_token', None) == idempotency_token
    assert driver_in_mongo == expected_in_mongo

    expected_response = copy.deepcopy(request_driver)
    expected_response['driver_profile']['park_id'] = park_id
    expected_response['driver_profile'].pop('profession_id', None)
    response_to_check = response.json()
    assert response_to_check['driver_profile'].pop('id') is not None
    assert response_to_check['accounts'][0].pop('id') is not None
    add_license(expected_response['driver_profile'])
    # we don't want to change format of returned dates right now
    expected_response = utils.replace(expected_response, response_replacement)
    assert response_to_check == expected_response


@pytest.mark.config(
    CONTRACTOR_PROFESSIONS_ORDERS_PROVIDERS_LIST=[
        'cargo',
        'eda',
        'lavka',
        'taxi',
        'taxi_walking_courier',
        'retail',
    ],
)
@pytest.mark.parametrize('courier_app', [None, 'taximeter'])
@pytest.mark.parametrize('phone', ['+7001', '+7005'])
@pytest.mark.parametrize(
    'courier_type,current_provider,orders_provider,expected_code',
    [
        (
            'walking_courier',
            'eda',
            (
                ('cargo', False),
                ('eda', True),
                ('lavka', False),
                ('taxi', False),
                ('taxi_walking_courier', False),
                ('retail', False),
            ),
            200,
        ),
        (
            'walking_courier',
            'lavka',
            (
                ('cargo', False),
                ('eda', False),
                ('lavka', True),
                ('taxi', False),
                ('taxi_walking_courier', False),
                ('retail', False),
            ),
            200,
        ),
        (
            'walking_courier',
            'taxi',
            (
                ('cargo', False),
                ('eda', False),
                ('lavka', False),
                ('taxi', True),
                ('taxi_walking_courier', False),
                ('retail', False),
            ),
            200,
        ),
        (
            'walking_courier',
            'walking_courier',
            (
                ('cargo', False),
                ('eda', False),
                ('lavka', False),
                ('taxi', False),
                ('taxi_walking_courier', True),
                ('retail', False),
            ),
            200,
        ),
        (
            '',
            'cargo',
            (
                ('cargo', True),
                ('eda', False),
                ('lavka', False),
                ('taxi', False),
                ('taxi_walking_courier', False),
                ('retail', False),
            ),
            400,
        ),
        (
            '',
            'retail',
            (
                ('eda', False),
                ('lavka', False),
                ('taxi', False),
                ('taxi_walking_courier', False),
                ('cargo', False),
                ('retail', True),
            ),
            400,
        ),
        (
            'walking_courier',
            None,
            (
                ('eda', False),
                ('lavka', False),
                ('taxi', False),
                ('taxi_walking_courier', True),
                ('cargo', False),
                ('retail', False),
            ),
            200,
        ),
        (
            '',
            None,
            (
                ('cargo', False),
                ('eda', False),
                ('lavka', False),
                ('taxi', True),
                ('taxi_walking_courier', False),
                ('retail', False),
            ),
            400,
        ),
    ],
)
@pytest.mark.now('2019-10-10T11:30:00+0300')
def test_courier_create_ok(
        taxi_parks,
        db,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        phone,
        courier_type,
        courier_app,
        current_provider,
        orders_provider,
        expected_code,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    courier_park = 'couriers_park'
    courier_driver_license = 'COURIER' + phone.replace('+', '')
    request_driver = utils.replace(
        NEWDRIVER1,
        {
            'driver_profile': {
                'courier_type': courier_type,
                'driver_license': {
                    'country': 'rus',
                    'number': courier_driver_license,
                },
                'phones': [phone],
                'external_ids': {
                    'eats': 'eats_courier_id',
                    'market': 'market_id',
                    'uslugi': 'uslugi_id',
                },
            },
        },
    )
    if courier_app:
        request_driver['driver_profile']['courier_app'] = courier_app
    if current_provider:
        request_driver['driver_profile']['orders_provider'] = current_provider

    idempotency_token = uuid.uuid1().hex

    response = taxi_parks.post(
        ENDPOINT_INTERNAL_URL,
        params={'park_id': courier_park},
        data=json.dumps(build_data(ENDPOINT_INTERNAL_URL, request_driver)),
        headers=build_headers(
            ENDPOINT_INTERNAL_URL, AUTHOR_YA_HEADERS, idempotency_token,
        ),
    )

    assert response.status_code == expected_code, response.text

    if response.status_code == 200:
        driver_in_mongo = utils.datetime_to_str(
            get_driver(db, courier_park, courier_driver_license),
        )
        assert driver_in_mongo['courier_type'] == courier_type
        assert driver_in_mongo['license_number'] == courier_driver_license
        assert driver_in_mongo['phone_pd_ids'] == ['id_' + phone]
        assert driver_in_mongo['orders_provider'] == dict(orders_provider)
        assert driver_in_mongo['external_ids'] == {
            'eats': 'eats_courier_id',
            'market': 'market_id',
            'uslugi': 'uslugi_id',
        }
        if courier_app:
            assert driver_in_mongo['courier_app'] == courier_app
        else:
            assert 'courier_app' not in driver_in_mongo

        assert 'courier_type' not in response.json()['driver_profile']
        assert 'orders_provider' not in response.json()['driver_profile']


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_post_random_payment_service_id(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        db,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    new_driver = utils.remove(
        NEWDRIVER1, {'driver_profile': ['payment_service_id', 'phones']},
    )
    new_driver = utils.replace(
        new_driver,
        {'driver_profile': {'driver_license': {'number': '123401234567'}}},
    )

    expected_driver_in_mongo = utils.replace(
        utils.remove(MONGO_DRIVER1, ['password', 'phone_pd_ids', 'phones']),
        {
            'license_number': '123401234567',
            'license': '123401234567',
            'license_normalized': '123401234567',
            'driver_license_pd_id': 'id_123401234567',
        },
    )

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, new_driver)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 200, response.text

    driver_in_mongo = utils.datetime_to_str(
        get_driver(db, PARK_ID, '123401234567'),
    )
    assert driver_in_mongo.pop('_id', None) is not None
    assert driver_in_mongo.pop('updated_ts', None) is not None
    assert driver_in_mongo.pop('created_date', None) is not None
    assert driver_in_mongo.pop('modified_date', None) is not None
    assert driver_in_mongo.pop('driver_id', None) is not None
    assert driver_in_mongo.pop('password', None) is not None
    assert driver_in_mongo.pop('idempotency_token', None) is not None
    assert driver_in_mongo == expected_driver_in_mongo

    expected_response = copy.deepcopy(new_driver)
    expected_response['driver_profile']['park_id'] = PARK_ID
    response_to_check = response.json()
    assert response_to_check['driver_profile'].pop('id', None) is not None
    assert response_to_check['accounts'][0].pop('id', None) is not None
    assert (
        response_to_check['driver_profile'].pop('payment_service_id', None)
        is not None
    )
    add_license(expected_response['driver_profile'])
    # we don't want to change return values format right now
    expected_response['driver_profile'].pop('profession_id', None)
    expected_response = utils.replace(
        expected_response,
        {
            'driver_profile': {
                'driver_license': {
                    'birth_date': '1939-09-01T00:00:00+0000',
                    'expiration_date': '2028-11-20T00:00:00+0000',
                    'issue_date': '2018-11-20T00:00:00+0000',
                },
                'hire_date': '2018-11-20T00:00:00+0000',
                'phones': [],
            },
        },
    )
    assert response_to_check == expected_response


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid_request(taxi_parks, endpoint_url):
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(
            utils.replace(
                build_data(endpoint_url),
                {
                    'driver_profile': {
                        'driver_license': {
                            'birth_date': '1939-09-01T00:00:00+0000',
                        },
                    },
                },
            ),
        ),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'driver_profile.driver_license.birth_date must be date '
        'without time zone in ISO 8601 format, like 2018-12-31',
    )


@pytest.mark.now('2019-12-27T11:30:00+0300')
@pytest.mark.parametrize(
    ['park_id', 'replacement', 'remove', 'error_message'],
    [
        (
            PARK_ID,
            {'driver_profile': {'phones': ['+700', '+1000']}},
            [],
            'duplicate_phone',
        ),
        (
            PARK_ID,
            {'driver_profile': {'driver_license': {'number': '123412345DUP'}}},
            [],
            'duplicate_driver_license',
        ),
        (
            PARK_ID,
            {'driver_profile': {'payment_service_id': '999999'}},
            [],
            'duplicate_payment_service_id',
        ),
        (
            PARK_ID,
            {'driver_profile': {'phones': ['+7123', '81123']}},
            [],
            'invalid_phone',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'emergency_person_contacts': [{'phone': '123123'}],
                },
            },
            [],
            'invalid_emergency_person_contact',
        ),
        (
            PARK_ID,
            {'driver_profile': {'phones': ['+7123456789123456']}},
            [],
            'invalid_phone',
        ),
        (
            PARK_ID,
            {'driver_profile': {'email': 'asd@asd'}},
            [],
            'invalid_email',
        ),
        (
            PARK_ID,
            {'driver_profile': {'email': 'a5469700013493448@asd.ru'}},
            [],
            'payment_card_number_in_email',
        ),
        (
            PARK_ID,
            {'driver_profile': {'address': '5469700013493448'}},
            [],
            'payment_card_number_in_address',
        ),
        (
            PARK_ID,
            {'driver_profile': {'comment': '5469700013493448'}},
            [],
            'payment_card_number_in_comment',
        ),
        (
            PARK_ID,
            {'driver_profile': {'check_message': '5469700013493448'}},
            [],
            'payment_card_number_in_check_message',
        ),
        (PARK_ID, {'driver_profile': {'car_id': '0'}}, [], 'no_such_car'),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'passport',
                            'number': '123',
                            'issuer_country': 'R S',
                            'issue_date': '2018-11-11',
                        },
                    ],
                },
            },
            [],
            'unsupported_identification_country',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'passport',
                            'number': '123',
                            'issuer_country': 'U.K',
                            'issue_date': '2018-11-11',
                        },
                    ],
                },
            },
            [],
            'unsupported_identification_country',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'passport',
                            'number': '123',
                            'issuer_country': 'msk',
                            'issue_date': '2018-11-11',
                        },
                    ],
                },
            },
            [],
            'unsupported_identification_country',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'passport',
                            'number': '123' * 166,
                            'issuer_country': 'rus',
                            'issue_date': '2018-11-11',
                        },
                    ],
                },
            },
            [],
            'too_long_identification',
        ),
        (
            PARK_ID,
            {'driver_profile': {'tax_identification_number': 'asd'}},
            [],
            'invalid_tax_identification_number',
        ),
        (
            PARK_ID,
            {'driver_profile': {'hiring_source': 'asd'}},
            [],
            'invalid_hiring_source',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'license_experience': {'total_since': '2020-01-20'},
                },
            },
            [],
            'invalid_license_experience_total_since',
        ),
        # Romania fields tests
        (
            PARK_ID,
            {
                'driver_profile': {
                    'professional_certificate_expiration_date': '2019-01-01',
                },
            },
            [],
            'unexpected_professional_certificate_expiration_date',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'road_penalties_record_issue_date': '2019-12-26',
                },
            },
            [],
            'unexpected_road_penalties_record_issue_date',
        ),
        (
            '322',
            {
                'driver_profile': {
                    'road_penalties_record_issue_date': '2018-12-26',
                },
            },
            [],
            'expired_road_penalties_record_issue_date',
        ),
        (
            PARK_ID,
            {
                'driver_profile': {
                    'background_criminal_record_issue_date': '2019-12-26',
                },
            },
            [],
            'unexpected_background_criminal_record_issue_date',
        ),
        (
            '322',
            {
                'driver_profile': {
                    'background_criminal_record_issue_date': '2018-12-27',
                },
            },
            [],
            'expired_background_criminal_record_issue_date',
        ),
        # couriers
        (
            'couriers_park',
            {'driver_profile': {'phones': ['+7001']}},
            [],
            'duplicate_phone',
        ),
        (
            'couriers_park',
            {'driver_profile': {'courier_type': 'foot', 'phones': ['+7002']}},
            [],
            'duplicate_phone',
        ),
        (
            'couriers_park',
            {'driver_profile': {'courier_type': 'foot', 'phones': ['+7004']}},
            [],
            'duplicate_phone',
        ),
        # optional rule_id
        # balance_deny_onlycard true
        (
            PARK_ID,
            {
                'driver_profile': {
                    'providers': [],
                    'balance_deny_onlycard': True,
                },
                'accounts': [{'balance_limit': '0.0000', 'type': 'current'}],
            },
            [{'driver_profile': 'work_rule_id'}],
            'absent_work_rule_id_bad_conditions',
        ),
        # providers not empty
        (
            PARK_ID,
            {
                'driver_profile': {
                    'providers': ['yandex'],
                    'balance_deny_onlycard': False,
                },
                'accounts': [{'balance_limit': '0.0000', 'type': 'current'}],
            },
            [{'driver_profile': 'work_rule_id'}],
            'absent_work_rule_id_bad_conditions',
        ),
        # balance_limit != 0
        (
            PARK_ID,
            {
                'driver_profile': {
                    'providers': [],
                    'balance_deny_onlycard': False,
                },
                'accounts': [{'balance_limit': '1.0000', 'type': 'current'}],
            },
            [{'driver_profile': 'work_rule_id'}],
            'absent_work_rule_id_bad_conditions',
        ),
        # platform_uid duplicate
        (
            '322',
            {'driver_profile': {'platform_uid': 'duplicate_test_uid'}},
            [],
            'duplicate_platform_uid',
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid_with_code(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        park_id,
        replacement,
        remove,
        error_message,
        endpoint_url,
        driver_work_rules,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': park_id},
        data=json.dumps(
            utils.remove(
                utils.replace(build_data(endpoint_url), replacement), remove,
            ),
        ),
        headers=build_headers(endpoint_url),
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
def test_forbidden_license_experiment(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        endpoint_url,
        driver_work_rules,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(
            utils.replace(
                build_data(endpoint_url),
                {
                    'driver_profile': {
                        'driver_license': {'number': '123412345FRB'},
                    },
                },
            ),
        ),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'forbidden_driver_license', 'forbidden_driver_license',
    )


@pytest.mark.parametrize(
    'replacement, error_message',
    [
        (
            {'driver_profile': {'phones': ['Q' * 501]}},
            'driver_profile.phones[0] must be an utf-8 string without BOM'
            ' with length >= 1 and <= 500',
        ),
        (
            {'driver_profile': {'address': 'Z' * 501}},
            'driver_profile.address must be an utf-8 string without BOM'
            ' with length <= 500',
        ),
        (
            {'driver_profile': {'identifications': [{}] * 33}},
            'driver_profile.identifications'
            ' must not contain more than 32 identifications',
        ),
        (
            {'driver_profile': {'phones': [f'+7{x}' for x in range(0, 33)]}},
            'driver_profile.phones must not contain more than 32 phones',
        ),
        (
            {'driver_profile': {'bank_accounts': [{}] * 101}},
            'driver_profile.bank_accounts'
            ' must not contain more than 100 bank accounts',
        ),
        (
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'number': '100500',
                            'issuer_country': 'rus',
                            'issue_date': '2018-12-18',
                        },
                    ],
                },
            },
            'driver_profile.identifications[0].type must be present',
        ),
        (
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'national',
                            'issuer_country': 'rus',
                            'issue_date': '2018-12-18',
                        },
                    ],
                },
            },
            'driver_profile.identifications[0].number must be present',
        ),
        (
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'national',
                            'number': '100500',
                            'issue_date': '2018-12-18',
                        },
                    ],
                },
            },
            'driver_profile.identifications[0].issuer_country must be present',
        ),
        (
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'national',
                            'number': '100500',
                            'issuer_country': 'rus',
                        },
                    ],
                },
            },
            'driver_profile.identifications[0].issue_date must be present',
        ),
        (
            {
                'driver_profile': {
                    'bank_accounts': [
                        {
                            'correspondent_account': '432',
                            'client_account': '2018-12-18',
                        },
                    ],
                },
            },
            'driver_profile.bank_accounts[0].'
            'russian_central_bank_identifier_code must be present',
        ),
        (
            {
                'driver_profile': {
                    'bank_accounts': [
                        {
                            'russian_central_bank_identifier_code': '234',
                            'client_account': '2018-12-18',
                        },
                    ],
                },
            },
            'driver_profile.bank_accounts[0].correspondent_account'
            ' must be present',
        ),
        (
            {
                'driver_profile': {
                    'bank_accounts': [
                        {
                            'russian_central_bank_identifier_code': '234',
                            'correspondent_account': '432',
                        },
                    ],
                },
            },
            'driver_profile.bank_accounts[0].client_account'
            ' must be present',
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid(
        taxi_parks, mockserver, replacement, error_message, endpoint_url,
):
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(utils.replace(build_data(endpoint_url), replacement)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_message)


@pytest.mark.parametrize(
    'replacement, error_message',
    [
        (
            {'driver_profile': {'phones': ['\ufeff89823678874']}},
            'driver_profile.phones[0] must be an utf-8 string without BOM'
            ' with length >= 1 and <= 500',
        ),
        (
            {'driver_profile': {'address': 'Mos\ufeffcow'}},
            'driver_profile.address must be an utf-8 string without BOM'
            ' with length <= 500',
        ),
        (
            {'driver_profile': {'address': 'Moscow\ufeff'}},
            'driver_profile.address must be an utf-8 string without BOM'
            ' with length <= 500',
        ),
        (
            {'driver_profile': {'first_name': '\ufeff'}},
            'driver_profile.first_name must be an utf-8 string without BOM'
            ' with length >= 1 and <= 500',
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_wrong_bom_string(
        taxi_parks, mockserver, replacement, error_message, endpoint_url,
):
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': '123'},
        data=json.dumps(utils.replace(build_data(endpoint_url), replacement)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_message)


@pytest.mark.now('2019-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    ['cpm_response', 'request_hiring_type', 'expected_code'],
    [
        (
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial_with_rent',
                'is_warning_expected': True,
            },
            'commercial_with_rent',
            200,
        ),
        (
            {
                'is_restricted': True,
                'available_hiring_type': 'commercial',
                'is_warning_expected': True,
            },
            'commercial',
            200,
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.config(TVM_USER_TICKET_USE_FAKE_CONTEXT=True)
def test_driver_hiring_type_restriction_ok(
        taxi_parks,
        db,
        driver_work_rules,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        personal_tins_bulk_store,
        dispatcher_access_control,
        endpoint_url,
        mockserver,
        contractor_profiles_manager,
        contractor_profession,
        cpm_response,
        request_hiring_type,
        expected_code,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    @mockserver.json_handler(
        '/contractor_profiles_manager/v1/hiring-type-restriction/retrieve',
    )
    def mock_cpm_callback(request):
        return mockserver.make_response(json.dumps(cpm_response), 200)

    idempotency_token = uuid.uuid1().hex
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url)),
        headers=build_headers(
            endpoint_url, AUTHOR_YA_HEADERS, idempotency_token,
        ),
    )

    assert response.status_code == expected_code, response.text
    driver_in_mongo = utils.datetime_to_str(
        get_driver(db, PARK_ID, '123412345678'),
    )

    assert (
        response.json()['driver_profile']['hiring_details']['hiring_type']
        == request_hiring_type
    )
    assert (
        driver_in_mongo['hiring_details']['hiring_type'] == request_hiring_type
    )


@pytest.mark.parametrize(
    'replacement, projection, expected',
    [
        (
            {'driver_profile': {'phones': ['  + 7  ']}},
            {'driver_profile': 'phones'},
            {'driver_profile': {'phones': ['+7']}},
        ),
        (
            {'driver_profile': {'email': ' ASD@QWE.RU '}},
            {'driver_profile': 'email'},
            {'driver_profile': {'email': 'asd@qwe.ru'}},
        ),
        (
            {
                'driver_profile': {
                    'driver_license': {'number': '  1234  1234 - 0aay '},
                },
            },
            {'driver_profile': {'driver_license': 'normalized_number'}},
            {
                'driver_profile': {
                    'driver_license': {'normalized_number': '123412340AAY'},
                },
            },
        ),
        (
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'national',
                            'number': ' 100 500 ',
                            'address': ' Ms k ',
                            'postal_code': ' 123 a12 ',
                            'issuer_country': 'RuS',
                            'issuer_organization': ' UVD 23 ',
                            'issue_date': '2018-12-18',
                            'expire_date': '2028-12-18',
                        },
                    ],
                    'tax_identification_number': '  123 ',
                    'primary_state_registration_number': '1 23 ',
                    'bank_accounts': [
                        {
                            'russian_central_bank_identifier_code': ' w3 45 ',
                            'correspondent_account': ' w4 234 ',
                            'client_account': ' w1 2 ',
                        },
                    ],
                },
            },
            {
                'driver_profile': [
                    'identifications',
                    'tax_identification_number',
                    'primary_state_registration_number',
                    'bank_accounts',
                ],
            },
            {
                'driver_profile': {
                    'identifications': [
                        {
                            'type': 'national',
                            'number': '100500',
                            'address': 'Ms k',
                            'postal_code': '123a12',
                            'issuer_country': 'rus',
                            'issuer_organization': 'UVD 23',
                            'issue_date': '2018-12-18T00:00:00+0000',
                            'expire_date': '2028-12-18T00:00:00+0000',
                        },
                    ],
                    'tax_identification_number': '123',
                    'primary_state_registration_number': '123',
                    'bank_accounts': [
                        {
                            'russian_central_bank_identifier_code': 'w345',
                            'correspondent_account': 'w4234',
                            'client_account': 'w12',
                        },
                    ],
                },
            },
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_normalization(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        personal_phones_bulk_find,
        replacement,
        projection,
        expected,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(utils.replace(build_data(endpoint_url), replacement)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 200, response.text
    assert utils.projection(response.json(), projection) == expected


@pytest.mark.parametrize(
    'replacement, projection, code, expected',
    [
        (
            {
                'driver_profile': {
                    'phones': ['+70001'],
                    'driver_license': {
                        'country': 'rus',
                        'number': '123412340AAA',
                    },
                },
            },
            {'driver_profile': {'driver_license': 'normalized_number'}},
            200,
            {
                'driver_profile': {
                    'driver_license': {'normalized_number': '123412340AAA'},
                },
            },
        ),
        (
            {
                'driver_profile': {
                    'phones': ['+70002'],
                    'driver_license': {'country': 'fra', 'number': '1234'},
                },
            },
            {'driver_profile': {'driver_license': 'normalized_number'}},
            200,
            {
                'driver_profile': {
                    'driver_license': {'normalized_number': '1234'},
                },
            },
        ),
        (
            {
                'driver_profile': {
                    'phones': ['+70003'],
                    'driver_license': {'country': 'kaz', 'number': '12341'},
                },
            },
            {'driver_profile': {'driver_license': 'normalized_number'}},
            200,
            {
                'driver_profile': {
                    'driver_license': {'normalized_number': '12341'},
                },
            },
        ),
        (
            {
                'driver_profile': {
                    'phones': ['+70002'],
                    'driver_license': {'country': 'aze', 'number': '12342'},
                },
            },
            {'driver_profile': {'driver_license': 'normalized_number'}},
            200,
            {
                'driver_profile': {
                    'driver_license': {'normalized_number': '12342'},
                },
            },
        ),
        (
            {
                'driver_profile': {
                    'phones': ['+70001'],
                    'driver_license': {'country': 'rus', 'number': '1234'},
                },
            },
            {'error': ['text', 'code']},
            400,
            error.make_error_response(
                'invalid_driver_license', 'invalid_driver_license',
            ),
        ),
        (
            {
                'driver_profile': {
                    'phones': ['+70001'],
                    'driver_license': {'country': 'qwe'},
                },
            },
            {'error': ['text', 'code']},
            400,
            error.make_error_response(
                'unsupported_driver_license_country',
                'unsupported_driver_license_country',
            ),
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_license_verification(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        replacement,
        projection,
        code,
        expected,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(utils.replace(build_data(endpoint_url), replacement)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == code, response.text
    assert utils.projection(response.json(), projection) == expected


@pytest.mark.parametrize(
    'endpoint_url, projection, code, expected',
    [
        (
            ENDPOINT_URL,
            {'error': ['text', 'code']},
            400,
            error.make_error_response(
                'driver_profile.driver_license country must be present',
            ),
        ),
        (
            ENDPOINT_INTERNAL_URL,
            {'driver_profile': {'driver_license': 'normalized_number'}},
            200,
            {
                'driver_profile': {
                    'driver_license': {'normalized_number': '123412345678'},
                },
            },
        ),
    ],
)
def test_license_verification_no_country(
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
        endpoint_url,
        projection,
        code,
        expected,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    driver = copy.deepcopy(BASE_DRIVER)
    del driver['driver_profile']['driver_license']['country']
    driver['options'] = {'skip_license_validation': True}

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, data=driver)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == code, response.text
    assert utils.projection(response.json(), projection) == expected


def _compare_change_log(
        sql_databases,
        object_id,
        park_id,
        extra_change_log,
        user_id,
        display_name,
        client_ip,
):
    cursor = sql_databases.taximeter.conn.cursor()
    query = 'SELECT * FROM changes_0 WHERE object_id=\'{}\''.format(object_id)
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    change = list(rows[0])
    assert change[0] == park_id
    # skip id and date
    change[8] = json.loads(change[8])
    change[8].pop('DriverId')
    expected_changes = utils.replace(EXPECTED_CHANGE, extra_change_log)
    assert change[3:] == [
        object_id,
        'MongoDB.Docs.Driver.DriverDoc',
        user_id,
        display_name,
        # because of poped DriverId
        len(expected_changes) + 1,
        expected_changes,
        client_ip,
    ]


EXPECTED_CHANGE = {
    'Address': {'current': 'Мск', 'old': ''},
    'BalanceDenyOnlycard': {'current': 'true', 'old': ''},
    'BalanceLimit': {'current': '50.000000', 'old': ''},
    'email_pd_id': {'current': 'id_asd@asd.ru', 'old': ''},
    'driver_license_pd_id': {'current': 'id_123412345678', 'old': ''},
    'phone_pd_ids': {
        'current': '["id_+79217652331","id_+89031234567"]',
        'old': '',
    },
    'CarId': {'current': '12345', 'old': ''},
    'CheckMessage': {'current': 'qwe', 'old': ''},
    'Comment': {'current': 'ads', 'old': ''},
    'Deaf': {'current': 'True', 'old': ''},
    'Email': {'current': 'asd@asd.ru', 'old': ''},
    'FirstName': {'current': 'Андрей', 'old': ''},
    'HireDate': {'current': '2018-11-20T00:00:00+0000', 'old': ''},
    'HiringSource': {'current': 'selfreg', 'old': ''},
    'Car': {'current': 'Audi A6', 'old': ''},
    'LastName': {'current': 'Мироненко', 'old': ''},
    'License': {'current': '123412345678', 'old': ''},
    'LicenseCountryId': {'current': 'rus', 'old': ''},
    'LicenseDriverBirthDate': {
        'current': '1939-09-01T00:00:00+0000',
        'old': '',
    },
    'LicenseExpireDate': {'current': '2028-11-20T00:00:00+0000', 'old': ''},
    'LicenseIssueDate': {'current': '2018-11-20T00:00:00+0000', 'old': ''},
    'LicenseNormalized': {'current': '123412345678', 'old': ''},
    'LicenseNumber': {'current': '123412345678', 'old': ''},
    'MiddleName': {'current': 'Алексеевич', 'old': ''},
    'ParkId': {'current': PARK_ID, 'old': ''},
    'Providers': {'current': '["yandex","park"]', 'old': ''},
    'RuleId': {'current': 'rule_zero', 'old': ''},
    'WorkStatus': {'current': 'Working', 'old': ''},
    'Password': {'current': '123456', 'old': ''},
    'permit_number': {'current': 'new_permit_number', 'old': ''},
}


@pytest.mark.now('2019-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'author, user_id, user_name',
    [
        (AUTHOR_YA_HEADERS, '1', 'Boss'),
        (AUTHOR_YA_TEAM_HEADERS, '', 'Техподдержка'),
    ],
)
@pytest.mark.parametrize(
    'park_id, extra_fields, extra_change_log', CHANGELOG_PARAMS,
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.sql('taximeter', 'SELECT 1')
def test_change_log(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        personal_phones_bulk_find,
        sql_databases,
        park_id,
        extra_fields,
        extra_change_log,
        author,
        user_id,
        user_name,
        endpoint_url,
        driver_work_rules,
        mockserver,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    request_driver = utils.replace(NEWDRIVER1, extra_fields)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': park_id},
        data=json.dumps(build_data(endpoint_url, request_driver, author)),
        headers=build_headers(endpoint_url, author),
    )

    assert response.status_code == 200, response.text

    if author['X-Ya-User-Ticket-Provider'] == 'yandex':
        assert dispatcher_access_control.times_called == 1
        data = dispatcher_access_control.next_call()['request'].get_data()
        assert json.loads(data)['query']['park']['id'] == park_id
    else:
        assert dispatcher_access_control.times_called == 0

    object_id = response.json()['driver_profile']['id']

    _compare_change_log(
        sql_databases=sql_databases,
        object_id=object_id,
        park_id=park_id,
        extra_change_log=extra_change_log,
        user_id=user_id,
        display_name=user_name,
        client_ip='1.2.3.4',
    )


@pytest.mark.now('2019-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'author_headers, user_id, display_name, client_ip',
    CHANGE_LOG_AUTHOR_PARAMS,
)
@pytest.mark.parametrize(
    'park_id, extra_fields, extra_change_log', CHANGELOG_PARAMS,
)
@pytest.mark.sql('taximeter', 'SELECT 1')
def test_change_log_different_authors(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        driver_balance_limit_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        personal_phones_bulk_find,
        sql_databases,
        park_id,
        extra_fields,
        extra_change_log,
        author_headers,
        user_id,
        display_name,
        client_ip,
        driver_work_rules,
        mockserver,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    request_driver = utils.replace(NEWDRIVER1, extra_fields)

    response = taxi_parks.post(
        ENDPOINT_URL,
        params={'park_id': park_id},
        data=json.dumps(build_data(ENDPOINT_URL, request_driver)),
        headers=build_headers(ENDPOINT_URL, author_headers),
    )

    assert response.status_code == 200, response.text

    object_id = response.json()['driver_profile']['id']
    _compare_change_log(
        sql_databases=sql_databases,
        object_id=object_id,
        park_id=park_id,
        extra_change_log=extra_change_log,
        user_id=user_id,
        display_name=display_name,
        client_ip=client_ip,
    )


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_no_yandex_user_in_park1(mockserver, taxi_parks, endpoint_url):
    @mockserver.json_handler(PARKS_USERS_LIST_URL)
    def mock_callback(request):
        return {'users': [], 'offset': 0}

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, NEWDRIVER1)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 1
    assert response.json() == error.make_error_response(
        'can not get change author',
    )


def test_no_yandex_user_in_park2(mockserver, taxi_parks):
    @mockserver.json_handler(PARKS_USERS_LIST_URL)
    def mock_callback(request):
        return {}

    response = taxi_parks.post(
        ENDPOINT_URL,
        params={'park_id': PARK_ID},
        data=json.dumps(NEWDRIVER1),
        headers={'net_hederov': 'polzovatelya', **get_idempotency_header()},
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0
    assert response.json() == error.make_error_response(
        'An author must be provided',
    )


def test_unreal_user_ticket_provider_in_park(mockserver, taxi_parks):
    @mockserver.json_handler(PARKS_USERS_LIST_URL)
    def mock_callback(request):
        return {}

    response = taxi_parks.post(
        ENDPOINT_URL,
        params={'park_id': PARK_ID},
        data=json.dumps(NEWDRIVER1),
        headers=build_headers(ENDPOINT_URL, AUTHOR_YA_UNREAL_HEADERS),
    )

    assert response.status_code == 400
    assert mock_callback.times_called == 0
    assert response.json() == error.make_error_response(
        'can not get change author',
    )


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_driver_updated_trigger(
        taxi_parks,
        mockserver,
        db,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        request.get_data()  # to save request
        return {}

    new_driver = utils.replace(
        NEWDRIVER1,
        {
            'driver_profile': {
                'driver_license': {'number': '000012345678'},
                'phones': ['+70987'],
            },
        },
    )

    expected_notification = utils.replace(
        MONGO_DRIVER1,
        {
            'license_number': '000012345678',
            'license': '000012345678',
            'license_normalized': '000012345678',
            'driver_license_pd_id': 'id_000012345678',
            'phone_pd_ids': ['id_+70987'],
        },
    )

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, new_driver)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    mock_request = mock_callback.next_call()['request']
    assert mock_request.method == 'POST'
    trigger_request = json.loads(mock_request.get_data())
    assert trigger_request['new_driver'].pop('modified_date', None) is not None
    assert trigger_request['new_driver'].pop('updated_ts', None) is not None
    assert trigger_request['new_driver'].pop('created_date', None) is not None
    assert trigger_request['new_driver'].pop('driver_id', None) is not None
    assert (
        trigger_request['new_driver'].pop('idempotency_token', None)
        is not None
    )
    assert trigger_request == {'new_driver': expected_notification}


def get_pd_data(personal):
    data = personal.next_call()['request'].get_data()
    return list(map(lambda item: item['value'], json.loads(data)['items']))


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_data_sent_to_pd_service(
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_identifications_bulk_store,
        personal_phones_bulk_store,
        personal_tins_bulk_store,
        personal_phones_bulk_find,
        taxi_parks,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    tin_data = '123'
    passport_data_1 = {
        'type': 'passport',
        'number': '100500',
        'address': 'Msk',
        'postal_code': '123a12',
        'issuer_country': 'rus',
        'issuer_organization': 'UVD 23',
        'issue_date': '2018-12-18',
        'expire_date': '2028-12-18',
    }
    passport_data_2 = {
        'type': 'passport',
        'number': '4395',
        'address': 'Spb',
        'postal_code': '111a12',
        'issuer_country': 'rus',
        'issuer_organization': 'UVD 13',
        'issue_date': '2018-12-19',
        'expire_date': '2028-12-19',
    }
    request_driver = utils.replace(
        NEWDRIVER1,
        {
            'driver_profile': {
                'tax_identification_number': tin_data,
                'identifications': [passport_data_1, passport_data_2],
            },
        },
    )

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, request_driver)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 200, response.text
    assert dispatcher_access_control.times_called == 1
    assert driver_updated_trigger.times_called == 1

    assert personal_driver_licenses_bulk_store.times_called == 1
    assert personal_emails_bulk_store.times_called == 1
    assert personal_identifications_bulk_store.times_called == 1
    assert personal_phones_bulk_store.times_called == 1
    assert personal_tins_bulk_store.times_called == 1

    assert get_pd_data(personal_driver_licenses_bulk_store) == [
        NEWDRIVER1_LICENSE,
    ]
    assert get_pd_data(personal_emails_bulk_store) == [NEWDRIVER1_EMAIL]
    assert (
        list(
            map(
                lambda x: json.loads(x),
                get_pd_data(personal_identifications_bulk_store),
            ),
        )
        == [
            utils.replace(
                passport_data_1,
                {
                    'issue_date': '2018-12-18T00:00:00+0000',
                    'expire_date': '2028-12-18T00:00:00+0000',
                },
            ),
            utils.replace(
                passport_data_2,
                {
                    'issue_date': '2018-12-19T00:00:00+0000',
                    'expire_date': '2028-12-19T00:00:00+0000',
                },
            ),
        ]
    )
    assert get_pd_data(personal_phones_bulk_store) == NEWDRIVER1_PHONES
    assert get_pd_data(personal_tins_bulk_store) == [tin_data]


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize('pd_error_code', [400, 401, 500])
def test_failed_pd_request(
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        taxi_parks,
        mockserver,
        pd_error_code,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    @mockserver.json_handler('/personal/v1/tins/bulk_store')
    def mock_callback(request):
        return mockserver.make_response('some error', pd_error_code)

    request_driver = utils.replace(
        NEWDRIVER1, {'driver_profile': {'tax_identification_number': '123'}},
    )

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, request_driver)),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 500, response.text


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_driver_idempotent_create(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        db,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        endpoint_url,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    new_driver = utils.remove(
        NEWDRIVER1, {'driver_profile': 'payment_service_id'},
    )

    headers = build_headers(endpoint_url, AUTHOR_YA_HEADERS)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, new_driver)),
        headers=headers,
    )

    assert response.status_code == 200, response.text

    first_json = response.json()
    driver_id = first_json['driver_profile']['id']
    payment_service_id = first_json['driver_profile']['payment_service_id']
    doc = db.dbdrivers.find_one({'driver_id': driver_id})

    # Retry
    other_response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, new_driver)),
        headers=headers,
    )

    assert other_response.status_code == 200, other_response.text
    body = other_response.json()
    assert body['driver_profile']['id'] == driver_id
    assert body['driver_profile']['payment_service_id'] == payment_service_id
    other_doc = db.dbdrivers.find_one({'driver_id': driver_id})
    assert other_doc == doc, doc

    # Even if request changed it must return same driver
    # and same payment id
    new_payment_id = str(int(payment_service_id) + 1)
    new_driver['driver_profile']['payment_service_id'] = new_payment_id
    other_response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, new_driver)),
        headers=headers,
    )

    assert other_response.status_code == 200, other_response.text
    body = other_response.json()
    assert body['driver_profile']['id'] == driver_id
    assert body['driver_profile']['payment_service_id'] == payment_service_id
    other_doc = db.dbdrivers.find_one({'driver_id': driver_id})
    assert other_doc == doc, doc


BAD_IDEMPOTENCY_TOKENS = [None, '', 'abc', 'pretder', ''.join(['a'] * 129)]


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize('idempotency_token', BAD_IDEMPOTENCY_TOKENS)
def test_driver_create_bad_idempotency_token(
        taxi_parks,
        dispatcher_access_control,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        db,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        idempotency_token,
        endpoint_url,
):
    """
    Checks that required X-Idempotency-Token is provided and valid.
    """
    if idempotency_token is not None:
        headers = build_headers(
            endpoint_url, AUTHOR_YA_HEADERS, idempotency_token,
        )
    else:
        headers = AUTHOR_YA_HEADERS

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, NEWDRIVER1)),
        headers=headers,
    )
    assert response.status_code == 400, response.text
    msg_exp = (
        'Header X-Idempotency-Token must contain'
        ' from 8 to 128 ASCII symbols.'
    )
    assert response.json()['error']['text'] == msg_exp


@pytest.mark.sql('taximeter', 'SELECT 1')
def test_driver_create_by_service(
        taxi_parks,
        driver_updated_trigger,
        contractor_profiles_manager,
        contractor_profession,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        sql_databases,
        driver_work_rules,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    response = taxi_parks.post(
        ENDPOINT_INTERNAL_URL,
        params={'park_id': PARK_ID},
        data=json.dumps({**BASE_DRIVER, **CHANGELOG_AUTHOR_PLATFORM}),
        headers=get_idempotency_header(),
    )

    assert response.status_code == 200, response.text

    cursor = sql_databases.taximeter.conn.cursor()
    object_id = response.json()['driver_profile']['id']
    query = 'SELECT * FROM changes_0 WHERE object_id=\'{}\''.format(object_id)
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    change = list(rows[0])
    assert change[0] == '123'
    # skip id and date
    change[8] = json.loads(change[8])
    change[8].pop('DriverId')
    assert change[3] == object_id
    assert change[4] == 'MongoDB.Docs.Driver.DriverDoc'
    assert change[5] == ''
    assert change[6] == 'platform'
    assert change[9] == ''


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_driver_create_pass_driver_profile_id(
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
        contractor_profiles_manager,
        contractor_profession,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        sql_databases,
        driver_work_rules,
        endpoint_url,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    driver_profile_id = 'newdriverprofileid00000000000000'

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID, 'driver_profile_id': driver_profile_id},
        data=json.dumps(build_data(endpoint_url, NEWDRIVER1)),
        headers=build_headers(endpoint_url, AUTHOR_YA_HEADERS),
    )

    assert response.status_code == 200, response.text
    assert response.json()['driver_profile']['id'] == driver_profile_id


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'bad_driver_profile_id',
    ('badid', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrst', '_abobus_'),
)
def test_driver_create_bad_driver_id(
        taxi_parks,
        bad_driver_profile_id,
        dispatcher_access_control,
        driver_updated_trigger,
        contractor_profiles_manager,
        contractor_profession,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        sql_databases,
        driver_work_rules,
        endpoint_url,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)

    response = taxi_parks.post(
        endpoint_url,
        params={
            'park_id': PARK_ID,
            'driver_profile_id': bad_driver_profile_id,
        },
        data=json.dumps(build_data(endpoint_url, NEWDRIVER1)),
        headers=build_headers(endpoint_url, AUTHOR_YA_HEADERS),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'invalid_driver_profile_id', 'invalid_driver_profile_id',
    )


BAD_AUTHOR = {
    'author': {
        'consumer': 'some_service_name',
        'identity': {'client_ip': '1.2.3.4', 'id': '11', 'type': 'error'},
    },
}


def test_bad_author(
        taxi_parks,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
):
    response = taxi_parks.post(
        ENDPOINT_INTERNAL_URL,
        params={'park_id': PARK_ID},
        data=json.dumps({**BASE_DRIVER, **BAD_AUTHOR}),
        headers=get_idempotency_header(),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'error': {'text': 'Invalid type: error'}}


WORK_RULE_ZERO = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'rule_zero',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'park',
}
WORK_RULE_SUPER_1 = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'extra_super_rule_id_1',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'park',
}
WORK_RULE_SUPER_2 = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'extra_super_rule_id_2',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'park',
}
WORK_RULE_SUPER_3 = {
    'commission_for_subvention_percent': '1.2345',
    'commission_for_workshift_percent': '5.4321',
    'id': 'vezet_super_rule_id_3',
    'is_commission_for_orders_cancelled_by_client_' 'enabled': True,
    'is_commission_if_platform_commission_is_null_' 'enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': 'Штатный',
    'subtype': 'selfreg',
    'type': 'vezet',
}

RULES_ONLY_ZERO = {'work_rules': [WORK_RULE_ZERO]}
RULES_WITH_ZERO = {
    'work_rules': [
        WORK_RULE_ZERO,
        WORK_RULE_SUPER_1,
        WORK_RULE_SUPER_2,
        WORK_RULE_SUPER_3,
    ],
}
RULES_NO_ZERO_SINGLE = {'work_rules': [WORK_RULE_SUPER_2]}
RULES_NO_ZERO_MULTY = {'work_rules': [WORK_RULE_SUPER_1, WORK_RULE_SUPER_2]}


# extra_fields, remove_fields, rules_list, response_code, response-text
TEST_WORK_RULES_PARAMS = [
    (
        # 0 absent work_rule_id, empty park list
        {},
        {'driver_profile': 'work_rule_id'},
        {'work_rules': []},
        400,
        {
            'error': {
                'code': 'absent_work_rule_id_bad_conditions',
                'text': 'absent_work_rule_id_bad_conditions',
            },
        },
    ),
    (
        # 1 empty work_rule_id, empty park list
        {'driver_profile': {'work_rule_id': ''}},
        {},
        {'work_rules': []},
        400,
        {
            'error': {
                'text': (
                    'driver_profile.work_rule_id must be an utf-8'
                    ' string without BOM with length >= 1 and <= 500'
                ),
            },
        },
    ),
    (
        # 2 some work_rule_id, empty park list
        {'driver_profile': {'work_rule_id': 'rule_zero'}},
        {},
        {'work_rules': []},
        400,
        {
            'error': {
                'code': 'invalid_work_rule_id',
                'text': 'invalid_work_rule_id',
            },
        },
    ),
    (
        # 3 absent work_rule_id, single element park list
        {},
        {'driver_profile': 'work_rule_id'},
        RULES_ONLY_ZERO,
        400,
        {
            'error': {
                'code': 'absent_work_rule_id_bad_conditions',
                'text': 'absent_work_rule_id_bad_conditions',
            },
        },
    ),
    (
        # 4 empty work_rule_id, single element park list
        {'driver_profile': {'work_rule_id': ''}},
        {},
        RULES_ONLY_ZERO,
        400,
        {
            'error': {
                'text': (
                    'driver_profile.work_rule_id must be an utf-8'
                    ' string without BOM with length >= 1 and <= 500'
                ),
            },
        },
    ),
    (
        # 5 some work_rule_id, single element park list == work_rule_id
        {'driver_profile': {'work_rule_id': 'rule_zero'}},
        {},
        RULES_ONLY_ZERO,
        200,
        {},
    ),
    (
        # 6 some work_rule_id, single element park list != work_rule_id
        {'driver_profile': {'work_rule_id': 'null'}},
        {},
        RULES_ONLY_ZERO,
        400,
        {
            'error': {
                'code': 'invalid_work_rule_id',
                'text': 'invalid_work_rule_id',
            },
        },
    ),
    (
        # 7 absent work_rule_id, multy element park list
        {},
        {'driver_profile': 'work_rule_id'},
        RULES_WITH_ZERO,
        400,
        {
            'error': {
                'code': 'absent_work_rule_id_bad_conditions',
                'text': 'absent_work_rule_id_bad_conditions',
            },
        },
    ),
    (
        # 8 empty work_rule_id, multy element park list
        {'driver_profile': {'work_rule_id': ''}},
        {},
        RULES_WITH_ZERO,
        400,
        {
            'error': {
                'text': (
                    'driver_profile.work_rule_id must be an utf-8'
                    ' string without BOM with length >= 1 and <= 500'
                ),
            },
        },
    ),
    (
        # 9 some work_rule_id, multy element park list inc work_rule_id
        {'driver_profile': {'work_rule_id': 'rule_zero'}},
        {},
        RULES_WITH_ZERO,
        200,
        {},
    ),
    (
        # 10 some work_rule_id, multy element park list exc work_rule_id
        {'driver_profile': {'work_rule_id': 'null'}},
        {},
        RULES_WITH_ZERO,
        400,
        {
            'error': {
                'code': 'invalid_work_rule_id',
                'text': 'invalid_work_rule_id',
            },
        },
    ),
]


@pytest.mark.now('2020-10-01T19:00:00+0300')
@pytest.mark.parametrize(
    'extra_fields, remove_fields, rules_list, response_code, response_json',
    TEST_WORK_RULES_PARAMS,
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_work_rules(
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        extra_fields,
        remove_fields,
        rules_list,
        response_code,
        response_json,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
):
    request_driver = utils.remove(
        utils.replace(NEWDRIVER1, extra_fields), remove_fields,
    )
    idempotency_token = uuid.uuid1().hex

    driver_work_rules.set_work_rules_response(rules_list)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, request_driver)),
        headers=build_headers(
            endpoint_url, AUTHOR_YA_HEADERS, idempotency_token,
        ),
    )

    assert response.status_code == response_code, response.text
    if response_json:
        assert response.json() == response_json


@pytest.mark.now('2020-10-01T19:00:00+0300')
@pytest.mark.parametrize(
    'extra_fields,rules_list,avoid_non_park,response_code,response_json',
    [
        (
            {'driver_profile': {'work_rule_id': 'vezet_super_rule_id_3'}},
            RULES_WITH_ZERO,
            True,
            400,
            {
                'error': {
                    'code': 'invalid_work_rule_id',
                    'text': 'invalid_work_rule_id',
                },
            },
        ),
        (
            {'driver_profile': {'work_rule_id': 'vezet_super_rule_id_3'}},
            RULES_WITH_ZERO,
            False,
            200,
            {},
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_non_park_work_rules(
        taxi_parks,
        dispatcher_access_control,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        extra_fields,
        rules_list,
        avoid_non_park,
        response_code,
        response_json,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
        config,
):
    request_driver = utils.replace(NEWDRIVER1, extra_fields)
    idempotency_token = uuid.uuid1().hex

    config.set_values(
        dict(PARKS_AVOID_NON_PARK_WORK_RULES_ON_PROFILE_CREATE=avoid_non_park),
    )

    driver_work_rules.set_work_rules_response(rules_list)

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, request_driver)),
        headers=build_headers(
            endpoint_url, AUTHOR_YA_HEADERS, idempotency_token,
        ),
    )

    if 'internal' in endpoint_url:
        response_code = 200
        response_json = {}
        assert driver_work_rules.from_master

    assert response.status_code == response_code, response.text
    if response_json:
        assert response.json() == response_json


SIGNALQ_DRIVER1 = {
    'accounts': [{'balance_limit': '0.0000', 'type': 'current'}],
    'driver_profile': {
        'first_name': 'Александр',
        'middle_name': 'Сигналкулович',
        'last_name': 'Камерный',
        'phones': [],
        'driver_license': {
            'country': 'rus',
            'number': '123412345DUP',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
        'work_status': 'working',  # should be ignored
        'providers': [],
        'hire_date': '2018-11-20',
        'payment_service_id': '241299',
        'signalq_details': {'unit': 'West', 'employee_number': '125125'},
    },
}
SIGNALQ_DRIVER2_EXISTING_PHONE = utils.replace(
    SIGNALQ_DRIVER1, {'driver_profile': {'phones': ['+7003']}},
)
SIGNALQ_DRIVER3_EXISTING_EMPLOYEE_NUMBER = utils.replace(
    SIGNALQ_DRIVER1,
    {'driver_profile': {'signalq_details': {'employee_number': '123'}}},
)
SIGNALQ_DRIVER4_EMPTY_LICENSE_NUMBER = utils.remove(
    utils.replace(
        SIGNALQ_DRIVER1,
        {
            'driver_profile': {
                'driver_license': {
                    'number': '',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
        },
    ),
    {'driver_profile': 'driver_license'},
)

MONGO_SIGNALQ_DRIVER1 = {
    'park_id': 'only_signalq_park1',
    'first_name': 'Александр',
    'middle_name': 'Сигналкулович',
    'last_name': 'Камерный',
    'license_country': 'rus',
    'license_number': '123412345DUP',
    'license': '123412345DUP',
    'license_normalized': '123412345DUP',
    'driver_license_pd_id': 'id_' + '123412345DUP',
    'license_expire_date': '2028-11-20T00:00:00+0000',
    'license_issue_date': '2018-11-20T00:00:00+0000',
    'work_status': 'not_working',
    'providers': [],
    'hire_date': '2018-11-20T00:00:00+0000',
    'password': '241299',
    'balance_limit': 0.0,
    'orders_provider': {
        'eda': False,
        'lavka': False,
        'taxi': True,
        'taxi_walking_courier': False,
        'retail': False,
        'cargo': False,
    },
    'signalq_details': {'unit': 'West', 'employee_number': '125125'},
}

MONGO_SIGNALQ_DRIVER_EMPTY_LICENSE_NUMBER = utils.remove(
    MONGO_SIGNALQ_DRIVER1,
    [
        'license_country',
        'driver_license_pd_id',
        'license_expire_date',
        'license_issue_date',
        'license_normalized',
        'license',
        'license_number',
    ],
)
# MONGO_SIGNALQ_DRIVER_EMPTY_LICENSE_NUMBER.pop('license_country')
# MONGO_SIGNALQ_DRIVER_EMPTY_LICENSE_NUMBER.pop('driver_license_pd_id')

DEFAULT_REPLACING_FIELDS = {
    'driver_license': {
        'expiration_date': '2028-11-20T00:00:00+0000',
        'issue_date': '2018-11-20T00:00:00+0000',
    },
    'hire_date': '2018-11-20T00:00:00+0000',
    'work_status': 'not_working',
}


@pytest.mark.now('2020-10-01T19:00:00+0300')
@pytest.mark.parametrize(
    'park_id,driver,replacing_fields,expected_mongo_driver,'
    'response_code,response_json',
    [
        (
            'only_signalq_park1',
            SIGNALQ_DRIVER1,
            {'driver_profile': {**DEFAULT_REPLACING_FIELDS}},
            MONGO_SIGNALQ_DRIVER1,
            200,
            SIGNALQ_DRIVER1,
        ),
        (
            'only_signalq_park1',
            SIGNALQ_DRIVER2_EXISTING_PHONE,
            None,
            None,
            400,
            {'error': {'code': 'duplicate_phone', 'text': 'duplicate_phone'}},
        ),
        (
            'only_signalq_park1',
            SIGNALQ_DRIVER3_EXISTING_EMPLOYEE_NUMBER,
            None,
            None,
            400,
            {
                'error': {
                    'code': 'duplicate_employee_number',
                    'text': 'duplicate_employee_number',
                },
            },
        ),
        (
            'only_signalq_park1',
            SIGNALQ_DRIVER4_EMPTY_LICENSE_NUMBER,
            {
                'driver_profile': {
                    'hire_date': '2018-11-20T00:00:00+0000',
                    'work_status': 'not_working',
                },
            },
            MONGO_SIGNALQ_DRIVER_EMPTY_LICENSE_NUMBER,
            200,
            SIGNALQ_DRIVER4_EMPTY_LICENSE_NUMBER,
        ),
        (
            'taxi_signalq_park1',
            SIGNALQ_DRIVER2_EXISTING_PHONE,
            None,
            None,
            400,
            {'error': {'code': 'duplicate_phone', 'text': 'duplicate_phone'}},
        ),
        (
            '322',
            SIGNALQ_DRIVER1,
            None,
            None,
            400,
            {
                'error': {
                    'code': 'unexpected_signalq_details',
                    'text': 'unexpected_signalq_details',
                },
            },
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_signalq_drivers(
        taxi_parks,
        db,
        dispatcher_access_control,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        personal_phones_bulk_find,
        park_id,
        driver,
        replacing_fields,
        expected_mongo_driver,
        response_code,
        response_json,
        endpoint_url,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
        config,
):
    idempotency_token = uuid.uuid1().hex

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': park_id},
        data=json.dumps(build_data(endpoint_url, driver)),
        headers=build_headers(
            endpoint_url, AUTHOR_YA_HEADERS, idempotency_token,
        ),
    )
    if expected_mongo_driver is None:
        assert response.status_code == 400, response.text
        assert response.json() == response_json
        return

    assert response.status_code == 200, response.text
    assert dispatcher_access_control.times_called == 1
    assert driver_updated_trigger.times_called == 0
    assert personal_phones_bulk_find.times_called == 0

    response_to_check = response.json()
    assert response_to_check['driver_profile'].pop('id') is not None
    assert response_to_check['accounts'][0].pop('id') is not None

    expected_response = copy.deepcopy(driver)
    expected_response['driver_profile']['park_id'] = park_id
    has_license = (
        expected_response['driver_profile'].get('driver_license') is not None
    )
    if has_license:
        add_license(expected_response['driver_profile'])

    expected_response = utils.replace(expected_response, replacing_fields)
    assert response_to_check == expected_response

    driver_in_mongo = utils.datetime_to_str(
        get_driver(
            db,
            park_id,
            expected_response['driver_profile']['driver_license']['number']
            if has_license
            else None,
        ),
    )

    assert driver_in_mongo.pop('_id', None) is not None
    assert driver_in_mongo.pop('updated_ts', None) is not None
    assert driver_in_mongo.pop('created_date', None) is not None
    assert driver_in_mongo.pop('modified_date', None) is not None
    assert driver_in_mongo.pop('driver_id', None) is not None
    assert driver_in_mongo.pop('idempotency_token', None) == idempotency_token
    assert driver_in_mongo == expected_mongo_driver


@pytest.mark.parametrize(
    'hire_date, projection, code, expected',
    [
        (
            '2199-12-31',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1800-02-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1700-01-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '2015-02-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1899-12-31',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '1900-01-01',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '1900-01-01T00:00:00+0000'}},
        ),
        (
            '2011-01-01',
            {'error': ['text']},
            400,
            error.make_error_response('invalid_hire_date'),
        ),
        (
            '2010-12-31',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '2010-12-31T00:00:00+0000'}},
        ),
        (
            '2000-02-01',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '2000-02-01T00:00:00+0000'}},
        ),
        (
            '2000-12-31',
            {'driver_profile': 'hire_date'},
            200,
            {'driver_profile': {'hire_date': '2000-12-31T00:00:00+0000'}},
        ),
    ],
)
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.now('2000-01-01T00:00:00+0000')
def test_valid_hire_date(
        taxi_parks,
        dispatcher_access_control,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        endpoint_url,
        hire_date,
        projection,
        code,
        expected,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)
    driver = copy.deepcopy(NEWDRIVER1)
    driver['driver_profile']['hire_date'] = hire_date
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, data=driver)),
        headers=build_headers(endpoint_url),
    )
    assert response.status_code == code, response.text
    assert utils.projection(response.json(), projection) == expected


def _send_with_balance_limit(
        taxi_parks, driver_work_rules, endpoint_url, balance_limit,
):
    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)
    driver = copy.deepcopy(NEWDRIVER1)
    driver['accounts'][0]['balance_limit'] = balance_limit

    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, data=driver)),
        headers=build_headers(endpoint_url),
    )
    return response


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize('balance_limit', [-1e9 - 1, -1e9, 1e9, 1e9 + 1])
def test_invalid_balance_limit(
        taxi_parks,
        dispatcher_access_control,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        endpoint_url,
        balance_limit,
):
    error_code = 'invalid_balance_limit'
    response = _send_with_balance_limit(
        taxi_parks, driver_work_rules, endpoint_url, str(balance_limit),
    )
    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_code, error_code)


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
@pytest.mark.parametrize(
    'balance_limit, expected_limit',
    [
        (50.11111111, '50.1111'),
        (1e9 - 1, '999999999.0000'),
        (-1e9 + 1, '-999999999.0000'),
        (50, '50.0000'),
        (50.09568123, '50.0957'),
    ],
)
def test_valid_balance_limit(
        taxi_parks,
        dispatcher_access_control,
        driver_work_rules,
        contractor_profiles_manager,
        contractor_profession,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        endpoint_url,
        balance_limit,
        expected_limit,
):
    response = _send_with_balance_limit(
        taxi_parks, driver_work_rules, endpoint_url, str(balance_limit),
    )
    assert response.status_code == 200, response.text
    assert response.json()['accounts'][0]['balance_limit'] == expected_limit


@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid_profession(
        taxi_parks,
        mockserver,
        dispatcher_access_control,
        driver_work_rules,
        contractor_profiles_manager,
        driver_updated_trigger,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        endpoint_url,
):
    @mockserver.json_handler(
        '/contractor_profession/internal/v1/professions/validate',
    )
    def mock_callback(request):
        return mockserver.make_response(
            status=400,
            response=json.dumps(
                {'code': 'BAD_REQUEST', 'message': 'Invalid profession id'},
            ),
        )

    driver_work_rules.set_work_rules_response(RULES_WITH_ZERO)
    driver = copy.deepcopy(NEWDRIVER1)
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(build_data(endpoint_url, data=driver)),
        headers=build_headers(endpoint_url),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'error': {
            'code': 'invalid_profession_id',
            'text': 'invalid_profession_id',
        },
    }


@pytest.mark.parametrize('birth_date', ['0216-09-01', '6210-09-01'])
@pytest.mark.parametrize('endpoint_url', ENDPOINT_URLS)
def test_invalid_request_date(taxi_parks, endpoint_url, birth_date):
    response = taxi_parks.post(
        endpoint_url,
        params={'park_id': PARK_ID},
        data=json.dumps(
            utils.replace(
                build_data(endpoint_url),
                {
                    'driver_profile': {
                        'driver_license': {'birth_date': birth_date},
                    },
                },
            ),
        ),
        headers=build_headers(endpoint_url),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'driver_profile.driver_license.birth_date must be date'
        ' without time zone in ISO 8601 format, like 2018-12-31',
    )
