import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/admin-api/cabinet/booking/unbook'
CONSUMER_ID = 'consumer_id1'


@pytest.mark.parametrize(
    'booking_id, booking_statuses, sql_row',
    [
        pytest.param(
            'booking_id1',
            ['CREATED'],
            ('booking_id1', 'REVOKED', 'contractor_id1', 'accum_id1'),
            id='booking in CREATED status',
        ),
        pytest.param(
            'booking_id2',
            ['CREATED'],
            ('booking_id2', 'REVOKED', 'contractor_id1', None),
            id='booking in REVOKED status',
        ),
        pytest.param(
            'booking_id3',
            ['CREATED', 'IN_PROCESS'],
            ('booking_id3', 'REVOKED', 'contractor_id1', 'accum_id2'),
            id='booking in IN_PROCESS status',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, booking_id, booking_statuses, sql_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={'booking_id': booking_id, 'expected_statuses': booking_statuses},
        params={'consumer_id': CONSUMER_ID},
    )
    assert response.status_code == 200
    assert sql.select_bookings_info(pgsql, booking_id) == ([sql_row])


@pytest.mark.parametrize(
    'booking_id, booking_statuses, booking_db_row, cell_db_row, accum_db_row',
    [
        pytest.param(
            'booking_id5',
            ['CREATED', 'PROCESSED'],
            ('booking_id5', 'REVOKED', 'contractor_id1', 'accum_id5'),
            ('cell_id5', 'accum_id5', None),
            ('accum_id5', None, 'cabinet_id1', None),
            id='booking (with accumulator) in PROCESSED status',
        ),
        pytest.param(
            'booking_id6',
            ['CREATED', 'IN_PROCESS', 'PROCESSED'],
            ('booking_id6', 'REVOKED', 'contractor_id1', None),
            ('cell_id6', None, None),
            ('accum_id6', 'contractor_id1', None, None),
            id='booking (empty cell) in PROCESSED status',
        ),
    ],
)
async def test_ok_processed(
        taxi_scooter_accumulator,
        pgsql,
        booking_id,
        booking_statuses,
        booking_db_row,
        cell_db_row,
        accum_db_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={'booking_id': booking_id, 'expected_statuses': booking_statuses},
        params={'consumer_id': CONSUMER_ID},
    )
    assert response.status_code == 200
    assert sql.select_bookings_info(pgsql, booking_id) == ([booking_db_row])
    assert sql.select_cells_info(pgsql, cell_db_row[0]) == ([cell_db_row])
    assert sql.select_accumulators_info(pgsql, accum_db_row[0]) == (
        [accum_db_row]
    )


@pytest.mark.parametrize(
    'booking_id, booking_statuses, code, json, sql_row',
    [
        pytest.param(
            'booking_id3',
            ['CREATED', 'PROCESSED'],
            409,
            {
                'code': '409',
                'message': 'booking `booking_id3` in status `IN_PROCESS`',
            },
            ('booking_id3', 'IN_PROCESS', 'contractor_id1', 'accum_id2'),
            id='booking in IN_PROCESS status',
        ),
        pytest.param(
            'booking_id4',
            ['CREATED'],
            404,
            {'code': '404', 'message': 'cabinet by booking_id was not found'},
            (),
            id='non existent booking',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator,
        pgsql,
        booking_id,
        booking_statuses,
        code,
        json,
        sql_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={'booking_id': booking_id, 'expected_statuses': booking_statuses},
        params={'consumer_id': CONSUMER_ID},
    )
    assert response.status_code == code
    assert response.json() == json
    assert sql.select_bookings_info(pgsql, booking_id) == ([sql_row])
