import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from driver_profiles_plugins.generated_tests import *  # noqa


async def test_app_retrieve(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        '/v1/driver/app/profiles/retrieve',
        json={'id_in_set': ['park4_driver4']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles': [
            {
                'revision': '0_1234567_4',
                'park_driver_profile_id': 'park4_driver4',
                'data': {
                    'taximeter_platform': 'android',
                    'taximeter_version': '9.37 (1003324)',
                    'taximeter_version_type': 'x',
                    'taximeter_brand': 'yandex',
                    'imei': '356145085158411',
                    'device_model': 'LGE LG-H870DS',
                    'network_operator': 'MegaFon',
                    'metrica_uuid': '77ece08f193818617e481da7242eae01',
                    'metrica_device_id': '821875086cef0d9b7a21edef95afa5a3',
                    'locale': 'ru',
                },
            },
        ],
    }


async def test_proxy_retrieve(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/proxy-retrieve',
        params={'consumer': 'test'},
        json={
            'id_in_set': [
                'park1_driver1',
                'park2_driver2',
                'park4_driver4',
                'unknown_driver1',
                'park1_unknown',
            ],
            'projection': ['data.license.pd_id', 'data.is_removed_by_request'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'profiles': [
            {
                'park_driver_profile_id': 'park1_driver1',
                'data': {'license': {'pd_id': 'driver_license_pd_id_1'}},
            },
            {
                'park_driver_profile_id': 'park2_driver2',
                'data': {'license': {'pd_id': 'driver_license_pd_id_2'}},
            },
            {
                'park_driver_profile_id': 'park4_driver4',
                'data': {
                    'is_removed_by_request': False,
                    'license': {'pd_id': 'driver_license_pd_id_4'},
                },
            },
            {'park_driver_profile_id': 'unknown_driver1'},
            {'park_driver_profile_id': 'park1_unknown'},
        ],
    }


async def test_driver_profiles_updates(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/driver/profiles/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_2'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_4',
        'profiles': [
            {
                'revision': '0_1234567_3',
                'park_driver_profile_id': 'park3_driver3',
                'data': {
                    'park_id': 'park3',
                    'car_id': 'car3',
                    'uuid': 'driver3',
                    'hiring_details': {
                        'default_rule_work_date': '1970-01-15T06:56:07.000',
                    },
                    'orders_provider': {'taxi': True},
                    'hire_date': '1970-01-13T06:56:07.000',
                    'fire_date': '1970-01-23T06:56:07.000',
                    'check_message': 'something',
                    'phone_pd_ids': [],
                    'email_pd_ids': [],
                    'last_login_at': '1970-01-15T06:56:07.000',
                },
            },
            {
                'revision': '0_1234567_4',
                'park_driver_profile_id': 'park4_driver4',
                'data': {
                    'park_id': 'park4',
                    'car_id': 'car4',
                    'courier_type': 'walking_courier',
                    'rule_id': 'some_rule_id',
                    'uuid': 'driver4',
                    'license': {'pd_id': 'driver_license_pd_id_4'},
                    'license_driver_birth_date': '1970-01-15T06:56:07.000',
                    'full_name': {
                        'first_name': 'Серей',
                        'middle_name': 'Борович',
                        'last_name': 'Курв',
                    },
                    'hiring_details': {
                        'hiring_type': 'commercial',
                        'hiring_date': '1970-01-15T06:56:07.000',
                    },
                    'hire_date': '1970-01-12T06:56:07.000',
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_4'}],
                    'email_pd_ids': [],
                    'is_removed_by_request': False,
                    'work_status': 'working',
                    'identification_pd_ids': ['some_identification_pd_id'],
                    'last_login_at': '1970-01-15T06:56:07.000',
                },
            },
        ],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(10)
    assert delay_header == delay_value

    response = await taxi_driver_profiles.get(
        'v1/driver/profiles/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_4'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_4',
        'profiles': [],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(10)
    assert delay_header == delay_value
    # no more changes
    response = await taxi_driver_profiles.get(
        'v1/driver/profiles/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_5'},
    )
    assert response.status_code == 429


@pytest.mark.config(
    API_OVER_DATA_SERVICES={
        'driver-profiles': {
            'incremental_merge_time_limit_ms': 5000,
            'max_x_polling_delay_ms': 10,
            'min_x_polling_delay_ms': 0,
            'max_answer_data_size_bytes': 1000,
            'updates_max_documents_count': 2,
            'is_dumper_enabled': False,
            'deleted_documents_ttl_seconds': 0,
        },
    },
)
async def test_driver_profiles_updates_empty_revision(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/driver/profiles/updates', params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_2',
        'profiles': [
            {
                'revision': '0_1234567_1',
                'park_driver_profile_id': 'park1_driver1',
                'data': {
                    'park_id': 'park1',
                    'car_id': 'car1',
                    'delivery': {
                        'thermobag': True,
                        'thermopack': True,
                        'profi_courier': True,
                    },
                    'medical_card': {
                        'is_enabled': True,
                        'issue_date': '1970-01-15T06:56:07.000',
                    },
                    'uuid': 'driver1',
                    'rule_id': '',
                    'license': {
                        'pd_id': 'driver_license_pd_id_1',
                        'country': 'rus',
                        'is_verified': True,
                    },
                    'full_name': {
                        'first_name': 'Дмий',
                        'middle_name': 'Сервич',
                        'last_name': 'Боркий',
                    },
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_1'}],
                    'platform_uid': 'platform_uid_1',
                    'email_pd_ids': [],
                    'last_login_at': '1970-01-15T06:56:07.000',
                },
            },
            {
                'revision': '0_1234567_2',
                'park_driver_profile_id': 'park2_driver2',
                'data': {
                    'park_id': 'park2',
                    'car_id': 'car2',
                    'delivery': {
                        'thermobag': False,
                        'thermopack': False,
                        'profi_courier': False,
                    },
                    'medical_card': {'is_enabled': False},
                    'uuid': 'driver2',
                    'license': {'pd_id': 'driver_license_pd_id_2'},
                    'full_name': {
                        'first_name': 'Анатой',
                        'middle_name': 'Аольевич',
                        'last_name': 'Зов',
                    },
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_2'}],
                    'email_pd_ids': [],
                    'last_login_at': '1970-01-15T06:56:07.000',
                },
            },
        ],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(0)
    assert delay_header == delay_value


async def test_driver_profiles_updates_no_consumer(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/driver/profiles/updates', params={},
    )
    assert response.status_code == 400


async def test_driver_profiles_retrieve(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve',
        json={'id_in_set': ['park4_driver4', 'no_id']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles': [
            {
                'revision': '0_1234567_4',
                'park_driver_profile_id': 'park4_driver4',
                'data': {
                    'park_id': 'park4',
                    'car_id': 'car4',
                    'courier_type': 'walking_courier',
                    'uuid': 'driver4',
                    'rule_id': 'some_rule_id',
                    'license': {'pd_id': 'driver_license_pd_id_4'},
                    'license_driver_birth_date': '1970-01-15T06:56:07.000',
                    'full_name': {
                        'first_name': 'Серей',
                        'middle_name': 'Борович',
                        'last_name': 'Курв',
                    },
                    'hiring_details': {
                        'hiring_type': 'commercial',
                        'hiring_date': '1970-01-15T06:56:07.000',
                    },
                    'hire_date': '1970-01-12T06:56:07.000',
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_4'}],
                    'email_pd_ids': [],
                    'is_removed_by_request': False,
                    'work_status': 'working',
                    'identification_pd_ids': ['some_identification_pd_id'],
                    'last_login_at': '1970-01-15T06:56:07.000',
                },
            },
            {'park_driver_profile_id': 'no_id'},
        ],
    }


async def test_car_id_retrieve(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/vehicle_bindings/cars/retrieve_by_driver_id',
        json={'id_in_set': ['park4_driver4', 'no_id']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles': [
            {
                'revision': '0_1234567_4',
                'park_driver_profile_id': 'park4_driver4',
                'data': {'car_id': 'car4'},
            },
            {'park_driver_profile_id': 'no_id'},
        ],
    }


async def test_driver_profiles_retrieve_bad_request(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve',
        json={
            # deliberate error in parameter name
            'ids_in_set': ['park4_driver4', 'no_id'],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 400


async def test_driver_profiles_retrieve_by_license(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve_by_license',
        json={'driver_license_in_set': ['driver_license_pd_id_4', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles_by_license': [
            {
                'driver_license': 'driver_license_pd_id_4',
                'profiles': [
                    {
                        'revision': '0_1234567_4',
                        'park_driver_profile_id': 'park4_driver4',
                        'data': {
                            'park_id': 'park4',
                            'car_id': 'car4',
                            'courier_type': 'walking_courier',
                            'uuid': 'driver4',
                            'license': {'pd_id': 'driver_license_pd_id_4'},
                            'license_driver_birth_date': (
                                '1970-01-15T06:56:07.000'
                            ),
                            'full_name': {
                                'first_name': 'Серей',
                                'middle_name': 'Борович',
                                'last_name': 'Курв',
                            },
                            'rule_id': 'some_rule_id',
                            'hiring_details': {
                                'hiring_type': 'commercial',
                                'hiring_date': '1970-01-15T06:56:07.000',
                            },
                            'hire_date': '1970-01-12T06:56:07.000',
                            'phone_pd_ids': [{'pd_id': 'phone_pd_id_4'}],
                            'email_pd_ids': [],
                            'is_removed_by_request': False,
                            'work_status': 'working',
                            'identification_pd_ids': [
                                'some_identification_pd_id',
                            ],
                            'last_login_at': '1970-01-15T06:56:07.000',
                        },
                    },
                ],
            },
            {'driver_license': 'unknown', 'profiles': []},
        ],
    }


async def test_driver_profiles_retrieve_by_license_projection(
        taxi_driver_profiles,
):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve_by_license',
        json={
            'driver_license_in_set': ['driver_license_pd_id_4', 'unknown'],
            'projection': ['data.park_id', 'data.uuid'],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles_by_license': [
            {
                'driver_license': 'driver_license_pd_id_4',
                'profiles': [
                    {
                        'park_driver_profile_id': 'park4_driver4',
                        'data': {'park_id': 'park4', 'uuid': 'driver4'},
                    },
                ],
            },
            {'driver_license': 'unknown', 'profiles': []},
        ],
    }


async def test_driver_profiles_retrieve_by_phone(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve_by_phone',
        json={'driver_phone_in_set': ['phone_pd_id_1', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles_by_phone': [
            {
                'driver_phone': 'phone_pd_id_1',
                'profiles': [
                    {
                        'revision': '0_1234567_1',
                        'park_driver_profile_id': 'park1_driver1',
                        'data': {
                            'park_id': 'park1',
                            'car_id': 'car1',
                            'delivery': {
                                'thermobag': True,
                                'thermopack': True,
                                'profi_courier': True,
                            },
                            'medical_card': {
                                'is_enabled': True,
                                'issue_date': '1970-01-15T06:56:07.000',
                            },
                            'uuid': 'driver1',
                            'license': {
                                'pd_id': 'driver_license_pd_id_1',
                                'country': 'rus',
                                'is_verified': True,
                            },
                            'full_name': {
                                'first_name': 'Дмий',
                                'middle_name': 'Сервич',
                                'last_name': 'Боркий',
                            },
                            'rule_id': '',
                            'phone_pd_ids': [{'pd_id': 'phone_pd_id_1'}],
                            'platform_uid': 'platform_uid_1',
                            'email_pd_ids': [],
                            'last_login_at': '1970-01-15T06:56:07.000',
                        },
                    },
                ],
            },
            {'driver_phone': 'unknown', 'profiles': []},
        ],
    }


async def test_driver_profiles_retrieve_by_platform_uid(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve_by_platform_uid',
        json={'platform_uid_in_set': ['platform_uid_1', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles_by_platform_uid': [
            {
                'platform_uid': 'platform_uid_1',
                'profiles': [
                    {
                        'revision': '0_1234567_1',
                        'park_driver_profile_id': 'park1_driver1',
                        'data': {
                            'park_id': 'park1',
                            'car_id': 'car1',
                            'delivery': {
                                'thermobag': True,
                                'thermopack': True,
                                'profi_courier': True,
                            },
                            'medical_card': {
                                'is_enabled': True,
                                'issue_date': '1970-01-15T06:56:07.000',
                            },
                            'uuid': 'driver1',
                            'license': {
                                'pd_id': 'driver_license_pd_id_1',
                                'country': 'rus',
                                'is_verified': True,
                            },
                            'full_name': {
                                'first_name': 'Дмий',
                                'middle_name': 'Сервич',
                                'last_name': 'Боркий',
                            },
                            'rule_id': '',
                            'phone_pd_ids': [{'pd_id': 'phone_pd_id_1'}],
                            'platform_uid': 'platform_uid_1',
                            'email_pd_ids': [],
                            'last_login_at': '1970-01-15T06:56:07.000',
                        },
                    },
                ],
            },
            {'platform_uid': 'unknown', 'profiles': []},
        ],
    }


async def test_driver_cars_updates(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/vehicle_bindings/cars/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_2'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_4',
        'profiles': [
            {
                'revision': '0_1234567_3',
                'park_driver_profile_id': 'park3_driver3',
                'data': {'car_id': 'car3'},
            },
            {
                'revision': '0_1234567_4',
                'park_driver_profile_id': 'park4_driver4',
                'data': {'car_id': 'car4'},
            },
        ],
    }

    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(10)
    assert delay_header == delay_value

    response = await taxi_driver_profiles.get(
        'v1/vehicle_bindings/cars/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_4'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_4',
        'profiles': [],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(10)
    assert delay_header == delay_value
    # no more changes
    response = await taxi_driver_profiles.get(
        'v1/vehicle_bindings/cars/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_5'},
    )
    assert response.status_code == 429


@pytest.mark.config(
    API_OVER_DATA_SERVICES={
        'driver-profiles': {
            'incremental_merge_time_limit_ms': 5000,
            'max_x_polling_delay_ms': 10,
            'min_x_polling_delay_ms': 0,
            'max_answer_data_size_bytes': 1000,
            'updates_max_documents_count': 2,
            'is_dumper_enabled': False,
            'deleted_documents_ttl_seconds': 0,
        },
    },
)
async def test_driver_cars_updates_empty_revision(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/vehicle_bindings/cars/updates', params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_2',
        'profiles': [
            {
                'revision': '0_1234567_1',
                'park_driver_profile_id': 'park1_driver1',
                'data': {'car_id': 'car1'},
            },
            {
                'revision': '0_1234567_2',
                'park_driver_profile_id': 'park2_driver2',
                'data': {'car_id': 'car2'},
            },
        ],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(0)
    assert delay_header == delay_value


async def test_driver_cars_updates_no_consumer(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/vehicle_bindings/cars/updates', params={},
    )
    assert response.status_code == 400


async def test_driver_profiles_retrieve_by_park_id(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/driver/profiles/retrieve_by_park_id',
        json={'park_id_in_set': ['park1', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'profiles_by_park_id': [
            {
                'park_id': 'park1',
                'profiles': [
                    {
                        'revision': '0_1234567_1',
                        'park_driver_profile_id': 'park1_driver1',
                        'data': {
                            'car_id': 'car1',
                            'park_id': 'park1',
                            'delivery': {
                                'thermobag': True,
                                'thermopack': True,
                                'profi_courier': True,
                            },
                            'medical_card': {
                                'is_enabled': True,
                                'issue_date': '1970-01-15T06:56:07.000',
                            },
                            'uuid': 'driver1',
                            'license': {
                                'pd_id': 'driver_license_pd_id_1',
                                'country': 'rus',
                                'is_verified': True,
                            },
                            'full_name': {
                                'first_name': 'Дмий',
                                'middle_name': 'Сервич',
                                'last_name': 'Боркий',
                            },
                            'rule_id': '',
                            'phone_pd_ids': [{'pd_id': 'phone_pd_id_1'}],
                            'platform_uid': 'platform_uid_1',
                            'email_pd_ids': [],
                            'last_login_at': '1970-01-15T06:56:07.000',
                        },
                    },
                ],
            },
            {'park_id': 'unknown', 'profiles': []},
        ],
    }


async def test_identity_docs_updates(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        'v1/identity-docs/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_2'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_3',
        'docs': [
            {
                'id': '000000000000000000000004',
                'data': {
                    'driver_id': 'driver4',
                    'park_id': 'park4',
                    'type': 'sailor_rus',
                    'data_pd_id': '3cf8370f325540139074632a91ffdffb',
                    'number_pd_id': 'ddab25ffd3b54b9db36183c85394027e',
                },
            },
        ],
    }


async def test_identity_docs_retrieve(taxi_driver_profiles):
    response = await taxi_driver_profiles.post(
        'v1/identity-docs/retrieve',
        json={
            'id_in_set': [
                '000000000000000000000002',
                '000000000000000000000003',
            ],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'docs': [
            {
                'id': '000000000000000000000002',
                'data': {
                    'driver_id': 'driver2',
                    'park_id': 'park2',
                    'type': 'passport_rus',
                    'data_pd_id': '36912ab0fbe147dd9d18b7ecfb9893ef',
                    'number_pd_id': '6d0cca029b9c4798bf953b033ce3afed',
                },
            },
            {'id': '000000000000000000000003'},
        ],
    }


async def test_identity_docs_retrieve_by_park_driver_profile_id(
        taxi_driver_profiles,
):
    response = await taxi_driver_profiles.post(
        'v1/identity-docs/retrieve_by_park_driver_profile_id',
        json={
            'park_driver_profile_id_in_set': [
                'park1_driver1',
                'park2_driver2',
            ],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'docs_by_park_driver_profile_id': [
            {
                'park_driver_profile_id': 'park1_driver1',
                'docs': [
                    {
                        'id': '000000000000000000000001',
                        'data': {
                            'driver_id': 'driver1',
                            'park_id': 'park1',
                            'type': 'passport_rus',
                            'data_pd_id': '2e127c1f4ca14019bcc46ad561e8a2ed',
                            'number_pd_id': 'c44c6d42008c4f679bc627fc95cadb49',
                        },
                    },
                ],
            },
            {
                'park_driver_profile_id': 'park2_driver2',
                'docs': [
                    {
                        'id': '000000000000000000000002',
                        'data': {
                            'driver_id': 'driver2',
                            'park_id': 'park2',
                            'type': 'passport_rus',
                            'data_pd_id': '36912ab0fbe147dd9d18b7ecfb9893ef',
                            'number_pd_id': '6d0cca029b9c4798bf953b033ce3afed',
                        },
                    },
                ],
            },
        ],
    }


async def test_identity_docs_retrieve_by_park_driver_profile_id_type(
        taxi_driver_profiles,
):
    response = await taxi_driver_profiles.post(
        'v1/identity-docs/retrieve_by_park_driver_profile_id_type',
        json={
            'park_driver_profile_id_type_in_set': [
                'park1_driver1_passport_rus',
                'park1_driver1_sailor_rus',
            ],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'docs_by_park_driver_profile_id_type': [
            {
                'park_driver_profile_id_type': 'park1_driver1_passport_rus',
                'docs': [
                    {
                        'id': '000000000000000000000001',
                        'data': {
                            'driver_id': 'driver1',
                            'park_id': 'park1',
                            'type': 'passport_rus',
                            'data_pd_id': '2e127c1f4ca14019bcc46ad561e8a2ed',
                            'number_pd_id': 'c44c6d42008c4f679bc627fc95cadb49',
                        },
                    },
                ],
            },
            {
                'park_driver_profile_id_type': 'park1_driver1_sailor_rus',
                'docs': [],
            },
        ],
    }
