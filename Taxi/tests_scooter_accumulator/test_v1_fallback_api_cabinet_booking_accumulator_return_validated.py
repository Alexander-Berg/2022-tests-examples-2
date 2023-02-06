import pytest

from . import sql

ENDPOINT = (
    '/scooter-accumulator/v1/fallback-api/cabinet/booking/'
    'accumulator-return-validated'
)

ACCUMULATOR_DEFERRED_VALIDATED_ID = 'acc_id7'
ACCUMULATOR_VALIDATED_ID = 'acc_id5'

BOOKING_DEFERRED_VALIDATED_ID = 'booking_id7'
BOOKING_VALIDATED_ID = 'booking_id5'
BOOKING_PROCESSED_ID = 'booking_id4'
BOOKING_DEFERRED_PROCESSED_ID = 'booking_id3'
BOOKING_ID_WRONG_CABINET_TYPE = 'booking_id8'
BOOKING_NON_EXISTENT_ID = 'booking_id9'

CELL_DEFERRED_VALIDATED_ID = 'cell_id7'
CELL_VALIDATED_ID = 'cell_id5'
CELL_NON_EXISTENT_ID = 'cell_id9'

CABINET_ID = 'cabinet_without_validation_id'
CONTRACTOR_ID = 'contractor_id1'
CONSUMER_ID = 'consumer_id1'


@pytest.mark.parametrize(
    'booking_id, cell_id, accumulator_id',
    [
        pytest.param(
            BOOKING_DEFERRED_VALIDATED_ID,
            CELL_DEFERRED_VALIDATED_ID,
            ACCUMULATOR_DEFERRED_VALIDATED_ID,
            id='ok: DEFERRED_VALIDATED to VALIDATED',
        ),
        pytest.param(
            BOOKING_VALIDATED_ID,
            CELL_VALIDATED_ID,
            ACCUMULATOR_VALIDATED_ID,
            id='ok: retry',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, booking_id, cell_id, accumulator_id,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'booking_id': booking_id,
            'accumulator_id': accumulator_id,
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 200

    assert sql.select_bookings_info(pgsql, booking_id) == [
        (booking_id, 'VALIDATED', CONTRACTOR_ID, None),
    ]
    assert sql.select_cells_info(pgsql, cell_id) == [
        (cell_id, accumulator_id, None),
    ]
    assert sql.select_accumulators_info(
        pgsql, accumulator_id, select_charge=True,
    ) == [(accumulator_id, None, CABINET_ID, None, 5)]


@pytest.mark.parametrize(
    'params, code, message',
    [
        pytest.param(
            {
                'booking_id': BOOKING_ID_WRONG_CABINET_TYPE,
                'accumulator_id': ACCUMULATOR_DEFERRED_VALIDATED_ID,
                'consumer_id': CONSUMER_ID,
            },
            400,
            'cabinet_type `cabinet` != `cabinet_without_validation`',
            id='wrong cabinet_type',
        ),
        pytest.param(
            {
                'booking_id': BOOKING_PROCESSED_ID,
                'accumulator_id': ACCUMULATOR_DEFERRED_VALIDATED_ID,
                'consumer_id': CONSUMER_ID,
            },
            400,
            (
                'booking_status `PROCESSED` of booking_id '
                f'`{BOOKING_PROCESSED_ID}` != `DEFERRED_VALIDATED`'
            ),
            id='booking has wrong status',
        ),
        pytest.param(
            {
                'booking_id': BOOKING_DEFERRED_PROCESSED_ID,
                'accumulator_id': ACCUMULATOR_DEFERRED_VALIDATED_ID,
                'consumer_id': CONSUMER_ID,
            },
            400,
            (
                'booking_status `DEFERRED_PROCESSED` of booking_id '
                f'`{BOOKING_DEFERRED_PROCESSED_ID}` != `DEFERRED_VALIDATED`'
            ),
            id='booking has wrong status',
        ),
        pytest.param(
            {
                'booking_id': BOOKING_NON_EXISTENT_ID,
                'accumulator_id': ACCUMULATOR_DEFERRED_VALIDATED_ID,
                'consumer_id': CONSUMER_ID,
            },
            404,
            f'booking_ids don\'t exist: {BOOKING_NON_EXISTENT_ID}',
            id='non existent booking id',
        ),
    ],
)
async def test_bad(taxi_scooter_accumulator, params, code, message):
    response = await taxi_scooter_accumulator.post(ENDPOINT, params=params)

    assert response.status_code == code

    response_json = response.json()
    assert response_json == {'code': str(code), 'message': message}
