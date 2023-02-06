import pytest

from . import sql

ENDPOINT = (
    '/scooter-accumulator/v1/fallback-api/cabinet/booking/'
    'accumulator-return-processed'
)

CONTRACTOR_ID = 'contractor_id1'
CONTRACTOR_ID_NON_EXISTENT = 'contractor_id_non_existent'
CABINET_ID = 'cabinet_id1'
CONSUMER_ID = 'consumer_id1'


@pytest.mark.parametrize(
    'accumulator_id, expected_bookings',
    [
        pytest.param(
            'accum_id1',
            ['booking_id1', 'booking_id2'],
            id='set states as if PROCESSED for CREATED or IN_PROCESS booking, '
            'selected randomly',
        ),
        pytest.param(
            'accum_id3',
            ['booking_id3'],
            id='check idempotency for PROCESSED booking',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, accumulator_id, expected_bookings,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': CABINET_ID,
            'contractor_id': CONTRACTOR_ID,
            'accumulator_id': accumulator_id,
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    booking_id = response_json['booking_id']
    cell_id = response_json['cell_id']

    assert booking_id in expected_bookings
    assert 'accumulator_id' not in response_json
    assert response_json['status'] == 'PROCESSED'

    assert sql.select_bookings_info(pgsql, booking_id) == [
        (booking_id, 'PROCESSED', CONTRACTOR_ID, None),
    ]
    assert sql.select_cells_info(pgsql, cell_id) == [
        (cell_id, accumulator_id, booking_id),
    ]
    assert sql.select_accumulators_info(
        pgsql, accumulator_id, select_charge=True,
    ) == [(accumulator_id, None, CABINET_ID, None, 5)]


CREATED_BOOKING_SQL = pytest.mark.pgsql(
    'scooter_accumulator', files=['created_booking.sql'],
)
IN_PROCESS_BOOKING_SQL = pytest.mark.pgsql(
    'scooter_accumulator', files=['in_process_booking.sql'],
)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=CREATED_BOOKING_SQL,
            id='set states as if PROCESSED for CREATED booking',
        ),
        pytest.param(
            marks=IN_PROCESS_BOOKING_SQL,
            id='set states as if PROCESSED for IN_PROCESS booking',
        ),
    ],
)
async def test_ok_concrete_booking(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': CABINET_ID,
            'contractor_id': CONTRACTOR_ID,
            'accumulator_id': 'accum_id1',
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'booking_id': 'booking_id1',
        'cell_id': 'cell_id1',
        'status': 'PROCESSED',
    }

    assert sql.select_bookings_info(pgsql, 'booking_id1') == [
        ('booking_id1', 'PROCESSED', CONTRACTOR_ID, None),
    ]
    assert sql.select_cells_info(pgsql, 'cell_id1') == [
        ('cell_id1', 'accum_id1', 'booking_id1'),
    ]
    assert sql.select_accumulators_info(
        pgsql, 'accum_id1', select_charge=True,
    ) == [('accum_id1', None, CABINET_ID, None, 5)]


@pytest.mark.pgsql('scooter_accumulator', files=['no_bookings_for_return.sql'])
async def test_bad_no_bookings_for_return(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': CABINET_ID,
            'contractor_id': CONTRACTOR_ID,
            'accumulator_id': 'accum_id1',
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': 'no_bookings_for_return_were_found'}


async def test_bad_no_bookings(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': CABINET_ID,
            'contractor_id': CONTRACTOR_ID_NON_EXISTENT,
            'accumulator_id': 'accum_id1',
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': 'no_bookings_were_found'}
