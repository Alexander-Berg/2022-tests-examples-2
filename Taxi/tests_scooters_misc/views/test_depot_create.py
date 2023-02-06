import pytest

from tests_scooters_misc import utils

ENDPOINT = '/admin/v1/depots/create'

DEPOT_RESPONSE_1 = {
    'depot_id': 'depot_id5',
    'location': {'lon': 10, 'lat': 20},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 1',
    'enabled': True,
    'timetable': [{'day_type': 'monday', 'from': '08:00', 'to': '20:30'}],
}


DEPOT_RESPONSE_2 = {
    'depot_id': 'depot_id1',
    'location': {'lon': 1, 'lat': 2},
    'city': 'Moscow',
    'address': 'ul. Moscow 2',
    'enabled': True,
    'timetable': [],
}

DEPOT_RESPONSE_3 = {
    'depot_id': 'depot_id5',
    'location': {'lon': 10, 'lat': 20},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 1',
    'enabled': True,
    'timetable': [],
}


def add_depots(pgsql, number: int = 1):
    for i in range(1, number + 1):
        utils.add_depot(
            pgsql,
            {
                'depot_id': f'depot_id{i}',
                'location': (2 * i - 1, 2 * i),
                'idempotency_token': f'000000000000000{i}',
                'created_at': '2021-09-07T15:56:12.646822+00:00',
                'updated_at': '2021-09-07T15:56:12.646822+00:00',
                'city': 'Moscow',
                'address': 'ul. Moscow 2',
                'enabled': True,
                'timetable': [],
            },
        )


@pytest.mark.parametrize(
    'idempotency_token, json_, db_size, response_expected',
    [
        pytest.param(
            '0000000000000005',
            {
                'location': {'lon': 10, 'lat': 20},
                'depot_id': 'depot_id5',
                'city': 'Krasnodar',
                'address': 'ul. Krasnodar 1',
                'enabled': True,
                'timetable': [
                    {'day_type': 'monday', 'from': '08:00', 'to': '20:30'},
                ],
            },
            2,
            DEPOT_RESPONSE_1,
            id='correct insert',
        ),
        pytest.param(
            '0000000000000006',
            {
                'location': {'lon': 10, 'lat': 20},
                'depot_id': 'depot_id5',
                'city': 'Krasnodar',
                'address': 'ul. Krasnodar 1',
            },
            2,
            DEPOT_RESPONSE_3,
            id='correct insert without optional fields',
        ),
        pytest.param(
            '0000000000000001',
            {
                'location': {'lon': 1, 'lat': 2},
                'depot_id': 'depot_id1',
                'city': 'Moscow',
                'address': 'ul. Moscow 2',
                'enabled': True,
            },
            2,
            DEPOT_RESPONSE_2,
            id='emulate retry',
        ),
    ],
)
async def test_ok(
        taxi_scooters_misc,
        pgsql,
        idempotency_token,
        json_,
        db_size,
        response_expected,
):
    add_depots(pgsql, db_size)

    response = await taxi_scooters_misc.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        json=json_,
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json['depot_id'] == response_expected['depot_id']
    assert response_json['location'] == response_expected['location']
    assert response_json['city'] == response_expected['city']
    assert response_json['address'] == response_expected['address']
    assert response_json['enabled'] == response_expected['enabled']
    assert response_json['timetable'] == response_expected['timetable']

    lon = response_expected['location']['lon']
    lat = response_expected['location']['lat']

    assert utils.get_depot(
        pgsql, json_['depot_id'], fields=['depot_id', 'location'],
    ) == [(json_['depot_id'], f'({lon},{lat})')]


@pytest.mark.parametrize(
    'idempotency_token, json_, expected_error, db_size, prev_depot',
    [
        pytest.param(
            '0000000000000005',
            {
                'location': {'lon': 14, 'lat': 88},
                'depot_id': 'depot_id1',
                'city': 'Krasnodar',
                'address': 'ul. Moscow 222',
                'enabled': True,
            },
            'Depot with id `depot_id1` already exists',
            2,
            DEPOT_RESPONSE_2,
            id='existent depot',
        ),
    ],
)
async def test_bad(
        taxi_scooters_misc,
        pgsql,
        idempotency_token,
        json_,
        expected_error,
        db_size,
        prev_depot,
):
    add_depots(pgsql, db_size)

    response = await taxi_scooters_misc.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        json=json_,
    )

    assert response.status_code == 400

    assert response.json()['message'] == expected_error

    lon = prev_depot['location']['lon']
    lat = prev_depot['location']['lat']

    assert utils.get_depot(
        pgsql, json_['depot_id'], fields=['depot_id', 'location'],
    ) == [(json_['depot_id'], f'({lon},{lat})')]
