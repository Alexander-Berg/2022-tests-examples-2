import pytest

from tests_scooters_misc import utils

ENDPOINT = '/admin/v1/depots/suggests/address'

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
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 1',
}


def add_depots(pgsql, number: int = 1):
    for i in range(1, number + 1):
        city = ''
        if i % 2 == 0:
            city = 'Moscow'
        else:
            city = 'Krasnodar'
        j = i
        if i == 5:
            j = 1
        utils.add_depot(
            pgsql,
            {
                'depot_id': f'depot_id{i}',
                'location': (2 * i - 1, 2 * i),
                'created_at': f'2019-12-17T07:38:5{i+3}',
                'updated_at': f'2019-12-17T07:38:5{i+3}',
                'city': city,
                'address': f'ul. {city} {j}',
            },
        )


@pytest.mark.parametrize(
    'cursor, limit, json_response, db_size, search',
    [
        pytest.param(
            None,
            1,
            {
                'addresses': [DEPOT_4['address']],
                'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfHVsLiBNb3Njb3cgNA',
            },
            5,
            None,
            id='first request',
        ),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfHVsLiBNb3Njb3cgNA',
            3,
            {
                'addresses': [
                    DEPOT_3['address'],
                    DEPOT_2['address'],
                    DEPOT_1['address'],
                ],
            },
            5,
            None,
            id='second request',
        ),
        pytest.param(
            None,
            None,
            {
                'addresses': [
                    DEPOT_4['address'],
                    DEPOT_3['address'],
                    DEPOT_2['address'],
                    DEPOT_1['address'],
                ],
            },
            5,
            None,
            id='all data request',
        ),
        pytest.param(
            None,
            None,
            {'addresses': [DEPOT_4['address'], DEPOT_2['address']]},
            5,
            'cow',
            id='search cow',
        ),
    ],
)
async def test_ok(
        taxi_scooters_misc,
        pgsql,
        cursor,
        limit,
        search,
        json_response,
        db_size,
):

    add_depots(pgsql, db_size)
    params = {}
    if limit:
        params['limit'] = limit
    if cursor:
        params['cursor'] = cursor
    if search:
        params['search'] = search

    response = await taxi_scooters_misc.get(ENDPOINT, params=params)
    assert response.status_code == 200
    assert response.json() == json_response
