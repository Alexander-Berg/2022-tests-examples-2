import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/bookings/cell/set-error-code'


@pytest.mark.parametrize(
    'booking_id, mark_command, cell',
    [
        pytest.param(
            'booking_id1',
            'mark_broken',
            (
                'cell_id1',
                'accum_id1',
                'booking_id1',
                'cell_broken_marked_by_client',
            ),
            id='mark as broken',
        ),
        pytest.param(
            'booking_id3',
            'mark_ok',
            ('cell_id3', None, 'booking_id3', 'ok'),
            id='mark as ok',
        ),
        pytest.param(
            'booking_id3',
            'mark_broken',
            ('cell_id3', None, 'booking_id3', 'cell_broken_marked_by_client'),
            id='mark as broken, retry',
        ),
        pytest.param(
            'booking_id1',
            'mark_ok',
            ('cell_id1', 'accum_id1', 'booking_id1', 'ok'),
            id='mark as ok, retry',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, booking_id, mark_command, cell,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_id': booking_id},
        json={'cell_error_code_mark': mark_command},
    )

    assert response.status_code == 200
    assert response.json() == {'cell_id': cell[0]}

    cell_db = sql.select_cells_info(
        pgsql, cell_id=cell[0], select_error_code=True,
    )

    assert cell_db[0] == cell


@pytest.mark.parametrize(
    'booking_id, mark_command, message',
    [
        pytest.param(
            'booking_id2',
            'mark_broken',
            'CellsMarkAsBrokenByBooking failed: booking_id `booking_id2`,'
            ' cell_id: `cell_id2`, cabinet_id: `cabinet_id1`,'
            ' previous eror_code: `cabinet_is_not_responding`,'
            ' trying to set error_code: `cell_broken_marked_by_client`',
            id='try mark broken, previous error_code incompatible',
        ),
        pytest.param(
            'booking_id2',
            'mark_ok',
            'CellsMarkAsBrokenByBooking failed: booking_id `booking_id2`,'
            ' cell_id: `cell_id2`, cabinet_id: `cabinet_id1`,'
            ' previous eror_code: `cabinet_is_not_responding`,'
            ' trying to set error_code: `ok`',
            id='try mark ok, previous error_code incompatible',
        ),
    ],
)
async def test_prev_code_incompatible(
        taxi_scooter_accumulator, pgsql, booking_id, mark_command, message,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_id': booking_id},
        json={'cell_error_code_mark': mark_command},
    )

    assert response.status_code == 400
    assert response.json()['message'] == message

    cell_db = sql.select_cells_info(
        pgsql, cell_id='cell_id2', select_error_code=True,
    )

    assert cell_db[0] == (
        'cell_id2',
        None,
        'booking_id2',
        'cabinet_is_not_responding',
    )


async def test_booking_does_not_exists(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_id': 'booking_id123'},
        json={'cell_error_code_mark': 'mark_broken'},
    )

    assert response.status_code == 404
    assert (
        response.json()['message']
        == 'booking_id `booking_id123` doesn\'t exist'
    )
