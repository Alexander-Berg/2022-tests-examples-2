import json

import pytest

from tests_vgw_api import db_regions


@pytest.mark.parametrize(
    ('params', 'response_data'),
    [
        (
            {'region_id': 1},
            {
                'region_id': 1,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Moscow',
                        'enabled_for': [],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                        ],
                    },
                ],
            },
        ),
        (
            {'region_id': 2},
            {
                'region_id': 2,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': False,
                        'city_id': 'Moscow',
                        'enabled_for': ['driver', 'passenger'],
                        'consumers': [{'consumer_id': 1, 'enabled': False}],
                    },
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Moscow',
                        'enabled_for': ['passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                        ],
                    },
                ],
            },
        ),
        ({'region_id': 3}, {'region_id': 3, 'gateways': []}),
    ],
)
async def test_region_get(taxi_vgw_api, params, response_data):
    response = await taxi_vgw_api.get(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert response.status_code == 200
    assert response.json() == response_data


@pytest.mark.parametrize(
    ('params', 'response_code'),
    [
        ({'region_id': 'text_id'}, 400),
        ({'region_id': 2147483648}, 400),
        ({'region_id': 100}, 404),
    ],
)
async def test_region_get_errors(taxi_vgw_api, params, response_code):
    response = await taxi_vgw_api.get(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)


@pytest.mark.pgsql(
    'vgw_api', files=['pg_vgw_api_regions_client_type_duplicates.sql'],
)
@pytest.mark.parametrize(
    ('params', 'response_data', 'response_code'),
    [
        (
            {'region_id': 1},
            {
                'region_id': 1,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Moscow',
                        'enabled_for': ['passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                        ],
                    },
                ],
            },
            200,
        ),
    ],
)
async def test_region_get_client_type_duplicates_in_db(
        taxi_vgw_api, params, response_data, response_code,
):
    response = await taxi_vgw_api.get(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert response.status_code == response_code
    assert response.json() == response_data


@pytest.mark.parametrize(
    ('params', 'db_data'),
    [
        (
            {'region_id': 1},
            [
                (
                    2,
                    'id_1',
                    [1],
                    [False],
                    'Moscow',
                    '{passenger,driver}',
                    False,
                ),
                (
                    2,
                    'id_2',
                    [1, 2],
                    [True, True],
                    'Moscow',
                    '{passenger}',
                    True,
                ),
            ],
        ),
        (
            {'region_id': 2},
            [(1, 'id_1', [1, 2], [True, True], 'Moscow', '{}', True)],
        ),
        (
            {'region_id': 3},
            [
                (1, 'id_1', [1, 2], [True, True], 'Moscow', '{}', True),
                (
                    2,
                    'id_1',
                    [1],
                    [False],
                    'Moscow',
                    '{passenger,driver}',
                    False,
                ),
                (
                    2,
                    'id_2',
                    [1, 2],
                    [True, True],
                    'Moscow',
                    '{passenger}',
                    True,
                ),
            ],
        ),
    ],
)
async def test_region_delete(taxi_vgw_api, pgsql, params, db_data):
    response = await taxi_vgw_api.delete(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert response.status_code == 200
    assert db_regions.select_gateway_region_settings(pgsql) == db_data


@pytest.mark.parametrize(
    ('params', 'response_code'),
    [
        ({'region_id': 'text_id'}, 400),
        ({'region_id': 2147483648}, 400),
        ({'region_id': 100}, 404),
    ],
)
async def test_region_delete_errors(taxi_vgw_api, params, response_code):
    response = await taxi_vgw_api.delete(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)


@pytest.mark.parametrize(
    ('params', 'request_data', 'response_data'),
    [
        (
            {'region_id': 4},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                    },
                ],
            },
            {
                'region_id': 4,
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': True},
                        ],
                    },
                ],
            },
        ),
        (
            {'region_id': 5},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Some-city-2',
                        'enabled_for': ['driver', 'passenger'],
                    },
                    {
                        'gateway_id': 'id_2',
                        'enabled': False,
                        'city_id': 'Some-city-3',
                        'enabled_for': ['passenger'],
                    },
                ],
            },
            {
                'region_id': 5,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Some-city-2',
                        'enabled_for': ['driver', 'passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': True},
                        ],
                    },
                    {
                        'gateway_id': 'id_2',
                        'enabled': False,
                        'city_id': 'Some-city-3',
                        'enabled_for': ['passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': False},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
        ),
        (
            {'region_id': 3},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                    },
                ],
            },
            {
                'region_id': 3,
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': True},
                        ],
                    },
                ],
            },
        ),
        (
            {'region_id': 2},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                    },
                ],
            },
            {
                'region_id': 2,
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': True},
                        ],
                    },
                ],
            },
        ),
        ({'region_id': 2}, {'gateways': []}, {'region_id': 2, 'gateways': []}),
        (
            {'region_id': 2},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['passenger', 'passenger'],
                    },
                ],
            },
            {
                'region_id': 2,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': True},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': True},
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_region_put_old(
        taxi_vgw_api, params, request_data, response_data,
):
    response = await taxi_vgw_api.put(
        'v1/voice_gateways_regions/id',
        params=params,
        data=json.dumps(request_data),
    )
    assert response.status_code == 200
    get_response = await taxi_vgw_api.get(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert get_response.json() == response_data


@pytest.mark.parametrize(
    ('params', 'request_data', 'response_data'),
    [
        (
            {'region_id': 4},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
            {
                'region_id': 4,
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
        ),
        (
            {'region_id': 5},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'city_id': 'Some-city-2',
                        'enabled_for': ['driver', 'passenger'],
                        'consumers': [{'consumer_id': 2, 'enabled': True}],
                    },
                    {
                        'gateway_id': 'id_2',
                        'city_id': 'Some-city-3',
                        'enabled_for': ['passenger'],
                        'consumers': [],
                    },
                ],
            },
            {
                'region_id': 5,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': True,
                        'city_id': 'Some-city-2',
                        'enabled_for': ['driver', 'passenger'],
                        'consumers': [{'consumer_id': 2, 'enabled': True}],
                    },
                    {
                        'gateway_id': 'id_2',
                        'enabled': False,
                        'city_id': 'Some-city-3',
                        'enabled_for': ['passenger'],
                        'consumers': [],
                    },
                ],
            },
        ),
        (
            {'region_id': 3},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
            {
                'region_id': 3,
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
        ),
        (
            {'region_id': 2},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
            {
                'region_id': 2,
                'gateways': [
                    {
                        'gateway_id': 'id_2',
                        'enabled': True,
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': True},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
        ),
        ({'region_id': 2}, {'gateways': []}, {'region_id': 2, 'gateways': []}),
        (
            {'region_id': 2},
            {
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'city_id': 'Some-city',
                        'enabled_for': ['passenger', 'passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': False},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
            {
                'region_id': 2,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'enabled': False,
                        'city_id': 'Some-city',
                        'enabled_for': ['passenger'],
                        'consumers': [
                            {'consumer_id': 1, 'enabled': False},
                            {'consumer_id': 2, 'enabled': False},
                            {'consumer_id': 3, 'enabled': False},
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_region_put(taxi_vgw_api, params, request_data, response_data):
    response = await taxi_vgw_api.put(
        'v1/voice_gateways_regions/id',
        params=params,
        data=json.dumps(request_data),
    )
    assert response.status_code == 200
    get_response = await taxi_vgw_api.get(
        'v1/voice_gateways_regions/id', params=params,
    )
    assert get_response.json() == response_data


@pytest.mark.parametrize(
    ('params', 'request_data', 'response_code'),
    [
        (
            {'region_id': 4},
            {
                'region_id': 4,
                'gateways': [
                    {
                        'gateway_id': 'id_null',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [],
                    },
                ],
            },
            404,
        ),
        (
            {'not_valid_id_name': 4},
            {
                'region_id': 4,
                'gateways': [
                    {
                        'gateway_id': 'id_null',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [],
                    },
                ],
            },
            400,
        ),
        (
            {'region_id': 4},
            {
                'region_id': 4,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'city_id': 'Some-city',
                        'enabled_for': ['passenger', 'not_valid_client_type'],
                        'consumers': [],
                    },
                ],
            },
            400,
        ),
        (
            {'region_id': 4},
            {
                'region_id': 4,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [],
                    },
                    {
                        'gateway_id': 'id_1',
                        'city_id': 'Some-city',
                        'enabled_for': ['passenger'],
                        'consumers': [],
                    },
                ],
            },
            400,
        ),
    ],
)
async def test_region_put_errors(
        taxi_vgw_api, params, request_data, response_code,
):
    response = await taxi_vgw_api.put(
        'v1/voice_gateways_regions/id',
        params=params,
        data=json.dumps(request_data),
    )

    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)


@pytest.mark.parametrize(
    ('params', 'request_data'),
    [
        (
            {'region_id': 1},
            {
                'region_id': 1,
                'gateways': [
                    {
                        'gateway_id': 'id_1',
                        'city_id': 'Some-city',
                        'enabled_for': ['driver'],
                        'consumers': [],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_regions_duplicate.sql'])
async def test_region_add_deleted_region(
        taxi_vgw_api, pgsql, params, request_data,
):
    response = await taxi_vgw_api.put(
        'v1/voice_gateways_regions/id',
        params=params,
        data=json.dumps(request_data),
    )
    assert response.status_code == 200

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute('SELECT deleted FROM regions.regions ORDER BY id')
    result = cursor.fetchall()
    cursor.close()
    assert len(result) == 2
    assert not result[0][0]  # id: 1 - activated because created new
    assert result[1][0]  # id: 2 still deactivated
