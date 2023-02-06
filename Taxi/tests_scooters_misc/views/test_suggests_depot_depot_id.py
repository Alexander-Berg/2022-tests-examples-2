import pytest

from tests_scooters_misc import utils

ENDPOINT = '/admin/v1/depots/suggests/depot_id'

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


def add_depots(pgsql, number: int = 1):
    for i in range(1, number + 1):
        city = ''
        if i % 2 == 0:
            city = 'Moscow'
        else:
            city = 'Krasnodar'

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
    'cursor, limit, json_response, db_size, search',
    [
        pytest.param(
            None,
            1,
            {
                'depot_ids': [DEPOT_4['depot_id']],
                'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfGRlcG90X2lkNA',
            },
            4,
            None,
            id='first request',
        ),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfGRlcG90X2lkNA',
            3,
            {
                'depot_ids': [
                    DEPOT_3['depot_id'],
                    DEPOT_2['depot_id'],
                    DEPOT_1['depot_id'],
                ],
            },
            4,
            None,
            id='second request',
        ),
        pytest.param(
            None,
            None,
            {
                'depot_ids': [
                    DEPOT_4['depot_id'],
                    DEPOT_3['depot_id'],
                    DEPOT_2['depot_id'],
                    DEPOT_1['depot_id'],
                ],
            },
            4,
            None,
            id='all data request',
        ),
        pytest.param(
            None,
            None,
            {'depot_ids': [DEPOT_2['depot_id']]},
            4,
            'id2',
            id='search id2',
        ),
    ],
)
async def test_ok(
        taxi_scooters_misc,
        pgsql,
        cursor,
        limit,
        json_response,
        db_size,
        search,
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
