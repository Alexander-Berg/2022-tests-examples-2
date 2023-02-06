import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/contractor/accumulator-exchange'

CONTRACTOR_ID = 'contractor_id1'
CONTRACTOR_ID_NON_EXISTENT = 'contractor_id_non_existent'
SCOOTER_ID = 'scooter_id1'
SCOOTER_ID_NON_EXISTENT = 'scooter_id_non_existent'
ACCUMULATOR_ID1 = 'accum_id1'
ACCUMULATOR_ID2 = 'accum_id2'
ACCUMULATOR_ID3 = 'accum_id3'
ACCUMULATOR_ID_NON_EXISTENT = 'accum_id_non_existent'
ACCUMULATOR_SERIAL_NUM1 = 'accum_serial_num1'
ACCUMULATOR_SERIAL_NUM2 = 'accum_serial_num2'
ACCUMULATOR_SERIAL_NUM3 = 'accum_serial_num3'
ACCUMULATOR_SERIAL_NUM_NON_EXISTENT = 'accum_serial_num_non_existent'


@pytest.mark.parametrize(
    'contractor_id, scooter_id, inserted_accumulator_id, '
    'taken_accumulator_id, inserted_accumulator_serial_number, '
    'taken_accumulator_serial_number, inserted_accum_db_row, '
    'taken_accum_db_row',
    [
        pytest.param(
            CONTRACTOR_ID,
            SCOOTER_ID,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID2,
            ACCUMULATOR_SERIAL_NUM1,
            ACCUMULATOR_SERIAL_NUM2,
            (ACCUMULATOR_ID1, None, None, SCOOTER_ID, ACCUMULATOR_SERIAL_NUM1),
            (
                ACCUMULATOR_ID2,
                CONTRACTOR_ID,
                None,
                None,
                ACCUMULATOR_SERIAL_NUM2,
            ),
            id='simple exchange',
        ),
        pytest.param(
            CONTRACTOR_ID,
            SCOOTER_ID,
            ACCUMULATOR_ID2,
            ACCUMULATOR_ID1,
            ACCUMULATOR_SERIAL_NUM2,
            ACCUMULATOR_SERIAL_NUM1,
            (ACCUMULATOR_ID2, None, None, SCOOTER_ID, ACCUMULATOR_SERIAL_NUM2),
            (
                ACCUMULATOR_ID1,
                CONTRACTOR_ID,
                None,
                None,
                ACCUMULATOR_SERIAL_NUM1,
            ),
            id='emulate retry',
        ),
        pytest.param(
            CONTRACTOR_ID,
            SCOOTER_ID,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID3,
            ACCUMULATOR_SERIAL_NUM1,
            ACCUMULATOR_SERIAL_NUM3,
            (ACCUMULATOR_ID1, None, None, SCOOTER_ID, ACCUMULATOR_SERIAL_NUM1),
            (
                ACCUMULATOR_ID3,
                CONTRACTOR_ID,
                None,
                None,
                ACCUMULATOR_SERIAL_NUM3,
            ),
            id=(
                'ACCUMULATOR_ID3 is in incorrect state, '
                'but handler must return ok'
            ),
        ),
        pytest.param(
            CONTRACTOR_ID,
            SCOOTER_ID_NON_EXISTENT,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID2,
            ACCUMULATOR_SERIAL_NUM1,
            ACCUMULATOR_SERIAL_NUM2,
            (
                ACCUMULATOR_ID1,
                None,
                None,
                SCOOTER_ID_NON_EXISTENT,
                ACCUMULATOR_SERIAL_NUM1,
            ),
            (
                ACCUMULATOR_ID2,
                CONTRACTOR_ID,
                None,
                None,
                ACCUMULATOR_SERIAL_NUM2,
            ),
            id='scooter_id is not-existent, but we can not control it',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator,
        pgsql,
        contractor_id,
        scooter_id,
        inserted_accumulator_id,
        taken_accumulator_id,
        inserted_accumulator_serial_number,
        taken_accumulator_serial_number,
        inserted_accum_db_row,
        taken_accum_db_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'contractor_id': contractor_id,
            'scooter_id': scooter_id,
            'inserted_accumulator_serial_number': (
                inserted_accumulator_serial_number
            ),
            'taken_accumulator_serial_number': taken_accumulator_serial_number,
        },
        json={},
    )

    assert response.status_code == 200
    assert sql.select_accumulators_info(
        pgsql, inserted_accumulator_id, select_serial_number=True,
    ) == [inserted_accum_db_row]
    assert sql.select_accumulators_info(
        pgsql, taken_accumulator_id, select_serial_number=True,
    ) == [taken_accum_db_row]


@pytest.mark.parametrize(
    'contractor_id, scooter_id, inserted_accumulator_id, '
    'taken_accumulator_id, inserted_accumulator_serial_number, '
    'taken_accumulator_serial_number, code, response_json, '
    'inserted_accum_db_row, taken_accum_db_row',
    [
        pytest.param(
            CONTRACTOR_ID,
            SCOOTER_ID,
            ACCUMULATOR_ID_NON_EXISTENT,
            ACCUMULATOR_ID2,
            ACCUMULATOR_SERIAL_NUM_NON_EXISTENT,
            ACCUMULATOR_SERIAL_NUM2,
            404,
            {
                'code': '404',
                'message': (
                    'kAccumulatorsSelectBySerialNumber: '
                    'accumulator with serial number '
                    '`accum_serial_num_non_existent` was not found'
                ),
            },
            (),
            (ACCUMULATOR_ID2, None, None, SCOOTER_ID, ACCUMULATOR_SERIAL_NUM2),
            id='non-existent inserted accumulator',
        ),
        pytest.param(
            CONTRACTOR_ID,
            SCOOTER_ID,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID_NON_EXISTENT,
            ACCUMULATOR_SERIAL_NUM1,
            ACCUMULATOR_SERIAL_NUM_NON_EXISTENT,
            404,
            {
                'code': '404',
                'message': (
                    'kAccumulatorsSelectBySerialNumber: '
                    'accumulator with serial number '
                    '`accum_serial_num_non_existent` was not found'
                ),
            },
            (
                ACCUMULATOR_ID1,
                CONTRACTOR_ID,
                None,
                None,
                ACCUMULATOR_SERIAL_NUM1,
            ),
            (),
            id='non-existent taken accumulator',
        ),
        pytest.param(
            CONTRACTOR_ID_NON_EXISTENT,
            SCOOTER_ID,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID2,
            ACCUMULATOR_SERIAL_NUM1,
            ACCUMULATOR_SERIAL_NUM2,
            409,
            {
                'code': '409',
                'message': (
                    f'accumulator contractor_id `{CONTRACTOR_ID}` '
                    'is different from request contractor_id '
                    f'`{CONTRACTOR_ID_NON_EXISTENT}`'
                ),
            },
            (
                ACCUMULATOR_ID1,
                CONTRACTOR_ID,
                None,
                None,
                ACCUMULATOR_SERIAL_NUM1,
            ),
            (ACCUMULATOR_ID2, None, None, SCOOTER_ID, ACCUMULATOR_SERIAL_NUM2),
            id='wrong contractor_id',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator,
        pgsql,
        contractor_id,
        scooter_id,
        inserted_accumulator_id,
        taken_accumulator_id,
        inserted_accumulator_serial_number,
        taken_accumulator_serial_number,
        code,
        response_json,
        inserted_accum_db_row,
        taken_accum_db_row,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'contractor_id': contractor_id,
            'scooter_id': scooter_id,
            'inserted_accumulator_serial_number': (
                inserted_accumulator_serial_number
            ),
            'taken_accumulator_serial_number': taken_accumulator_serial_number,
        },
        json={},
    )

    assert response.status_code == code
    assert response.json() == response_json
    assert sql.select_accumulators_info(
        pgsql, inserted_accumulator_id, select_serial_number=True,
    ) == [inserted_accum_db_row]
    assert sql.select_accumulators_info(
        pgsql, taken_accumulator_id, select_serial_number=True,
    ) == [taken_accum_db_row]
