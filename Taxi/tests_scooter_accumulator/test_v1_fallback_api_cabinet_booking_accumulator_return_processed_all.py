import pytest

from . import sql

ENDPOINT = (
    '/scooter-accumulator/v1/fallback-api/cabinet/booking/'
    'accumulator-return-processed-all'
)

CONTRACTOR_ID = 'contractor_id1'
CONTRACTOR_ID_NON_EXISTENT = 'contractor_id_non_existent'
CABINET_ID = 'cabinet_id1'
CABINET_ID2 = 'cabinet_id2'
CABINET_ID_NON_EXISTENT = 'cabinet_id_non_existent'
CONSUMER_ID = 'consumer_id1'

CELLS = [
    ('cell_id1', None, 'booking_id1'),
    ('cell_id2', None, 'booking_id2'),
    ('cell_id3', None, 'booking_id3'),
    ('cell_id4', None, 'booking_id4'),
    ('cell_id5', None, None),
    ('cell_id6', None, None),
    ('cell_id7', 'accum_id7', 'booking_id7'),
]

ACCUMULATORS = [
    ('accum_id1', 'contractor_id1', None, None),
    ('accum_id2', 'contractor_id1', None, None),
    ('accum_id3', 'contractor_id1', None, None),
    ('accum_id4', 'contractor_id1', None, None),
    ('accum_id5', None, 'cabinet_id1', None),
    ('accum_id7', None, 'cabinet_id1', None),
]


@pytest.mark.parametrize(
    'params, etalon_response, bookings',
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
                        'status': 'DEFERRED_PROCESSED',
                        'cell_id': 'cell_id1',
                    },
                    {
                        'booking_id': 'booking_id2',
                        'status': 'DEFERRED_PROCESSED',
                        'cell_id': 'cell_id2',
                    },
                    {
                        'booking_id': 'booking_id3',
                        'status': 'DEFERRED_PROCESSED',
                        'cell_id': 'cell_id3',
                    },
                ],
                'cabinet_type': 'cabinet_without_validation',
            },
            [
                (
                    'booking_id1',
                    'DEFERRED_PROCESSED',
                    'contractor_id1',
                    None,
                    'cell_id1',
                ),
                (
                    'booking_id2',
                    'DEFERRED_PROCESSED',
                    'contractor_id1',
                    None,
                    'cell_id2',
                ),
                (
                    'booking_id3',
                    'DEFERRED_PROCESSED',
                    'contractor_id1',
                    None,
                    'cell_id3',
                ),
                (
                    'booking_id4',
                    'PROCESSED',
                    'contractor_id1',
                    None,
                    'cell_id4',
                ),
                (
                    'booking_id5',
                    'VALIDATED',
                    'contractor_id1',
                    None,
                    'cell_id5',
                ),
                ('booking_id6', 'REVOKED', 'contractor_id1', None, 'cell_id6'),
                (
                    'booking_id7',
                    'CREATED',
                    'contractor_id1',
                    'accum_id7',
                    'cell_id7',
                ),
            ],
            id='set state DEFERRED_PROCESSED to all bookings in `cabinet_id1`',
        ),
        pytest.param(
            {
                'cabinet_id': CABINET_ID,
                'contractor_id': CONTRACTOR_ID_NON_EXISTENT,
                'consumer_id': CONSUMER_ID,
            },
            {'bookings': [], 'cabinet_type': 'cabinet_without_validation'},
            [
                ('booking_id1', 'CREATED', 'contractor_id1', None, 'cell_id1'),
                (
                    'booking_id2',
                    'IN_PROCESS',
                    'contractor_id1',
                    None,
                    'cell_id2',
                ),
                (
                    'booking_id3',
                    'DEFERRED_PROCESSED',
                    'contractor_id1',
                    None,
                    'cell_id3',
                ),
                (
                    'booking_id4',
                    'PROCESSED',
                    'contractor_id1',
                    None,
                    'cell_id4',
                ),
                (
                    'booking_id5',
                    'VALIDATED',
                    'contractor_id1',
                    None,
                    'cell_id5',
                ),
                ('booking_id6', 'REVOKED', 'contractor_id1', None, 'cell_id6'),
                (
                    'booking_id7',
                    'CREATED',
                    'contractor_id1',
                    'accum_id7',
                    'cell_id7',
                ),
            ],
            id='no bookings for contractor, but it is ok',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, params, etalon_response, bookings,
):
    response = await taxi_scooter_accumulator.post(ENDPOINT, params=params)

    assert response.status_code == 200

    response_json = response.json()
    assert response_json == etalon_response

    assert sql.select_bookings_info(pgsql, select_cell_id=True) == bookings
    assert sql.select_cells_info(pgsql) == CELLS
    assert sql.select_accumulators_info(pgsql) == ACCUMULATORS


@pytest.mark.parametrize(
    'params, code, message',
    [
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
    ],
)
async def test_bad(taxi_scooter_accumulator, params, code, message):
    response = await taxi_scooter_accumulator.post(ENDPOINT, params=params)

    assert response.status_code == code

    response_json = response.json()
    assert response_json == {'code': str(code), 'message': message}
