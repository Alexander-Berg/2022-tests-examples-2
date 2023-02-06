import base64
import json
import typing as tp

import pytest

SIMPLE_PROJECTION = [
    'person.full_name.first_name',
    'person.full_name.middle_name',
    'person.full_name.last_name',
    'person.driver_license_experience.total_since_date',
    'person.driver_license.issue_date',
    'person.driver_license.expire_date',
    'person.driver_license.birth_date',
    'person.driver_license.number_pd_id',
    'person.driver_license.country',
    'person.contact_info.email_pd_id',
    'person.contact_info.phone_pd_ids',
    'person.is_deaf',
    'car_id',
    'providers.platform',
]

FULL_PROJECTION = [
    'car_id',
    'platform_uid',
    'is_removed_by_request',
    'person.full_name.first_name',
    'person.full_name.middle_name',
    'person.full_name.last_name',
    'person.driver_license.issue_date',
    'person.driver_license.expire_date',
    'person.driver_license.birth_date',
    'person.driver_license.number_pd_id',
    'person.driver_license.country',
    'person.driver_license_experience.total_since_date',
    'person.contact_info.email_pd_id',
    'person.contact_info.phone_pd_ids',
    'person.is_deaf',
    'account.balance_limit',
    'account.rule_id',
    'profile.work_status',
    'profile.hire_date',
    'profile.fire_date',
    'profile.hiring_type',
    'profile.hiring_source',
    'profile.tax_identification_number_pd_id',
    'profile.check_message',
    'internal.delivery.thermobag',
    'internal.delivery.thermopack',
    'internal.delivery.profi_courier',
    'internal.medical_card.is_enabled',
    'internal.medical_card.issue_date',
    'internal.external_ids.eats',
    'internal.courier_app',
    'internal.courier_type',
    'internal.orders_provider.eda',
    'internal.orders_provider.lavka',
    'internal.orders_provider.taxi',
    'internal.orders_provider.taxi_walking_courier',
    'internal.orders_provider.cargo',
    'internal.orders_provider.retail',
    'providers.platform',
    'providers.partner',
]


def check_cursor(cursor, request, last_item):
    assert cursor['sort']['field'] == request['sort']['field']
    assert cursor['sort']['direction'] == request['sort']['direction']
    assert cursor['projection'] == request['projection']
    assert cursor['last_item'] == last_item


def decode_cursor(cursor_str):
    return json.loads(base64.b64decode(cursor_str))


def encode_cursor(cursor: tp.Dict):
    return base64.b64encode(json.dumps(cursor).encode('utf-8')).decode()


@pytest.mark.parametrize(
    ('limit', 'sort', 'park_id', 'projection', 'response', 'last_item'),
    [
        (
            3,
            {'field': 'created_at', 'direction': 'asc'},
            'park_test',
            SIMPLE_PROJECTION,
            [
                {
                    'created_at': '2015-11-20T17:04:14.517+00:00',
                    'contractor_profile_id': 'driver2',
                    'person': {
                        'full_name': {
                            'first_name': 'Анатой',
                            'last_name': 'Зов',
                            'middle_name': 'Аольевич',
                        },
                        'driver_license': {
                            'issue_date': '2018-11-20',
                            'expire_date': '2018-11-20',
                            'birth_date': '1995-11-20',
                            'number_pd_id': 'driver_license_pd_id_2',
                            'country': 'Russia',
                        },
                        'driver_license_experience': {
                            'total_since_date': '2018-11-20',
                        },
                        'contact_info': {
                            'email_pd_id': 'mail1',
                            'phone_pd_ids': ['phone_pd_id_2', 'phone_pd_id_3'],
                        },
                        'is_deaf': False,
                    },
                    'car_id': 'car2',
                    'providers': {'platform': True},
                },
                {
                    'created_at': '2017-05-20T17:04:14.517+00:00',
                    'contractor_profile_id': 'driver3',
                    'car_id': 'car3',
                    'person': {
                        'contact_info': {'phone_pd_ids': ['12']},
                        'is_deaf': False,
                    },
                },
                {
                    'created_at': '2017-11-20T17:04:14.517+00:00',
                    'contractor_profile_id': 'ddddriver1',
                    'person': {
                        'full_name': {
                            'first_name': 'Дмий',
                            'last_name': 'Боркий',
                            'middle_name': 'Сервич',
                        },
                        'driver_license': {
                            'number_pd_id': 'driver_license_pd_id_1',
                            'country': 'rus',
                        },
                        'contact_info': {'phone_pd_ids': ['phone_pd_id_1']},
                        'is_deaf': True,
                    },
                    'car_id': 'car1',
                },
            ],
            {
                'created_at': '2017-11-21T17:04:14.517+00:00',
                'driver_id': 'driver4',
            },
        ),
        (
            1,
            {'field': 'created_at', 'direction': 'asc'},
            'park_test',
            FULL_PROJECTION,
            [
                {
                    'created_at': '2015-11-20T17:04:14.517+00:00',
                    'car_id': 'car2',
                    'person': {
                        'full_name': {
                            'first_name': 'Анатой',
                            'last_name': 'Зов',
                            'middle_name': 'Аольевич',
                        },
                        'contact_info': {
                            'email_pd_id': 'mail1',
                            'phone_pd_ids': ['phone_pd_id_2', 'phone_pd_id_3'],
                        },
                        'driver_license': {
                            'issue_date': '2018-11-20',
                            'expire_date': '2018-11-20',
                            'birth_date': '1995-11-20',
                            'number_pd_id': 'driver_license_pd_id_2',
                            'country': 'Russia',
                        },
                        'driver_license_experience': {
                            'total_since_date': '2018-11-20',
                        },
                        'is_deaf': False,
                    },
                    'account': {
                        'balance_limit': '12.000000',
                        'rule_id': 'testrule',
                    },
                    'profile': {
                        'work_status': 'driving??',
                        'hire_date': '1970-01-13',
                        'fire_date': '2005-01-13',
                        'hiring_type': 'type',
                        'hiring_source': 'example_source',
                        'tax_identification_number_pd_id': '1234567890',
                        'check_message': 'messages',
                    },
                    'internal': {
                        'delivery': {
                            'profi_courier': False,
                            'thermobag': False,
                            'thermopack': False,
                        },
                        'medical_card': {'is_enabled': False},
                        'external_ids': {'eats': 'external_id_1'},
                        'courier_app': 'eats',
                        'orders_provider': {
                            'eda': False,
                            'lavka': True,
                            'taxi': False,
                            'taxi_walking_courier': True,
                        },
                        'courier_type': 'walking_courier',
                    },
                    'providers': {'partner': False, 'platform': True},
                    'is_removed_by_request': True,
                    'platform_uid': '12345',
                    'contractor_profile_id': 'driver2',
                },
            ],
            {
                'created_at': '2017-05-20T17:04:14.517+00:00',
                'driver_id': 'driver3',
            },
        ),
    ],
)
async def test_driver_profiles_post(
        taxi_driver_profiles,
        limit,
        sort,
        park_id,
        projection,
        response,
        last_item,
):
    request = {
        'park_id': park_id,
        'limit': limit,
        'sort': sort,
        'projection': projection,
    }
    response_ = await taxi_driver_profiles.post(
        '/v1/driver-profiles/list', json=request,
    )
    assert response_.status_code == 200

    check_cursor(decode_cursor(response_.json()['cursor']), request, last_item)
    assert response_.json()['driver_profiles'] == response


async def test_driver_profiles_post_sort(taxi_driver_profiles):
    request = {
        'park_id': 'park_test',
        'limit': 2,
        'sort': {'field': 'created_at', 'direction': 'desc'},
    }
    response = await taxi_driver_profiles.post(
        '/v1/driver-profiles/list', json=request,
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['driver_profiles'] == [
        {
            'created_at': '2017-11-21T17:04:14.517+00:00',
            'contractor_profile_id': 'driver4',
        },
        {
            'created_at': '2017-11-20T17:04:14.517+00:00',
            'contractor_profile_id': 'ddddriver1',
        },
    ]


async def test_driver_profiles_get(taxi_driver_profiles):
    cursor_json = {
        'sort': {'field': 'created_at', 'direction': 'asc'},
        'projection': SIMPLE_PROJECTION,
        'park_id': 'park_test',
        'last_item': {
            'created_at': '2017-11-21T17:04:14.517+00:00',
            'driver_id': 'driver4',
        },
    }
    params = {'limit': 3, 'cursor': encode_cursor(cursor_json)}
    response = await taxi_driver_profiles.get(
        '/v1/driver-profiles/list', params=params,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['driver_profiles'] == [
        {
            'created_at': '2017-11-21T17:04:14.517+00:00',
            'contractor_profile_id': 'driver4',
            'person': {
                'full_name': {
                    'first_name': 'Серей',
                    'last_name': 'Курв',
                    'middle_name': 'Борович',
                },
                'contact_info': {'phone_pd_ids': ['phone_pd_id_4']},
                'is_deaf': False,
                'driver_license': {
                    'number_pd_id': 'driver_license_pd_id_4',
                    'birth_date': '1970-01-15',
                },
            },
            'car_id': 'car4',
        },
    ]


async def test_driver_profiles_post_not_found(taxi_driver_profiles):
    request = {
        'limit': 100,
        'sort': {'field': 'created_at', 'direction': 'asc'},
        'park_id': 'not_found_park',
    }
    response = await taxi_driver_profiles.post(
        '/v1/driver-profiles/list', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {'driver_profiles': []}


async def test_driver_profiles_post_invalid_projection(taxi_driver_profiles):
    request = {
        'limit': 100,
        'sort': {'field': 'created_at', 'direction': 'asc'},
        'park_id': 'park_test',
        'projection': ['car_id', 'car_id'],
    }
    response = await taxi_driver_profiles.post(
        '/v1/driver-profiles/list', json=request,
    )
    assert response.status_code == 400
    assert response.json() == {
        'message': 'Projection must contain unique fields',
        'code': 'invalid_projection',
    }


async def test_driver_profiles_get_invalid_cursor(taxi_driver_profiles):
    params = {'limit': 3, 'cursor': 'invalid_cusror'}
    response = await taxi_driver_profiles.get(
        '/v1/driver-profiles/list', params=params,
    )
    assert response.status_code == 400
    assert response.json() == {
        'message': 'Invalid cursor',
        'code': 'invalid_cursor',
    }


async def test_invalid_projection_in_cursor(taxi_driver_profiles):
    response = await taxi_driver_profiles.get(
        '/v1/driver-profiles/list',
        params={
            'limit': 1,
            'cursor': (
                'eyJzb3J0Ijp7ImZpZWxkIjoiY3JlYXRlZF9hdCIsImRpcmVj'
                'dGlvbiI6ImFzYyJ9LCJwYXJrX2lkIjoicGFya190ZXN0Iiwic'
                'HJvamVjdGlvbiI6WyJjYXJfaWQiLCJjYXJfaWQiXSwibGFzdF'
                '9pdGVtIjp7ImNyZWF0ZWRfYXQiOiIyMDE3LTExLTIwVDE3OjA0'
                'OjE0LjUxNyswMDowMCIsImRyaXZlcl9pZCI6ImRkZGRyaXZlcjEifX0='
            ),
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'message': 'Invalid cursor',
        'code': 'invalid_cursor',
    }
