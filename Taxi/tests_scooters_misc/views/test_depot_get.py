import typing

import pytest

from tests_scooters_misc import utils

ENDPOINT = '/admin/v1/depots/list'

TEST_EMPTY_RESPONSE: typing.Dict[str, typing.Any] = {'depots': []}

DEPOT_1 = {
    'cabinets': [
        {
            'accumulators_available_for_booking': 10,
            'cabinet_id': 'cabinet_id1',
            'cabinet_type': 'cabinet',
            'empty_cells_available_for_booking': 20,
            'accumulators_count': 11,
            'cells_count': 21,
        },
        {
            'accumulators_available_for_booking': 5,
            'cabinet_id': 'cabinet_id2',
            'cabinet_type': 'charge_station',
            'empty_cells_available_for_booking': 25,
            'accumulators_count': 6,
            'cells_count': 26,
        },
    ],
    'allowed_from_areas': ['cool_grocery_area1', 'cool_grocery_area2'],
    'depot_id': 'depot_id1',
    'created_at': '2019-12-17T04:38:54+00:00',
    'updated_at': '2019-12-17T04:38:54+00:00',
    'location': {'lat': 2.0, 'lon': 1.0},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 1',
    'enabled': True,
    'timetable': [{'day_type': 'monday', 'from': '01:00', 'to': '23:00'}],
}

DEPOT_2 = {
    'cabinets': [],
    'allowed_from_areas': [],
    'depot_id': 'depot_id2',
    'created_at': '2019-12-17T04:38:55+00:00',
    'updated_at': '2019-12-17T04:38:55+00:00',
    'location': {'lat': 4.0, 'lon': 3.0},
    'city': 'Moscow',
    'address': 'ul. Moscow 2',
    'enabled': True,
    'timetable': [{'day_type': 'monday', 'from': '02:00', 'to': '23:00'}],
}

DEPOT_3 = {
    'cabinets': [
        {
            'accumulators_available_for_booking': 14,
            'cabinet_id': 'cabinet_id3',
            'cabinet_type': 'cabinet',
            'empty_cells_available_for_booking': 16,
            'accumulators_count': 15,
            'cells_count': 17,
        },
    ],
    'allowed_from_areas': [],
    'depot_id': 'depot_id3',
    'created_at': '2019-12-17T04:38:56+00:00',
    'updated_at': '2019-12-17T04:38:56+00:00',
    'location': {'lat': 6.0, 'lon': 5.0},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 3',
    'enabled': False,
    'timetable': [{'day_type': 'monday', 'from': '03:00', 'to': '23:00'}],
}

DEPOT_4 = {
    'cabinets': [
        {
            'accumulators_available_for_booking': 17,
            'cabinet_id': 'cabinet_id4',
            'cabinet_type': 'charge_station_without_id_receiver',
            'empty_cells_available_for_booking': 13,
            'accumulators_count': 18,
            'cells_count': 14,
        },
        {
            'accumulators_available_for_booking': 13,
            'cabinet_id': 'cabinet_id5',
            'cabinet_type': 'charge_station',
            'empty_cells_available_for_booking': 17,
            'accumulators_count': 14,
            'cells_count': 18,
        },
    ],
    'allowed_from_areas': [],
    'depot_id': 'depot_id4',
    'created_at': '2019-12-17T04:38:57+00:00',
    'updated_at': '2019-12-17T04:38:57+00:00',
    'location': {'lat': 8.0, 'lon': 7.0},
    'city': 'Moscow',
    'address': 'ul. Moscow 4',
    'enabled': True,
    'timetable': [{'day_type': 'monday', 'from': '04:00', 'to': '23:00'}],
}

DEPOT_5 = {
    'cabinets': [
        {
            'accumulators_available_for_booking': 29,
            'cabinet_id': 'cabinet_id6',
            'cabinet_type': 'charge_station',
            'empty_cells_available_for_booking': 1,
            'accumulators_count': 30,
            'cells_count': 2,
        },
        {
            'accumulators_available_for_booking': 1,
            'cabinet_id': 'cabinet_id7',
            'cabinet_type': 'cabinet',
            'empty_cells_available_for_booking': 29,
            'accumulators_count': 2,
            'cells_count': 30,
        },
    ],
    'allowed_from_areas': [],
    'depot_id': 'depot_id5',
    'created_at': '2019-12-17T04:38:58+00:00',
    'updated_at': '2019-12-17T04:38:58+00:00',
    'location': {'lat': 10.0, 'lon': 9.0},
    'city': 'Krasnodar',
    'address': 'ul. Krasnodar 5',
    'enabled': True,
    'timetable': [{'day_type': 'monday', 'from': '05:00', 'to': '23:00'}],
}

TEST_OK_RESPONSE_1 = {
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGRlcG90X2lkNQ',
    'depots': [DEPOT_5],
}

TEST_OK_RESPONSE_2 = {
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGRlcG90X2lkMg',
    'depots': [DEPOT_4, DEPOT_3, DEPOT_2],
}

TEST_OK_RESPONSE_3 = {'depots': [DEPOT_1]}

TEST_DEPOT_ID_FILTER = {'depots': [DEPOT_2]}

TEST_CITY_FILTER = {'depots': [DEPOT_5, DEPOT_3, DEPOT_1]}

TEST_ADDRESS_FILTER = {'depots': [DEPOT_5]}

TEST_DEPOT_ID_FILTER_DEPOT = {
    'depots': [DEPOT_5, DEPOT_4, DEPOT_3, DEPOT_2, DEPOT_1],
}

TEST_CITY_FILTER_CO = {'depots': [DEPOT_4, DEPOT_2]}

TEST_ADDRESS_FILTER_NODAR = {'depots': [DEPOT_5, DEPOT_3, DEPOT_1]}

TEST_ENABLED_FILTER_ENABLED = {'depots': [DEPOT_5, DEPOT_4, DEPOT_2, DEPOT_1]}

TEST_ENABLED_FILTER_NOT_ENABLED = {'depots': [DEPOT_3]}


def add_depots(pgsql, number: int = 1):
    for i in range(1, number + 1):
        city = ''
        if i % 2 == 0:
            city = 'Moscow'
        else:
            city = 'Krasnodar'
        enabled = i != 3

        utils.add_depot(
            pgsql,
            {
                'depot_id': f'depot_id{i}',
                'location': (2 * i - 1, 2 * i),
                'created_at': f'2019-12-17T07:38:5{i+3}',
                'updated_at': f'2019-12-17T07:38:5{i+3}',
                'city': city,
                'address': f'ul. {city} {i}',
                'enabled': enabled,
                'timetable': f'{{"(monday,\\"({i}:00:00,23:00:00)\\")"}}',
            },
        )


def is_eq(response, exp_res):
    json_copy = response.json()
    for depot in json_copy['depots']:
        depot['cabinets'].sort(key=lambda cabinet: cabinet['cabinet_id'])
        depot['allowed_from_areas'].sort()

    return json_copy == exp_res


def get_depots_info(request):
    res = {'cabinets': []}
    if 'depot_id1' in request.json['depot_ids']:
        cabinet_1 = {
            'depot_id': 'depot_id1',
            'cabinet_id': 'cabinet_id1',
            'cabinet_type': 'cabinet',
            'accums_available_for_booking': 10,
            'empty_cells_available_for_booking': 20,
            'accumulators_count': 11,
            'cells_count': 21,
            'cabinet_name': 'cabinet_name1',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_1)

        cabinet_2 = {
            'depot_id': 'depot_id1',
            'cabinet_id': 'cabinet_id2',
            'cabinet_type': 'charge_station',
            'accums_available_for_booking': 5,
            'empty_cells_available_for_booking': 25,
            'accumulators_count': 6,
            'cells_count': 26,
            'cabinet_name': 'cabinet_name2',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_2)

    if 'depot_id3' in request.json['depot_ids']:
        cabinet_3 = {
            'depot_id': 'depot_id3',
            'cabinet_id': 'cabinet_id3',
            'cabinet_type': 'cabinet',
            'accums_available_for_booking': 14,
            'empty_cells_available_for_booking': 16,
            'accumulators_count': 15,
            'cells_count': 17,
            'cabinet_name': 'cabinet_name3',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_3)

    if 'depot_id4' in request.json['depot_ids']:
        cabinet_4 = {
            'depot_id': 'depot_id4',
            'cabinet_id': 'cabinet_id4',
            'cabinet_type': 'charge_station_without_id_receiver',
            'accums_available_for_booking': 17,
            'empty_cells_available_for_booking': 13,
            'accumulators_count': 18,
            'cells_count': 14,
            'cabinet_name': 'cabinet_name4',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_4)

        cabinet_5 = {
            'depot_id': 'depot_id4',
            'cabinet_id': 'cabinet_id5',
            'cabinet_type': 'charge_station',
            'accums_available_for_booking': 13,
            'empty_cells_available_for_booking': 17,
            'accumulators_count': 14,
            'cells_count': 18,
            'cabinet_name': 'cabinet_name5',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_5)

    if 'depot_id5' in request.json['depot_ids']:
        cabinet_6 = {
            'depot_id': 'depot_id5',
            'cabinet_id': 'cabinet_id6',
            'cabinet_type': 'charge_station',
            'accums_available_for_booking': 29,
            'empty_cells_available_for_booking': 1,
            'accumulators_count': 30,
            'cells_count': 2,
            'cabinet_name': 'cabinet_name6',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_6)

        cabinet_7 = {
            'depot_id': 'depot_id5',
            'cabinet_id': 'cabinet_id7',
            'cabinet_type': 'cabinet',
            'accums_available_for_booking': 1,
            'empty_cells_available_for_booking': 29,
            'accumulators_count': 2,
            'cells_count': 30,
            'cabinet_name': 'cabinet_name7',
            'created_at': '2019-12-17T04:38:58+00:00',
            'updated_at': '2019-12-17T04:38:58+00:00',
        }
        res['cabinets'].append(cabinet_7)

    return res


@pytest.mark.config(
    SCOOTERS_MISC_DEPOTS_LOCATIONS=[
        {
            'id': 'depot_id1',
            'location': [36.198835, 51.740521],
            'enabled': True,
            'allowed_from_polygons': [
                'cool_grocery_area1',
                'cool_grocery_area2',
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'cursor, limit, json_, db_size',
    [
        pytest.param(None, 20, TEST_EMPTY_RESPONSE, 0),
        pytest.param(None, 1, TEST_OK_RESPONSE_1, 5),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGRlcG90X2lkNQ',
            3,
            TEST_OK_RESPONSE_2,
            5,
        ),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGRlcG90X2lkMg',
            None,
            TEST_OK_RESPONSE_3,
            5,
        ),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGRlcG90X2lkMg',
            1,
            TEST_OK_RESPONSE_3,
            5,
        ),
    ],
)
async def test_ok(
        mockserver, taxi_scooters_misc, pgsql, cursor, limit, json_, db_size,
):
    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1'
        '/admin-api/cabinet/list',
    )
    def mock_scooter_accumulator(request):
        return mockserver.make_response(
            status=200, json=get_depots_info(request),
        )

    add_depots(pgsql, db_size)
    json_request = {}
    if limit:
        json_request['limit'] = limit
    if cursor:
        json_request['cursor'] = cursor
    response = await taxi_scooters_misc.post(ENDPOINT, json=json_request)
    assert response.status_code == 200

    assert is_eq(response, json_)

    if db_size:
        assert mock_scooter_accumulator.times_called == 1
    else:
        assert mock_scooter_accumulator.times_called == 0


@pytest.mark.config(
    SCOOTERS_MISC_DEPOTS_LOCATIONS=[
        {
            'id': 'depot_id1',
            'location': [36.198835, 51.740521],
            'enabled': True,
            'allowed_from_polygons': [
                'cool_grocery_area1',
                'cool_grocery_area2',
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'json_, json_expected',
    [
        pytest.param(
            {
                'limit': 5,
                'depot_id': 'depot_id2',
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
            },
            TEST_DEPOT_ID_FILTER,
            id='depot_id filter',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': 'depot_id55',
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
            },
            TEST_EMPTY_RESPONSE,
            id='depot_id filter, empty response',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': 'Krasnodar',
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
            },
            TEST_CITY_FILTER,
            id='city filter',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': 'ul. Krasnodar 5',
                'address_is_substring': None,
            },
            TEST_ADDRESS_FILTER,
            id='address filter',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': 'depot',
                'depot_id_is_substring': True,
                'city': None,
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
            },
            TEST_DEPOT_ID_FILTER_DEPOT,
            id='depot_id filter depot',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': 'co',
                'city_is_substring': True,
                'address': None,
                'address_is_substring': None,
            },
            TEST_CITY_FILTER_CO,
            id='city filter co',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': 'Nodar',
                'address_is_substring': True,
            },
            TEST_ADDRESS_FILTER_NODAR,
            id='city address Nodar',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': 'depot',
                'depot_id_is_substring': False,
                'city': None,
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
            },
            TEST_EMPTY_RESPONSE,
            id='depot_id filter depot. Empty',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': 'co',
                'city_is_substring': False,
                'address': None,
                'address_is_substring': None,
            },
            TEST_EMPTY_RESPONSE,
            id='city filter co. Empty',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': 'Nodar',
                'address_is_substring': False,
            },
            TEST_EMPTY_RESPONSE,
            id='city address Nodar. Empty',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
                'enabled': True,
            },
            TEST_ENABLED_FILTER_ENABLED,
            id='filter only enabled depots',
        ),
        pytest.param(
            {
                'limit': 5,
                'depot_id': None,
                'depot_id_is_substring': None,
                'city': None,
                'city_is_substring': None,
                'address': None,
                'address_is_substring': None,
                'enabled': False,
            },
            TEST_ENABLED_FILTER_NOT_ENABLED,
            id='filter only disabled depots',
        ),
    ],
)
async def test_filter(
        mockserver, taxi_scooters_misc, pgsql, json_, json_expected,
):
    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1'
        '/admin-api/cabinet/list',
    )
    def mock_scooter_accumulator(request):
        return mockserver.make_response(
            status=200, json=get_depots_info(request),
        )

    add_depots(pgsql, 5)
    response = await taxi_scooters_misc.post(ENDPOINT, json=json_)
    assert response.status_code == 200
    assert is_eq(response, json_expected)
    if json_expected != TEST_EMPTY_RESPONSE:
        assert mock_scooter_accumulator.times_called == 1
    else:
        assert mock_scooter_accumulator.times_called == 0
