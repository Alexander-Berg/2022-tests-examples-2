import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/booking/unbook'


@pytest.mark.parametrize(
    'booking_id, sql_row',
    [
        pytest.param(
            'booking_id1',
            ('booking_id1', 'REVOKED', 'contractor_id1', 'accum_id1'),
            id='booking in CREATED status',
        ),
        pytest.param(
            'booking_id2',
            ('booking_id2', 'REVOKED', 'contractor_id1', None),
            id='booking in REVOKED status',
        ),
    ],
)
async def test_ok(taxi_scooter_accumulator, pgsql, booking_id, sql_row):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': booking_id}, json={},
    )
    assert response.status_code == 200
    assert sql.select_bookings_info(pgsql, booking_id) == ([sql_row])


@pytest.mark.parametrize(
    'booking_id, code, json, sql_row',
    [
        pytest.param(
            'booking_id3',
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
            404,
            {'code': '404', 'message': 'cabinet by booking_id was not found'},
            (),
            id='non existent booking',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator, pgsql, booking_id, code, json, sql_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': booking_id}, json={},
    )
    assert response.status_code == code
    assert response.json() == json
    assert sql.select_bookings_info(pgsql, booking_id) == ([sql_row])
