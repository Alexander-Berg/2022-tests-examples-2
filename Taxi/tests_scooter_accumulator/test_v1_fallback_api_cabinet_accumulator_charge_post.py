import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/fallback-api/cabinet/accumulator/charge'

ACCUMULATOR_ID = 'accum_id1'
CABINET_ID = 'cabinet_id2'
CONSUMER_ID = 'consumer_id1'


@pytest.mark.parametrize(
    'accumulator_charge', [pytest.param(0), pytest.param(100)],
)
async def test_ok(taxi_scooter_accumulator, pgsql, accumulator_charge):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'accumulator_id': ACCUMULATOR_ID,
            'accumulator_charge': accumulator_charge,
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == 200

    assert sql.select_accumulators_info(
        pgsql, ACCUMULATOR_ID, select_charge=True,
    ) == [(ACCUMULATOR_ID, None, CABINET_ID, None, accumulator_charge)]


@pytest.mark.parametrize(
    'accumulator_id, accumulator_charge, code, accumulator_db_row',
    [
        pytest.param(
            ACCUMULATOR_ID,
            101,
            400,
            (ACCUMULATOR_ID, None, CABINET_ID, None, 95),
            id='wrong accumulator_charge',
        ),
        pytest.param(
            ACCUMULATOR_ID,
            -1,
            400,
            (ACCUMULATOR_ID, None, CABINET_ID, None, 95),
            id='wrong accumulator_charge',
        ),
        pytest.param(
            'accum_id_non_existent',
            99,
            404,
            (),
            id='non-existent accumulator',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator,
        pgsql,
        accumulator_id,
        accumulator_charge,
        code,
        accumulator_db_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'accumulator_id': accumulator_id,
            'accumulator_charge': accumulator_charge,
            'consumer_id': CONSUMER_ID,
        },
    )

    assert response.status_code == code

    assert sql.select_accumulators_info(
        pgsql, accumulator_id, select_charge=True,
    ) == [accumulator_db_row]
