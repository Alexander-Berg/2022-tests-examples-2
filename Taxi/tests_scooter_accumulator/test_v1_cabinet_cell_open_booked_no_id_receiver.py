import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/cell/open-booked'

TESTPOINT_NAME = 'mqtt_publish'

BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
CONTRACTOR_ID1 = 'contractor_id1'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
CELL_ID3 = 'cell_id3'


async def test_ok_previous_open(
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
    ) == [(CELL_ID1, 'fake_id1', BOOKING_ID1, False, 'ok')]
    assert sql.select_cells_info(
        pgsql, CELL_ID2, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID2, None, BOOKING_ID2, True, 'ok')]


@pytest.mark.pgsql('scooter_accumulator', files=['ok_previous_broken.sql'])
async def test_ok_previous_broken(
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
        pgsql,
        CELL_ID3,
        select_is_open=True,
        select_error_code=True,
        select_error_response_number=True,
    ) == [(CELL_ID3, None, BOOKING_ID1, True, 'cabinet_is_not_responding', 1)]
    assert sql.select_cells_info(
        pgsql, CELL_ID2, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID2, None, BOOKING_ID2, True, 'ok')]
