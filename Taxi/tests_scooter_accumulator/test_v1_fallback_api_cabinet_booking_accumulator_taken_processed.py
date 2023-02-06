import pytest

from . import sql

ENDPOINT = (
    '/scooter-accumulator/v1/fallback-api/cabinet/booking/'
    'accumulator-taken-processed'
)

CONTRACTOR_ID = 'contractor_id1'
CONTRACTOR_ID_NON_EXISTENT = 'contractor_id_non_existent'
CABINET_ID = 'cabinet_id1'
CONSUMER_ID = 'consumer_id1'
ACCUMULATOR_ID_NON_EXISTENT = 'accum_id_non_existent'


@pytest.mark.parametrize(
    'accumulator_id, booking_id, cell_id, comment',
    [
        pytest.param(
            'accum_id1',
            'booking_id1',
            'cell_id1',
            None,
            id='set states as if PROCESSED for CREATED booking',
        ),
        pytest.param(
            'accum_id2',
            'booking_id2',
            'cell_id2',
            None,
            id='set states as if PROCESSED for IN_PROCESS booking',
        ),
        pytest.param(
            'accum_id3',
            'booking_id3',
            'cell_id3',
            None,
            id='check idempotency for PROCESSED booking',
        ),
        pytest.param(
            'accum_id_no_place',
            'booking_id6',
            'cell_id7',
            'processed manually by accumulator_id: `accum_id_no_place`',
            id='set states as if PROCESSED for CREATED booking with fake id',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator,
        pgsql,
        accumulator_id,
        booking_id,
        cell_id,
        comment,
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

    if comment:
        accumulator_id = 'fake_id123'

    assert response_json == {
        'booking_id': booking_id,
        'cell_id': cell_id,
        'accumulator_id': accumulator_id,
        'status': 'PROCESSED',
    }
    assert sql.select_bookings_info(
        pgsql, booking_id, select_comment=True,
    ) == [(booking_id, 'PROCESSED', CONTRACTOR_ID, accumulator_id, comment)]
    assert sql.select_cells_info(pgsql, cell_id) == [
        (cell_id, None, booking_id),
    ]
    assert sql.select_accumulators_info(pgsql, accumulator_id) == [
        (accumulator_id, CONTRACTOR_ID, None, None),
    ]


@pytest.mark.parametrize(
    'accumulator_id, code',
    [
        pytest.param(
            ACCUMULATOR_ID_NON_EXISTENT,
            'accumulator_id_was_not_found',
            id='non existent accumulator',
        ),
        pytest.param(
            'accum_id4',
            'processed_error',
            id='accumulator_id for booking that has already been VALIDATED',
        ),
    ],
)
async def test_bad(taxi_scooter_accumulator, accumulator_id, code):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'cabinet_id': CABINET_ID,
            'contractor_id': CONTRACTOR_ID,
            'accumulator_id': accumulator_id,
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 400
    assert response.json() == {'code': code}


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
