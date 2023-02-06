import pytest

from tests_scooters_misc import utils

ENDPOINT = '/admin/v1/depots/suggests/city'

DEPOT_1 = {
    'cabinets': [],
    'depot_id': 'depot_id1',
    'created_at': '2019-12-17T04:38:54+00:00',
    'updated_at': '2019-12-17T04:38:54+00:00',
    'location': {'lat': 2.0, 'lon': 1.0},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 1',
}

DEPOT_2 = {
    'cabinets': [],
    'depot_id': 'depot_id2',
    'created_at': '2019-12-17T04:38:55+00:00',
    'updated_at': '2019-12-17T04:38:55+00:00',
    'location': {'lat': 4.0, 'lon': 3.0},
    'city': 'Moscow',
    'address': 'ul. Moscow 2',
}

DEPOT_3 = {
    'cabinets': [],
    'depot_id': 'depot_id3',
    'created_at': '2019-12-17T04:38:56+00:00',
    'updated_at': '2019-12-17T04:38:56+00:00',
    'location': {'lat': 6.0, 'lon': 5.0},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 3',
}

DEPOT_4 = {
    'cabinets': [],
    'depot_id': 'depot_id4',
    'created_at': '2019-12-17T04:38:57+00:00',
    'updated_at': '2019-12-17T04:38:57+00:00',
    'location': {'lat': 8.0, 'lon': 7.0},
    'city': 'Moscow',
    'address': 'ul. Moscow 4',
}

DEPOT_5 = {
    'cabinets': [],
    'depot_id': 'depot_id5',
    'created_at': '2019-12-17T04:38:58+00:00',
    'updated_at': '2019-12-17T04:38:58+00:00',
    'location': {'lat': 10.0, 'lon': 9.0},
    'city': 'Spb',
    'address': 'ul. Spb 5',
}


def add_depots(pgsql, number: int = 1):
    for i in range(1, number + 1):
        city = ''
        if i % 2 == 0:
            city = 'Moscow'
        else:
            city = 'Krasnodar'
        if i == 5:
            city = 'Spb'

        utils.add_depot(
            pgsql,
            {
                'depot_id': f'depot_id{i}',
                'location': (2 * i - 1, 2 * i),
                'created_at': f'2019-12-17T07:38:5{i+3}',
                'updated_at': f'2019-12-17T07:38:5{i+3}',
                'city': city,
                'address': f'ul. {city} {i}',
            },
        )


@pytest.mark.parametrize(
    'search, json_response, db_size',
    [
        pytest.param('os', {'cities': [DEPOT_2['city']]}, 5, id='search os'),
        pytest.param(
            None,
            {'cities': [DEPOT_3['city'], DEPOT_4['city'], DEPOT_5['city']]},
            5,
            id='all data request',
        ),
    ],
)
async def test_ok(taxi_scooters_misc, pgsql, search, json_response, db_size):

    add_depots(pgsql, db_size)
    params = {}
    if search:
        params['search'] = search

    response = await taxi_scooters_misc.get(ENDPOINT, params=params)
    assert response.status_code == 200
    assert response.json() == json_response
