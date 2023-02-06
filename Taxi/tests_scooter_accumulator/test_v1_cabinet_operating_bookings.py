import typing

ENDPOINT = '/scooter-accumulator/v1/cabinet/operating-bookings'

CABINET_ID1 = 'cabinet_id1'
CONTRACTOR_ID1 = 'contractor_id1'
CONTRACTOR_ID3 = 'contractor_id3'
BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
BOOKING_ID4 = 'booking_id4'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
CELL_ID3 = 'cell_id3'
CELL_ID4 = 'cell_id4'
ACCUMULATOR_ID1 = 'accum_id1'
ACCUMULATOR_ID2 = 'accum_id2'

TEST_OK_RESPONSE = {
    'bookings': [
        {
            'booking_id': BOOKING_ID1,
            'status': 'CREATED',
            'cell_id': CELL_ID1,
            'accumulator_id': ACCUMULATOR_ID1,
        },
        {
            'booking_id': BOOKING_ID2,
            'status': 'IN_PROCESS',
            'cell_id': CELL_ID2,
            'accumulator_id': ACCUMULATOR_ID2,
        },
        {'booking_id': BOOKING_ID3, 'status': 'CREATED', 'cell_id': CELL_ID3},
        {
            'booking_id': BOOKING_ID4,
            'status': 'PROCESSED',
            'cell_id': CELL_ID4,
        },
    ],
    'cabinet_type': 'cabinet_without_validation',
}


async def test_ok(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT,
        params={'cabinet_id': CABINET_ID1, 'contractor_id': CONTRACTOR_ID1},
    )

    assert response.status_code == 200
    assert response.json() == TEST_OK_RESPONSE


TEST_OK_NO_BOOKINGS_RESPONSE: typing.Dict[str, typing.Any] = {
    'bookings': [],
    'cabinet_type': 'cabinet_without_validation',
}


async def test_ok_no_bookings(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT,
        params={'cabinet_id': CABINET_ID1, 'contractor_id': CONTRACTOR_ID3},
    )

    assert response.status_code == 200
    assert response.json() == TEST_OK_NO_BOOKINGS_RESPONSE
