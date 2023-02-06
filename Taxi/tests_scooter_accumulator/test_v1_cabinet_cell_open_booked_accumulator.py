import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/cell/open-booked'

TESTPOINT_NAME = 'mqtt_publish'

BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
CONTRACTOR_ID1 = 'contractor_id1'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
CELL_ID3 = 'cell_id3'
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
        'code': 'accumulator_was_taken',
        'message': 'accumulator has already been taken',
    }
    assert (
        sql.select_bookings_info(pgsql, BOOKING_ID1, select_cell_id=True)
        == [
            (
                BOOKING_ID1,
                'PROCESSED',
                CONTRACTOR_ID1,
                ACCUMULATOR_ID1,
                CELL_ID1,
            ),
        ]
    )
    assert sql.select_cells_info(
        pgsql, CELL_ID1, select_is_open=True, select_error_code=True,
    ) == [(CELL_ID1, None, BOOKING_ID1, False, 'ok')]


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'ok_previous_closed.sql'],
)
async def test_ok_previous_closed(
        taxi_scooter_accumulator,
        testpoint,
        tp_open_booked_acc_previous_ok,
        pgsql,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_open_booked_acc_previous_ok[
            data['commands'][0]['command_name']
        ]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID2}, json={},
    )

    assert response.status_code == 200
    assert mqtt_cabinet_response.times_called == 1
    assert sql.select_bookings_info(pgsql, select_cell_id=True) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID1, CELL_ID1),
        (BOOKING_ID2, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID2, CELL_ID2),
    ]
    assert (
        sql.select_cells_info(
            pgsql, select_is_open=True, select_error_code=True,
        )
        == [
            (CELL_ID1, None, BOOKING_ID1, False, 'ok'),
            (CELL_ID2, ACCUMULATOR_ID2, BOOKING_ID2, True, 'ok'),
        ]
    )


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'previous_open.sql'],
)
async def test_ok_previous_open_in_db_closed_by_cabinet(
        taxi_scooter_accumulator,
        testpoint,
        tp_open_booked_acc_previous_ok,
        pgsql,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_open_booked_acc_previous_ok[
            data['commands'][0]['command_name']
        ]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID2}, json={},
    )

    assert response.status_code == 200
    assert mqtt_cabinet_response.times_called == 2
    assert sql.select_bookings_info(pgsql, select_cell_id=True) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID1, CELL_ID1),
        (BOOKING_ID2, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID2, CELL_ID2),
        (BOOKING_ID3, 'IN_PROCESS', CONTRACTOR_ID1, None, CELL_ID3),
    ]
    assert (
        sql.select_cells_info(
            pgsql, select_is_open=True, select_error_code=True,
        )
        == [
            (CELL_ID1, None, BOOKING_ID1, False, 'ok'),
            (CELL_ID2, ACCUMULATOR_ID2, BOOKING_ID2, True, 'ok'),
            (CELL_ID3, None, BOOKING_ID3, False, 'ok'),
        ]
    )


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'previous_open.sql'],
)
async def test_cabinet_is_not_responding(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID2}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'cabinet_is_not_responding',
        'message': 'cabinet is not responding',
    }
    assert sql.select_bookings_info(pgsql, select_cell_id=True) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID1, CELL_ID1),
        (BOOKING_ID2, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID2, CELL_ID2),
        (BOOKING_ID3, 'IN_PROCESS', CONTRACTOR_ID1, None, CELL_ID3),
    ]
    assert (
        sql.select_cells_info(
            pgsql,
            select_is_open=True,
            select_error_code=True,
            select_error_response_number=True,
        )
        == [
            (
                CELL_ID1,
                ACCUMULATOR_ID1,
                BOOKING_ID1,
                True,
                'cabinet_is_offline',
                3,
            ),
            (
                CELL_ID2,
                ACCUMULATOR_ID2,
                BOOKING_ID2,
                False,
                'cabinet_is_not_responding',
                1,
            ),
            (CELL_ID3, None, BOOKING_ID3, False, 'ok', 0),
        ]
    )


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'cabinet_is_offline.sql'],
)
async def test_cabinet_is_offline(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID1}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'cabinet_is_offline',
        'message': 'cabinet is not responding',
    }
    assert sql.select_bookings_info(pgsql, select_cell_id=True) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID1, CELL_ID1),
    ]
    assert (
        sql.select_cells_info(
            pgsql,
            select_is_open=True,
            select_error_code=True,
            select_error_response_number=True,
        )
        == [
            (
                CELL_ID1,
                ACCUMULATOR_ID1,
                BOOKING_ID1,
                False,
                'cabinet_is_offline',
                3,
            ),
        ]
    )


@pytest.mark.pgsql(
    'scooter_accumulator', files=['default.sql', 'non_closed_cell_exists.sql'],
)
async def test_non_closed_cell_exists(
        taxi_scooter_accumulator,
        pgsql,
        testpoint,
        tp_open_booked_acc_door_is_open,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_open_booked_acc_door_is_open

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID1}, json={},
    )

    assert response.status_code == 400
    assert mqtt_cabinet_response.times_called == 1
    assert response.json() == {
        'code': 'previous_cell_was_not_closed',
        'message': f'please close cell `{CELL_ID1}` before open next',
        'cell_id': CELL_ID1,
    }
    assert sql.select_bookings_info(
        pgsql, BOOKING_ID1, select_cell_id=True,
    ) == [(BOOKING_ID1, 'CREATED', CONTRACTOR_ID1, ACCUMULATOR_ID2, CELL_ID2)]
    assert (
        sql.select_cells_info(
            pgsql, select_is_open=True, select_error_code=True,
        )
        == [
            (CELL_ID1, ACCUMULATOR_ID1, None, True, 'ok'),
            (CELL_ID2, ACCUMULATOR_ID2, BOOKING_ID1, False, 'ok'),
        ]
    )


@pytest.mark.pgsql(
    'scooter_accumulator', files=['accumulator_is_not_exists.sql'],
)
async def test_accumulator_is_not_exists(
        taxi_scooter_accumulator,
        pgsql,
        testpoint,
        tp_open_booked_acc_previous_bad,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_open_booked_acc_previous_bad[
            data['commands'][0]['command_name']
        ]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID2}, json={},
    )

    assert response.status_code == 400
    assert mqtt_cabinet_response.times_called == 2
    assert response.json() == {
        'code': 'cabinet_is_not_responding',
        'message': (
            'cabinet response error: requested cell_id `cell_id2`, but '
            'response contains cell_id `cell_id1`'
        ),
    }
    assert (
        sql.select_bookings_info(pgsql, BOOKING_ID1, select_cell_id=True)
        == [
            (
                BOOKING_ID1,
                'IN_PROCESS',
                CONTRACTOR_ID1,
                ACCUMULATOR_ID1,
                CELL_ID1,
            ),
        ]
    )
    assert (
        sql.select_cells_info(
            pgsql, select_is_open=True, select_error_code=True,
        )
        == [
            (CELL_ID1, None, BOOKING_ID1, False, 'ok'),
            (
                CELL_ID2,
                ACCUMULATOR_ID2,
                BOOKING_ID2,
                False,
                'cabinet_is_not_responding',
            ),
        ]
    )


@pytest.mark.pgsql('scooter_accumulator', files=['evolve_created_status.sql'])
async def test_evolve_created_status(
        taxi_scooter_accumulator, pgsql, testpoint,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return None

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID1}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'cabinet_is_not_responding',
        'message': 'cabinet is not responding',
    }
    assert mqtt_cabinet_response.times_called == 1

    assert sql.select_bookings_info(pgsql) == [
        (BOOKING_ID1, 'IN_PROCESS', CONTRACTOR_ID1, ACCUMULATOR_ID1),
    ]

    assert sql.select_cells_info(
        pgsql,
        select_is_open=True,
        select_error_code=True,
        select_error_response_number=True,
    ) == [(CELL_ID1, None, BOOKING_ID1, False, 'cabinet_is_not_responding', 1)]
