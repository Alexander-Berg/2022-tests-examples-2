import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/booking/contractor'

CONTRACTOR_ID1 = 'contractor_id1'
CONTRACTOR_ID2 = 'contractor_id2'
CONTRACTOR_ID3 = 'contractor_id3'
BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
BOOKING_ID_NONEXISTENT = 'nonexistent_booking_id'


def select_booking_info(pgsql, booking_id):
    db = pgsql['scooter_accumulator'].cursor()
    db.execute(
        'SELECT booking_id, contractor_id '
        'FROM scooter_accumulator.bookings '
        f'WHERE booking_id = \'{booking_id}\';',
    )

    return db.fetchall()


@pytest.mark.parametrize(
    'booking_id, contractor_id, booking_db_row',
    [
        pytest.param(
            BOOKING_ID1,
            CONTRACTOR_ID1,
            (BOOKING_ID1, 'CREATED', CONTRACTOR_ID1, 'accum_id4'),
            id='set contractor when he was not set',
        ),
        pytest.param(
            BOOKING_ID2,
            CONTRACTOR_ID3,
            (BOOKING_ID2, 'CREATED', CONTRACTOR_ID3, 'accum_id2'),
            id='set contractor when he has already been set',
        ),
    ],
)
@pytest.mark.pgsql(
    'scooter_accumulator',
    files=['pg_scooter_accumulator.sql', 'bookings.sql'],
)
async def test_ok(
        taxi_scooter_accumulator,
        pgsql,
        booking_id,
        contractor_id,
        booking_db_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_id': booking_id, 'contractor_id': contractor_id},
    )

    assert response.status_code == 200
    assert sql.select_bookings_info(pgsql, booking_id) == [booking_db_row]


@pytest.mark.parametrize(
    'booking_id, status_code, response_json, booking_db_row',
    [
        pytest.param(
            BOOKING_ID_NONEXISTENT,
            404,
            {
                'code': '404',
                'message': (
                    f'booking_id `{BOOKING_ID_NONEXISTENT}` does not exist'
                ),
            },
            (),
            id='non-existent booking_id',
        ),
        pytest.param(
            BOOKING_ID3,
            409,
            {
                'code': '409',
                'message': (
                    'set contractor is not allowed when '
                    'booking_status is set in `IN_PROCESS`'
                ),
            },
            (BOOKING_ID3, 'IN_PROCESS', CONTRACTOR_ID3, 'accum_id3'),
            id=(
                'booking_status has a value where '
                'we prohibit change contractor_id'
            ),
        ),
    ],
)
@pytest.mark.pgsql(
    'scooter_accumulator',
    files=['pg_scooter_accumulator.sql', 'bookings.sql'],
)
async def test_bad(
        taxi_scooter_accumulator,
        pgsql,
        booking_id,
        status_code,
        response_json,
        booking_db_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_id': booking_id, 'contractor_id': CONTRACTOR_ID1},
    )

    assert response.status_code == status_code
    assert response.json() == response_json
    assert sql.select_bookings_info(pgsql, booking_id) == [booking_db_row]
