import pytest

from tests_scooters_misc import utils

ENDPOINT = '/admin/v1/depots/update'

DEPOT_1 = {
    'depot_id': 'depot_id1',
    'location': {'lon': 1, 'lat': 2},
    'city': 'Moscow',
    'address': 'ul. Moscow 1',
    'enabled': True,
    'timetable': [],
}
DEPOT_1_UPDATED = {
    'depot_id': 'depot_id1',
    'location': {'lon': 3, 'lat': 4},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 1',
    'enabled': True,
    'timetable': [],
}
DEPOT_1_DISABLED = {
    'depot_id': 'depot_id1',
    'location': {'lon': 1, 'lat': 2},
    'city': 'Moscow',
    'address': 'ul. Moscow 1',
    'enabled': False,
    'timetable': [],
}
DEPOT_2 = {
    'depot_id': 'depot_id2',
    'location': {'lon': 3, 'lat': 4},
    'city': 'Moscow',
    'address': 'ul. Moscow 2',
    'enabled': True,
    'timetable': [],
}

DEPOT_1_WITH_TIMETABLE = {
    'depot_id': 'depot_id1',
    'location': {'lon': 1, 'lat': 2},
    'city': 'Moscow',
    'address': 'ul. Moscow 1',
    'enabled': True,
    'timetable': [{'day_type': 'monday', 'from': '08:00', 'to': '20:30'}],
}


def add_depots(pgsql, number: int = 1):
    for i in range(1, number + 1):
        utils.add_depot(
            pgsql,
            {
                'depot_id': f'depot_id{i}',
                'location': (2 * i - 1, 2 * i),
                'created_at': '2021-09-07T15:56:12.646822+00:00',
                'updated_at': '2021-09-07T15:56:12.646822+00:00',
                'enabled': i % 2 != 0,
                'city': 'Moscow',
                'address': f'ul. Moscow {i}',
                'timetable': [],
            },
        )


@pytest.mark.parametrize(
    'json_, depot_id, response_expected',
    [
        pytest.param(
            {
                'set': {
                    'location': {'lon': 3, 'lat': 4},
                    'city': 'Krasnodar',
                    'address': 'ul. Krasnodar 1',
                },
                'unset': [],
            },
            'depot_id1',
            DEPOT_1_UPDATED,
            id='correct update',
        ),
        pytest.param(
            {'set': {'location': {'lon': 1, 'lat': 2}}, 'unset': []},
            'depot_id1',
            DEPOT_1,
            id='emulate retry',
        ),
        pytest.param(
            {'set': {}, 'unset': []}, 'depot_id1', DEPOT_1, id='do not update',
        ),
        pytest.param(
            {'set': {'enabled': False}, 'unset': []},
            'depot_id1',
            DEPOT_1_DISABLED,
            id='disable depot',
        ),
        pytest.param(
            {'set': {'enabled': True}, 'unset': []},
            'depot_id2',
            DEPOT_2,
            id='enable depot',
        ),
        pytest.param(
            {
                'set': {
                    'timetable': [
                        {'day_type': 'monday', 'from': '08:00', 'to': '20:30'},
                    ],
                },
                'unset': [],
            },
            'depot_id1',
            DEPOT_1_WITH_TIMETABLE,
            id='set timetable',
        ),
    ],
)
async def test_ok(
        taxi_scooters_misc, pgsql, json_, depot_id, response_expected,
):
    add_depots(pgsql, 2)

    response = await taxi_scooters_misc.post(
        ENDPOINT, params={'depot_id': depot_id}, json=json_,
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
        pgsql, depot_id, fields=['depot_id', 'location'],
    ) == [(depot_id, f'({lon},{lat})')]


@pytest.mark.parametrize(
    'json_, depot_id, message',
    [
        pytest.param(
            {'set': {'location': {'lon': 3, 'lat': 4}}, 'unset': []},
            'depot_id123',
            'kUpdateDepots: depot with id `depot_id123` doesn\'t exist.',
            id='depot doesn\'t exist',
        ),
    ],
)
async def test_bad(taxi_scooters_misc, pgsql, json_, depot_id, message):
    add_depots(pgsql)

    response = await taxi_scooters_misc.post(
        ENDPOINT, params={'depot_id': depot_id}, json=json_,
    )

    assert response.status_code == 400

    assert response.json()['message'] == message
