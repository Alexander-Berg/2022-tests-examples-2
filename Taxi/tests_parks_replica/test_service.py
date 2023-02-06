import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from parks_replica_plugins.generated_tests import *  # noqa


async def test_parks_updates(taxi_parks_replica):
    response = await taxi_parks_replica.get(
        'v1/parks/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_0'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_3',
        'parks': [
            {
                'revision': '0_1234567_1',
                'park_id': 'park_id_1',
                'data': {
                    'city': 'spb',
                    'name': 'name1',
                    'phone_pd_id': 'phone_pd_id_1',
                    'email_pd_id': 'email_pd_id_1',
                    'threshold': '15.500000',
                    'balances': [{'contract_id': 3121565}],
                    'recommended_payments': [130753.75],
                    'promised_payment_till': '1970-01-15T06:56:07.000',
                    'account_invalid_bankprops': True,
                    'corp_vats': [
                        {
                            'begin': '1970-01-15T06:56:07.000',
                            'end': '1970-01-15T06:56:07.000',
                            'value': 100,
                        },
                        {'end': '1970-01-15T06:56:07.000', 'value': 100},
                        {'begin': '1970-01-15T06:56:07.000'},
                    ],
                    'requirements': {'creditcard': False, 'coupon': True},
                    'legal_address': '777777,Москва,Садовническая наб.',
                    'long_name': (
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЧИРИК"'
                    ),
                    'ogrn': '777',
                    'inn': 'test_inn_1',
                    'legal_log': [
                        {
                            'legal_address': '420111,Казань,ул Карла Маркса,5',
                            'long_name': (
                                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ '
                                'ОТВЕТСТВЕННОСТЬЮ "СВР"'
                            ),
                            'ogrn': '1187746641940',
                            'updated': '2019-11-20T11:03:52.004',
                        },
                    ],
                },
            },
            {
                'revision': '0_1234567_2',
                'park_id': 'park_id_2',
                'data': {
                    'city': 'moscow',
                    'name': 'name2',
                    'threshold': '0.100000',
                    'requirements': {'creditcard': True, 'corp': True},
                    'deactivated_reason': 'reason1',
                    'account_invalid_bankprops': True,
                },
            },
            {'revision': '0_1234567_3', 'park_id': 'park_id_3', 'data': {}},
        ],
    }


async def test_parks_updates_projection(taxi_parks_replica):
    response = await taxi_parks_replica.post(
        'v1/parks/updates',
        params={'consumer': 'test'},
        json={
            'last_known_revision': '0_1234567_0',
            'projection': ['data.city', 'data.corp_vats'],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_3',
        'parks': [
            {
                'park_id': 'park_id_1',
                'data': {
                    'city': 'spb',
                    'corp_vats': [
                        {
                            'begin': '1970-01-15T06:56:07.000',
                            'end': '1970-01-15T06:56:07.000',
                            'value': 100,
                        },
                        {'end': '1970-01-15T06:56:07.000', 'value': 100},
                        {'begin': '1970-01-15T06:56:07.000'},
                    ],
                },
            },
            {'park_id': 'park_id_2', 'data': {'city': 'moscow'}},
            {'park_id': 'park_id_3', 'data': {}},
        ],
    }


async def test_parks_retrieve(taxi_parks_replica):
    response = await taxi_parks_replica.post(
        'v1/parks/retrieve',
        json={'id_in_set': ['park_id_1', 'unknown_id']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json == {
        'parks': [
            {
                'revision': '0_1234567_1',
                'park_id': 'park_id_1',
                'data': {
                    'city': 'spb',
                    'name': 'name1',
                    'phone_pd_id': 'phone_pd_id_1',
                    'email_pd_id': 'email_pd_id_1',
                    'threshold': '15.500000',
                    'balances': [{'contract_id': 3121565}],
                    'recommended_payments': [130753.75],
                    'promised_payment_till': '1970-01-15T06:56:07.000',
                    'account_invalid_bankprops': True,
                    'corp_vats': [
                        {
                            'begin': '1970-01-15T06:56:07.000',
                            'end': '1970-01-15T06:56:07.000',
                            'value': 100,
                        },
                        {'end': '1970-01-15T06:56:07.000', 'value': 100},
                        {'begin': '1970-01-15T06:56:07.000'},
                    ],
                    'requirements': {'creditcard': False, 'coupon': True},
                    'legal_address': '777777,Москва,Садовническая наб.',
                    'long_name': (
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ЧИРИК"'
                    ),
                    'ogrn': '777',
                    'inn': 'test_inn_1',
                    'legal_log': [
                        {
                            'legal_address': '420111,Казань,ул Карла Маркса,5',
                            'long_name': (
                                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ '
                                'ОТВЕТСТВЕННОСТЬЮ "СВР"'
                            ),
                            'ogrn': '1187746641940',
                            'updated': '2019-11-20T11:03:52.004',
                        },
                    ],
                },
            },
            {'park_id': 'unknown_id'},
        ],
    }


@pytest.mark.parametrize(
    'projection, data_field',
    [
        (
            ['data.city', 'data.corp_vats', 'data.requirements.creditcard'],
            {
                'city': 'spb',
                'corp_vats': [
                    {
                        'begin': '1970-01-15T06:56:07.000',
                        'end': '1970-01-15T06:56:07.000',
                        'value': 100,
                    },
                    {'end': '1970-01-15T06:56:07.000', 'value': 100},
                    {'begin': '1970-01-15T06:56:07.000'},
                ],
                'requirements': {'creditcard': False},
            },
        ),
        (['data.name'], {'name': 'name1'}),
    ],
)
async def test_parks_retrieve_projection(
        taxi_parks_replica, projection, data_field,
):
    response = await taxi_parks_replica.post(
        'v1/parks/retrieve',
        json={
            'id_in_set': ['park_id_1', 'unknown_id'],
            'projection': projection,
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'parks': [
            {'park_id': 'park_id_1', 'data': data_field},
            {'park_id': 'unknown_id'},
        ],
    }


async def test_parks_retrieve_projection_array(taxi_parks_replica):
    response = await taxi_parks_replica.post(
        'v1/parks/retrieve',
        json={
            'id_in_set': ['park_id_1', 'unknown_id'],
            'projection': ['data.corp_vats.value'],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'parks': [
            {
                'park_id': 'park_id_1',
                'data': {'corp_vats': [{'value': 100}, {'value': 100}]},
            },
            {'park_id': 'unknown_id'},
        ],
    }
