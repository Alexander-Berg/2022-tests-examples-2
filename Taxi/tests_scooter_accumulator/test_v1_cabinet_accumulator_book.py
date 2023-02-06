import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/accumulator/book'

CABINET_ID1 = 'cabinet_id1'
CABINET_ID2 = 'cabinet_id2'
CABINET_ID_NONEXISTENT = 'nonexistent_cabinet_id'
BOOKING_ID_CREATED = 'booking_id_created'
BOOKING_ID_CREATED2 = 'booking_id_created2'
BOOKING_ID_REVOKED = 'booking_id_revoked'
BOOKING_ID_NEW = 'booking_new'


@pytest.mark.parametrize(
    'input_params, cell_rows, booking_rows',
    [
        pytest.param(
            {
                'count': 1,
                'cabinet_id': CABINET_ID1,
                'booking_id': BOOKING_ID_NEW,
            },
            [('cell_id2', 'accum_id2', BOOKING_ID_NEW)],
            [(BOOKING_ID_NEW, 'CREATED', None, 'accum_id2')],
            id='create new booking',
        ),
        pytest.param(
            {
                'count': 1,
                'cabinet_id': CABINET_ID1,
                'booking_id': BOOKING_ID_CREATED,
            },
            [('cell_id1', 'accum_id1', BOOKING_ID_CREATED)],
            [(BOOKING_ID_CREATED, 'CREATED', None, 'accum_id1')],
            id='emulate retry book: book with already CREATED booking_id',
        ),
        pytest.param(
            {
                'count': 1,
                'cabinet_id': CABINET_ID2,
                'booking_id': BOOKING_ID_CREATED2,
            },
            [('cell_id4', 'accum_id4', BOOKING_ID_CREATED2)],
            [(BOOKING_ID_CREATED2, 'CREATED', None, 'accum_id4')],
            id='emulate retry book, '
            'but also there are no available accumulators',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, input_params, cell_rows, booking_rows,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': input_params['cabinet_id'],
            'booking_id': input_params['booking_id'],
            'accumulators_count': input_params['count'],
        },
        json={},
    )

    assert response.status_code == 200
    assert sql.select_bookings_info(pgsql, booking_rows[0][0]) == booking_rows
    assert sql.select_cells_info(pgsql, cell_rows[0][0]) == cell_rows


@pytest.mark.parametrize(
    'cabinet_id, booking_id, accumulators_count, code, message',
    [
        pytest.param(
            CABINET_ID1,
            BOOKING_ID_CREATED,
            2,
            400,
            'booking only 1 cell/accumulator per booking is supported',
            id='2 accumulators count, but only 1 per booking is allowed',
        ),
        pytest.param(
            CABINET_ID2,
            BOOKING_ID_CREATED,
            1,
            409,
            'booking with status `CREATED` of 1 accumulators '
            f'in cabinet_id `{CABINET_ID1}` has same booking_id',
            id='existent booking_id, but with wrong cabinet_id',
        ),
        pytest.param(
            CABINET_ID1,
            BOOKING_ID_REVOKED,
            1,
            409,
            'booking with status `REVOKED` of 1 accumulators '
            f'in cabinet_id `{CABINET_ID1}` has same booking_id',
            id='existent booking_id, but status is REVOKED',
        ),
        pytest.param(
            CABINET_ID_NONEXISTENT,
            BOOKING_ID_NEW,
            1,
            400,
            'not enough available accumulators, available count: 0',
            id='try to book in non-existent cabinet',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator,
        cabinet_id,
        booking_id,
        accumulators_count,
        code,
        message,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': cabinet_id,
            'booking_id': booking_id,
            'accumulators_count': accumulators_count,
        },
        json={},
    )

    assert response.status_code == code
    assert response.json() == {'code': str(code), 'message': message}
