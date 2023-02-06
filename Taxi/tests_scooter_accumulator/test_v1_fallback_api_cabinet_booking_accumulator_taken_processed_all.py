import pytest

from . import sql

ENDPOINT = (
    '/scooter-accumulator/v1/fallback-api/cabinet/booking/'
    'accumulator-taken-processed-all'
)

CONTRACTOR_ID = 'contractor_id1'
CONTRACTOR_ID_NON_EXISTENT = 'contractor_id_non_existent'
CABINET_ID = 'cabinet_id1'
CABINET_ID2 = 'cabinet_id2'
CABINET_ID_NON_EXISTENT = 'cabinet_id_non_existent'
CONSUMER_ID = 'consumer_id1'


@pytest.mark.parametrize(
    'params, etalon_response, sql_tables',
    [
        pytest.param(
            {
                'cabinet_id': CABINET_ID,
                'contractor_id': CONTRACTOR_ID,
                'consumer_id': CONSUMER_ID,
            },
            {
                'bookings': [
                    {
                        'booking_id': 'booking_id1',
                        'status': 'PROCESSED',
                        'cell_id': 'cell_id1',
                        'accumulator_id': 'accum_id1',
                    },
                    {
                        'booking_id': 'booking_id2',
                        'status': 'PROCESSED',
                        'cell_id': 'cell_id2',
                        'accumulator_id': 'accum_id2',
                    },
                    {
                        'booking_id': 'booking_id3',
                        'status': 'PROCESSED',
                        'cell_id': 'cell_id3',
                        'accumulator_id': 'accum_id3',
                    },
                    {
                        'booking_id': 'booking_id6',
                        'status': 'PROCESSED',
                        'cell_id': 'cell_id7',
                        'accumulator_id': 'fake_id123',
                    },
                ],
                'cabinet_type': 'cabinet_without_validation',
            },
            {
                'bookings': [
                    (
                        'booking_id1',
                        'PROCESSED',
                        'contractor_id1',
                        'accum_id1',
                    ),
                    (
                        'booking_id2',
                        'PROCESSED',
                        'contractor_id1',
                        'accum_id2',
                    ),
                    (
                        'booking_id3',
                        'PROCESSED',
                        'contractor_id1',
                        'accum_id3',
                    ),
                    (
                        'booking_id4',
                        'VALIDATED',
                        'contractor_id1',
                        'accum_id4',
                    ),
                    ('booking_id5', 'CREATED', 'contractor_id1', None),
                    (
                        'booking_id6',
                        'PROCESSED',
                        'contractor_id1',
                        'fake_id123',
                    ),
                    ('booking_id7', 'CREATED', 'contractor_id1', 'acc_id_2_1'),
                    (
                        'booking_id8',
                        'PROCESSED',
                        'contractor_id1',
                        'acc_id_2_2',
                    ),
                ],
                'cells': [
                    ('cell_id1', None, 'booking_id1'),
                    ('cell_id1', 'acc_id_2_1', 'booking_id7'),
                    ('cell_id2', None, 'booking_id2'),
                    ('cell_id2', None, 'booking_id8'),
                    ('cell_id3', None, 'booking_id3'),
                    ('cell_id4', None, None),
                    ('cell_id5', None, 'booking_id5'),
                    ('cell_id6', None, None),
                    ('cell_id7', None, 'booking_id6'),
                ],
                'accumulators': [
                    ('acc_id_2_1', None, 'cabinet_id2', None),
                    ('acc_id_2_2', 'contractor_id1', None, None),
                    ('accum_id1', 'contractor_id1', None, None),
                    ('accum_id2', 'contractor_id1', None, None),
                    ('accum_id3', 'contractor_id1', None, None),
                    ('accum_id4', 'contractor_id1', None, None),
                    ('accum_id_no_place', None, None, None),
                    ('fake_id123', 'contractor_id1', None, None),
                ],
            },
            id='set state PROCESSED to all bookings in `cabinet_id1`',
        ),
        pytest.param(
            {
                'cabinet_id': CABINET_ID,
                'contractor_id': CONTRACTOR_ID_NON_EXISTENT,
                'consumer_id': CONSUMER_ID,
            },
            {'bookings': [], 'cabinet_type': 'cabinet_without_validation'},
            {
                'bookings': [
                    ('booking_id1', 'CREATED', 'contractor_id1', 'accum_id1'),
                    (
                        'booking_id2',
                        'IN_PROCESS',
                        'contractor_id1',
                        'accum_id2',
                    ),
                    (
                        'booking_id3',
                        'PROCESSED',
                        'contractor_id1',
                        'accum_id3',
                    ),
                    (
                        'booking_id4',
                        'VALIDATED',
                        'contractor_id1',
                        'accum_id4',
                    ),
                    ('booking_id5', 'CREATED', 'contractor_id1', None),
                    ('booking_id6', 'CREATED', 'contractor_id1', 'fake_id123'),
                    ('booking_id7', 'CREATED', 'contractor_id1', 'acc_id_2_1'),
                    (
                        'booking_id8',
                        'PROCESSED',
                        'contractor_id1',
                        'acc_id_2_2',
                    ),
                ],
                'cells': [
                    ('cell_id1', 'accum_id1', 'booking_id1'),
                    ('cell_id1', 'acc_id_2_1', 'booking_id7'),
                    ('cell_id2', 'accum_id2', 'booking_id2'),
                    ('cell_id2', None, 'booking_id8'),
                    ('cell_id3', None, 'booking_id3'),
                    ('cell_id4', None, None),
                    ('cell_id5', None, 'booking_id5'),
                    ('cell_id6', None, None),
                    ('cell_id7', 'fake_id123', 'booking_id6'),
                ],
                'accumulators': [
                    ('acc_id_2_1', None, 'cabinet_id2', None),
                    ('acc_id_2_2', 'contractor_id1', None, None),
                    ('accum_id1', None, 'cabinet_id1', None),
                    ('accum_id2', None, 'cabinet_id1', None),
                    ('accum_id3', 'contractor_id1', None, None),
                    ('accum_id4', 'contractor_id1', None, None),
                    ('accum_id_no_place', None, None, None),
                    ('fake_id123', None, 'cabinet_id1', None),
                ],
            },
            id='no bookings for contractor, but it is ok',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, params, etalon_response, sql_tables,
):
    response = await taxi_scooter_accumulator.post(ENDPOINT, params=params)

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == etalon_response

    assert sql.select_bookings_info(pgsql) == sql_tables['bookings']
    assert sql.select_cells_info(pgsql) == sql_tables['cells']
    assert sql.select_accumulators_info(pgsql) == sql_tables['accumulators']


@pytest.mark.parametrize(
    'params, code, message',
    [
        pytest.param(
            {
                'cabinet_id': CABINET_ID_NON_EXISTENT,
                'contractor_id': CONTRACTOR_ID,
                'consumer_id': CONSUMER_ID,
            },
            404,
            'cabinet was not found',
            id='non existent cabinet id',
        ),
        pytest.param(
            {
                'cabinet_id': CABINET_ID2,
                'contractor_id': CONTRACTOR_ID,
                'consumer_id': CONSUMER_ID,
            },
            400,
            'cabinet_type `cabinet` != `cabinet_without_validation`',
            id='wrong cabinet_type',
        ),
    ],
)
async def test_bad(taxi_scooter_accumulator, params, code, message):
    response = await taxi_scooter_accumulator.post(ENDPOINT, params=params)

    assert response.status_code == code

    response_json = response.json()
    assert response_json == {'code': str(code), 'message': message}
