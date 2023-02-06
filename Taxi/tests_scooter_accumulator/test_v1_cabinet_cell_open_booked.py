import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/cell/open-booked'

TESTPOINT_NAME = 'mqtt_publish'

BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
CONTRACTOR_ID1 = 'contractor_id1'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
ACCUMULATOR_ID1 = 'accum_id1'
ACCUMULATOR_ID2 = 'accum_id2'
CABINET_ID = 'cabinet_id1'


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'processed_closed_cell.sql'],
)
async def test_processed_closed_cell(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID1}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'accumulator_was_returned',
        'message': 'accumulator has already been received',
    }
    assert sql.select_bookings_info(pgsql, BOOKING_ID1) == [
        (BOOKING_ID1, 'PROCESSED', CONTRACTOR_ID1, None),
    ]
    assert sql.select_cells_info(
        pgsql, CELL_ID1, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID1, ACCUMULATOR_ID1, BOOKING_ID1, False, 'ok')]


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'ok_previous_closed.sql'],
)
async def test_ok_previous_closed(
        taxi_scooter_accumulator, testpoint, tp_open_booked_previous_ok, pgsql,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_open_booked_previous_ok[data['commands'][0]['command_name']]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID2}, json={},
    )

    assert response.status_code == 200
    assert mqtt_cabinet_response.times_called == 1
    assert sql.select_bookings_info(pgsql, BOOKING_ID1) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, None),
    ]

    assert sql.select_bookings_info(pgsql, BOOKING_ID2) == [
        (BOOKING_ID2, 'IN_PROCESS', CONTRACTOR_ID1, None),
    ]
    assert sql.select_cells_info(
        pgsql, CELL_ID1, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID1, ACCUMULATOR_ID1, BOOKING_ID1, False, 'ok')]
    assert sql.select_cells_info(
        pgsql, CELL_ID2, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID2, None, BOOKING_ID2, True, 'ok')]

    assert sql.select_accumulators_info(pgsql, ACCUMULATOR_ID1, True) == [
        (ACCUMULATOR_ID1, None, CABINET_ID, None, 95),
    ]


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'previous_open.sql'],
)
async def test_ok_previous_open_in_db_closed_by_cabinet(
        taxi_scooter_accumulator, testpoint, tp_open_booked_previous_ok, pgsql,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_open_booked_previous_ok[data['commands'][0]['command_name']]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID2}, json={},
    )

    assert response.status_code == 200
    assert mqtt_cabinet_response.times_called == 2
    assert sql.select_bookings_info(pgsql, BOOKING_ID1) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, None),
    ]
    assert sql.select_bookings_info(pgsql, BOOKING_ID2) == [
        (BOOKING_ID2, 'IN_PROCESS', CONTRACTOR_ID1, None),
    ]
    assert sql.select_cells_info(
        pgsql, CELL_ID1, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID1, ACCUMULATOR_ID1, BOOKING_ID1, False, 'ok')]
    assert sql.select_cells_info(
        pgsql, CELL_ID2, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID2, None, BOOKING_ID2, True, 'ok')]
