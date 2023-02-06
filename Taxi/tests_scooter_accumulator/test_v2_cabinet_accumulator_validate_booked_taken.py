import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v2/cabinet/accumulator/validate-booked-taken'

TESTPOINT_NAME = 'mqtt_publish'

CONTRACTOR_ID1 = 'contractor_id1'
CABINET_ID1 = 'cabinet_id1'
BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
BOOKING_ID4 = 'booking_id4'
BOOKING_ID5 = 'booking_id5'
BOOKING_ID6 = 'booking_id6'
ACCUMULATOR_ID1 = 'accum_id1'
ACCUMULATOR_ID2 = 'accum_id2'
ACCUMULATOR_ID3 = 'accum_id3'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
CELL_ID3 = 'cell_id3'

REBOOK_4 = {
    'booking_id': BOOKING_ID4,
    'cabinet_id': CABINET_ID1,
    'cabinet_type': 'cabinet',
    'cell_id': CELL_ID1,
    'cells_count': 1,
    'status': 'CREATED',
}
REBOOK_5 = {
    'booking_id': BOOKING_ID5,
    'cabinet_id': CABINET_ID1,
    'cabinet_type': 'cabinet',
    'cell_id': CELL_ID2,
    'cells_count': 1,
    'status': 'CREATED',
}
REBOOK_6 = {
    'booking_id': BOOKING_ID6,
    'cabinet_id': CABINET_ID1,
    'cabinet_type': 'cabinet',
    'cell_id': CELL_ID3,
    'cells_count': 1,
    'status': 'CREATED',
}


@pytest.mark.pgsql('scooter_accumulator', files=['ok.sql'])
async def test_ok(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={'booking_ids': [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3]},
    )

    assert response.status_code == 200
    assert response.json() == {'bookings': []}
    assert sql.select_bookings_info(pgsql) == [
        (BOOKING_ID1, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID1),
        (BOOKING_ID2, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID2),
        (BOOKING_ID3, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID3),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, CONTRACTOR_ID1, None, None),
        (ACCUMULATOR_ID2, CONTRACTOR_ID1, None, None),
        (ACCUMULATOR_ID3, CONTRACTOR_ID1, None, None),
    ]
    assert sql.select_cells_info(pgsql) == [
        (CELL_ID1, None, None),
        (CELL_ID2, None, None),
        (CELL_ID3, None, None),
    ]


@pytest.mark.pgsql('scooter_accumulator', files=['ok_rebook.sql'])
async def test_ok_rebook(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'booking_ids': [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3],
            'rebooking_ids': [BOOKING_ID4, BOOKING_ID5, BOOKING_ID6],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'bookings': [REBOOK_4, REBOOK_5, REBOOK_6]}
    assert sql.select_bookings_info(pgsql) == [
        (BOOKING_ID1, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID1),
        (BOOKING_ID2, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID2),
        (BOOKING_ID3, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID3),
        (BOOKING_ID4, 'CREATED', CONTRACTOR_ID1, None),
        (BOOKING_ID5, 'CREATED', CONTRACTOR_ID1, None),
        (BOOKING_ID6, 'CREATED', CONTRACTOR_ID1, None),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, CONTRACTOR_ID1, None, None),
        (ACCUMULATOR_ID2, CONTRACTOR_ID1, None, None),
    ]
    assert sql.select_cells_info(pgsql) == [
        (CELL_ID1, None, BOOKING_ID4),
        (CELL_ID2, None, BOOKING_ID5),
        (CELL_ID3, None, BOOKING_ID6),
    ]


@pytest.mark.pgsql('scooter_accumulator', files=['ok_rebook_retry.sql'])
async def test_ok_rebook_retry(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'booking_ids': [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3],
            'rebooking_ids': [BOOKING_ID4, BOOKING_ID5, BOOKING_ID6],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'bookings': [REBOOK_4, REBOOK_5, REBOOK_6]}
    assert sql.select_bookings_info(pgsql, select_comment=True) == [
        (BOOKING_ID1, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID1, None),
        (BOOKING_ID2, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID2, None),
        (BOOKING_ID3, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID3, None),
        (BOOKING_ID4, 'CREATED', CONTRACTOR_ID1, None, None),
        (BOOKING_ID5, 'CREATED', CONTRACTOR_ID1, None, None),
        (BOOKING_ID6, 'CREATED', CONTRACTOR_ID1, None, None),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, CONTRACTOR_ID1, None, None),
        (ACCUMULATOR_ID2, CONTRACTOR_ID1, None, None),
    ]
    assert sql.select_cells_info(pgsql) == [
        (CELL_ID1, None, BOOKING_ID4),
        (CELL_ID2, None, BOOKING_ID5),
        (CELL_ID3, None, BOOKING_ID6),
    ]


@pytest.mark.pgsql('scooter_accumulator', files=['ok_rebook.sql'])
async def test_bad_rebook(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'booking_ids': [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3],
            'rebooking_ids': [BOOKING_ID4, BOOKING_ID5],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'error',
        'message': 'count of rebooking_ids differs from count of booking_ids',
    }
    assert sql.select_bookings_info(pgsql) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID1),
        (BOOKING_ID2, 'PROCESSED', CONTRACTOR_ID1, ACCUMULATOR_ID2),
        (BOOKING_ID3, 'PROCESSED', CONTRACTOR_ID1, ACCUMULATOR_ID3),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, None, CABINET_ID1, None),
        (ACCUMULATOR_ID2, CONTRACTOR_ID1, None, None),
    ]
    assert sql.select_cells_info(pgsql) == [
        (CELL_ID1, None, BOOKING_ID1),
        (CELL_ID2, None, BOOKING_ID2),
        (CELL_ID3, None, BOOKING_ID3),
    ]


@pytest.mark.pgsql('scooter_accumulator', files=['ok_opened_cell.sql'])
async def test_ok_opened_cell(
        taxi_scooter_accumulator,
        pgsql,
        testpoint,
        tp_validate_cell_without_accum,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cell_status(data):
        return tp_validate_cell_without_accum

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, json={'booking_ids': [BOOKING_ID1]},
    )

    assert response.status_code == 200
    assert mqtt_cell_status.times_called == 1
    assert response.json() == {'bookings': []}
    assert sql.select_bookings_info(pgsql) == [
        (BOOKING_ID1, 'VALIDATED', CONTRACTOR_ID1, ACCUMULATOR_ID1),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, CONTRACTOR_ID1, None, None),
    ]
    assert sql.select_cells_info(pgsql) == [(CELL_ID1, None, None)]


@pytest.mark.pgsql(
    'scooter_accumulator', files=['booking_without_accumulator.sql'],
)
async def test_booking_without_accumulator(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, json={'booking_ids': [BOOKING_ID1]},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'booking_without_accumulator',
        'booking_id': BOOKING_ID1,
    }


@pytest.mark.pgsql('scooter_accumulator', files=['cell_is_open.sql'])
async def test_cell_is_open(
        taxi_scooter_accumulator, testpoint, tp_validate_cell_is_open,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cell_status(data):
        return tp_validate_cell_is_open

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, json={'booking_ids': [BOOKING_ID1, BOOKING_ID2]},
    )

    assert response.status_code == 400
    assert mqtt_cell_status.times_called == 1
    assert response.json() == {
        'code': 'cell_is_open',
        'booking_id': BOOKING_ID1,
    }


@pytest.mark.pgsql(
    'scooter_accumulator', files=['accumulator_was_not_taken.sql'],
)
async def test_accumulator_was_not_taken(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={'booking_ids': [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3]},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'accumulator_was_not_taken',
        'booking_id': BOOKING_ID3,
    }


@pytest.mark.pgsql('scooter_accumulator', files=['non_processed_booking.sql'])
async def test_non_processed_booking(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, json={'booking_ids': [BOOKING_ID1]},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'non_processed_booking',
        'booking_id': BOOKING_ID1,
        'message': 'booking state: kCreated',
    }
