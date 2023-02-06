import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/depot/accumulator/book'

BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
BOOKING_ID4 = 'booking_id4'
BOOKING_ID5 = 'booking_id5'
BOOKING_ID6 = 'booking_id6'
BOOKING_ID7 = 'booking_id7'
BOOKING_ID100 = 'booking_id100'
BOOKING_ID101 = 'booking_id101'
BOOKING_ID102 = 'booking_id102'
BOOKING_ID103 = 'booking_id103'

BOOKING1_AUTOMATIC = {
    'booking_id': BOOKING_ID1,
    'status': 'CREATED',
    'cell_id': 'cell_id3',
    'accumulator_id': 'accum_id3',
    'cabinet_id': 'cabinet_id2',
    'cells_count': 1,
    'cabinet_type': 'charge_station',
}

BOOKING2_AUTOMATIC = {
    'booking_id': BOOKING_ID2,
    'status': 'CREATED',
    'cell_id': 'cell_id4',
    'accumulator_id': 'accum_id4',
    'cabinet_id': 'cabinet_id2',
    'cells_count': 1,
    'cabinet_type': 'charge_station',
}

BOOKING3_AUTOMATIC = {
    'booking_id': BOOKING_ID3,
    'status': 'CREATED',
    'cell_id': 'cell_id5',
    'accumulator_id': 'accum_id5',
    'cabinet_id': 'cabinet_id3',
    'cells_count': 1,
    'cabinet_type': 'charge_station_without_id_receiver',
}

BOOKING1_MANUAL = {
    'booking_id': BOOKING_ID1,
    'status': 'CREATED',
    'cell_id': 'cell_id1',
    'accumulator_id': 'accum_id1',
    'cabinet_id': 'cabinet_id1',
    'cells_count': 1,
    'cabinet_type': 'cabinet',
}

BOOKING2_MANUAL = {
    'booking_id': BOOKING_ID2,
    'status': 'CREATED',
    'cell_id': 'cell_id2',
    'accumulator_id': 'accum_id2',
    'cabinet_id': 'cabinet_id1',
    'cells_count': 1,
    'cabinet_type': 'cabinet',
}

BOOKING3_MANUAL = {
    'booking_id': BOOKING_ID3,
    'status': 'CREATED',
    'cell_id': 'cell_id6',
    'accumulator_id': 'accum_id6',
    'cabinet_id': 'cabinet_id1',
    'cells_count': 1,
    'cabinet_type': 'cabinet',
}

BOOKING4_MANUAL = {
    'booking_id': BOOKING_ID4,
    'status': 'CREATED',
    'cell_id': 'cell_id7',
    'accumulator_id': 'accum_id7',
    'cabinet_id': 'cabinet_id1',
    'cells_count': 1,
    'cabinet_type': 'cabinet',
}

BOOKING5_MANUAL = {
    'booking_id': BOOKING_ID5,
    'status': 'CREATED',
    'cell_id': 'cell_id9',
    'accumulator_id': 'accum_id9',
    'cabinet_id': 'cabinet_id4',
    'cells_count': 1,
    'cabinet_type': 'cabinet',
}

BOOKING100_RETRY = {
    'booking_id': BOOKING_ID100,
    'status': 'CREATED',
    'cell_id': 'cell_id8',
    'accumulator_id': 'accum_id8',
    'cabinet_id': 'cabinet_id2',
    'cells_count': 1,
    'cabinet_type': 'charge_station',
}

BOOKING101_RETRY = {
    'booking_id': BOOKING_ID101,
    'status': 'CREATED',
    'cell_id': 'cell_id10',
    'accumulator_id': 'accum_id10',
    'cabinet_id': 'cabinet_id2',
    'cells_count': 1,
    'cabinet_type': 'charge_station',
}

BOOKING102_RETRY = {
    'booking_id': BOOKING_ID102,
    'status': 'CREATED',
    'cell_id': 'cell_id11',
    'accumulator_id': 'accum_id11',
    'cabinet_id': 'cabinet_id2',
    'cells_count': 1,
    'cabinet_type': 'charge_station',
}

BOOKING103_RETRY = {
    'booking_id': BOOKING_ID103,
    'status': 'CREATED',
    'cell_id': 'cell_id12',
    'accumulator_id': 'accum_id12',
    'cabinet_id': 'cabinet_id2',
    'cells_count': 1,
    'cabinet_type': 'charge_station',
}

RESPONSE_JSON_ONE_AUTOMATIC = {
    'bookings': [BOOKING1_AUTOMATIC, BOOKING2_AUTOMATIC],
}

RESPONSE_JSON_TWO_AUTOMATIC = {
    'bookings': [BOOKING1_AUTOMATIC, BOOKING2_AUTOMATIC, BOOKING3_AUTOMATIC],
}

RESPONSE_JSON_ONE_MANUAL = {
    'bookings': [
        BOOKING1_MANUAL,
        BOOKING2_MANUAL,
        BOOKING3_MANUAL,
        BOOKING4_MANUAL,
    ],
}

RESPONSE_JSON_TWO_MANUAL = {
    'bookings': [
        BOOKING1_MANUAL,
        BOOKING2_MANUAL,
        BOOKING3_MANUAL,
        BOOKING4_MANUAL,
        BOOKING5_MANUAL,
    ],
}

RESPONSE_JSON_RETRY = {'bookings': [BOOKING100_RETRY, BOOKING101_RETRY]}


def is_eq(response, exp_res):
    vals = sorted(
        response.json()['bookings'], key=lambda booking: booking['booking_id'],
    )

    return vals == exp_res['bookings']


@pytest.mark.parametrize(
    'json_, response_expected',
    [
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [BOOKING_ID1, BOOKING_ID2],
                'bookings_must_be_in_one_cabinet': False,
            },
            RESPONSE_JSON_ONE_AUTOMATIC,
            id='book in one automatic cabinet',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3],
            },
            RESPONSE_JSON_TWO_AUTOMATIC,
            id='book in two automatic cabinets',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [
                    BOOKING_ID1,
                    BOOKING_ID2,
                    BOOKING_ID3,
                    BOOKING_ID4,
                ],
                'bookings_must_be_in_one_cabinet': True,
            },
            RESPONSE_JSON_ONE_MANUAL,
            id='book in one manual cabinet',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [
                    BOOKING_ID1,
                    BOOKING_ID2,
                    BOOKING_ID3,
                    BOOKING_ID4,
                    BOOKING_ID5,
                ],
            },
            RESPONSE_JSON_TWO_MANUAL,
            id='book in two manuals cabinet',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [BOOKING_ID100, BOOKING_ID101],
            },
            RESPONSE_JSON_RETRY,
            id='emulate retry',
        ),
    ],
)
async def test_ok(taxi_scooter_accumulator, pgsql, json_, response_expected):
    response = await taxi_scooter_accumulator.post(ENDPOINT, json=json_)

    assert response.status_code == 200

    response_json = response.json()

    assert is_eq(response, response_expected)

    for booking in response_json['bookings']:
        assert (
            sql.select_bookings_info(pgsql, booking['booking_id'], True)
            == [
                (
                    booking['booking_id'],
                    'CREATED',
                    None,
                    booking['accumulator_id'],
                    booking['cell_id'],
                ),
            ]
        )
        assert sql.select_cells_info(pgsql, booking['cell_id']) == [
            (
                booking['cell_id'],
                booking['accumulator_id'],
                booking['booking_id'],
            ),
        ]


@pytest.mark.parametrize(
    'json_, code, message, error_code,',
    [
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [
                    BOOKING_ID1,
                    BOOKING_ID2,
                    BOOKING_ID3,
                    BOOKING_ID4,
                    BOOKING_ID5,
                    BOOKING_ID6,
                    BOOKING_ID7,
                ],
            },
            'not_enough_accumulators_bookable',
            'Not enough accumulators available, '
            'there are only 3 in automatic cabinets '
            'and 5 in manual cabinets,'
            ' but 7 accumulators were requested.',
            400,
            id='not enough accumulators bookable',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [
                    BOOKING_ID1,
                    BOOKING_ID2,
                    BOOKING_ID3,
                    BOOKING_ID4,
                    BOOKING_ID5,
                ],
                'bookings_must_be_in_one_cabinet': True,
            },
            'not_enough_accumulators_bookable',
            'Impossible to find strongly one '
            'cabinet with at least 5 bookable accumulators. '
            'The biggest one has 4 bookable accumulators.',
            400,
            id='not enough accumulators bookable, requied in one cabinet',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id_not_existing',
                'booking_ids': [BOOKING_ID1],
            },
            'no_cabinets_in_depot',
            'No cabinets in depot `depot_id_not_existing`.',
            400,
            id='not enough accumulators bookable',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [BOOKING_ID100, BOOKING_ID1],
            },
            '409',
            'Booking with id `booking_id100` already'
            ' exists in status `CREATED`.\n',
            409,
            id='not all bookings already exists',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [
                    BOOKING_ID100,
                    BOOKING_ID101,
                    BOOKING_ID102,
                    BOOKING_ID103,
                ],
            },
            '409',
            'Booking with id `booking_id102` '
            'already exists in status `IN_PROCESS`.\n'
            'Booking with id `booking_id103` '
            'already exists in status `PROCESSED`.\n',
            409,
            id='not all existing bookings are CREATED',
        ),
        pytest.param(
            {
                'depot_id': 'depot_id1',
                'booking_ids': [BOOKING_ID100, BOOKING_ID1],
            },
            '409',
            'Booking with id `booking_id100` '
            'already exists in status `CREATED`.\n',
            409,
            id='not all bookings already exists',
        ),
    ],
)
async def test_bad(taxi_scooter_accumulator, json_, error_code, code, message):
    response = await taxi_scooter_accumulator.post(ENDPOINT, json=json_)

    assert response.status_code == error_code

    assert response.json()['code'] == code
    assert response.json()['message'] == message
