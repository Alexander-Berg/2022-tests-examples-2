import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/accumulator/validate-return'

TESTPOINT_NAME = 'mqtt_publish'

CONTRACTOR_ID1 = 'contractor_id1'
CABINET_ID1 = 'cabinet_id1'
SCOOTER_ID1 = 'scooter_id1'
BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
BOOKING_ID4 = 'booking_id4'
ACCUMULATOR_ID1 = 'accum_id1'
ACCUMULATOR_ID2 = 'accum_id2'
ACCUMULATOR_ID3 = 'accum_id3'
ACCUMULATOR_ID4 = 'accum_id4'
ACCUMULATOR_ID5 = 'accum_id5'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
CELL_ID3 = 'cell_id3'
CELL_ID4 = 'cell_id4'


@pytest.mark.pgsql('scooter_accumulator', files=['ok.sql'])
async def test_ok(taxi_scooter_accumulator, pgsql):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'booking_ids': ','.join([BOOKING_ID1, BOOKING_ID2, BOOKING_ID3]),
        },
        json={},
    )

    assert response.status_code == 200
    assert sql.select_bookings_info(pgsql, select_comment=True) == [
        (BOOKING_ID1, 'VALIDATED', CONTRACTOR_ID1, None, None),
        (
            BOOKING_ID2,
            'VALIDATED',
            CONTRACTOR_ID1,
            None,
            'returned accumulator: `accum_id2`',
        ),
        (
            BOOKING_ID3,
            'VALIDATED',
            CONTRACTOR_ID1,
            None,
            'returned accumulator: `accum_id3`',
        ),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, None, None, SCOOTER_ID1),
        (ACCUMULATOR_ID2, None, CABINET_ID1, None),
        (ACCUMULATOR_ID3, None, CABINET_ID1, None),
        (ACCUMULATOR_ID4, None, None, None),
        (ACCUMULATOR_ID5, None, None, None),
    ]
    assert sql.select_cells_info(pgsql) == [
        (CELL_ID1, ACCUMULATOR_ID1, None),
        (CELL_ID2, ACCUMULATOR_ID2, None),
        (CELL_ID3, ACCUMULATOR_ID3, None),
    ]


# @pytest.mark.pgsql('scooter_accumulator', files=['deferred_ok.sql'])
# async def test_deferred_ok(taxi_scooter_accumulator, pgsql):
#     response = await taxi_scooter_accumulator.post(
#         ENDPOINT,
#         params={
#             'booking_ids': ','.join(
#                 [BOOKING_ID1, BOOKING_ID2, BOOKING_ID3, BOOKING_ID4],
#             ),
#         },
#         json={},
#     )

#     assert response.status_code == 200
#     assert sql.select_bookings_info(pgsql, select_comment=True) == [
#         (BOOKING_ID1, 'DEFERRED_VALIDATED', CONTRACTOR_ID1, None, None),
#         (
#             BOOKING_ID2,
#             'DEFERRED_VALIDATED',
#             CONTRACTOR_ID1,
#             None,
#             'defer returned accumulator to cell: `cell_id2`',
#         ),
#         (
#             BOOKING_ID3,
#             'DEFERRED_VALIDATED',
#             CONTRACTOR_ID1,
#             None,
#             'defer returned accumulator to cell: `cell_id3`',
#         ),
#         (BOOKING_ID4, 'VALIDATED', CONTRACTOR_ID1, None, None),
#     ]
#     assert sql.select_accumulators_info(pgsql) == [
#         (ACCUMULATOR_ID1, None, None, SCOOTER_ID1),
#         (ACCUMULATOR_ID2, None, CABINET_ID1, None),
#         (ACCUMULATOR_ID3, None, None, SCOOTER_ID1),
#         (ACCUMULATOR_ID4, None, None, None),
#         (ACCUMULATOR_ID5, None, None, None),
#     ]
#     assert sql.select_cells_info(pgsql) == [
#         (CELL_ID1, None, BOOKING_ID1),
#         (CELL_ID2, None, BOOKING_ID2),
#         (CELL_ID3, None, BOOKING_ID3),
#         (CELL_ID4, ACCUMULATOR_ID2, None),
#     ]


@pytest.mark.pgsql('scooter_accumulator', files=['ok_opened_cell.sql'])
async def test_ok_opened_cell(
        taxi_scooter_accumulator,
        pgsql,
        testpoint,
        tp_validate_cell_with_accum,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cell_status(data):
        return tp_validate_cell_with_accum

    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_ids': ','.join([BOOKING_ID2, BOOKING_ID1])},
        json={},
    )

    assert response.status_code == 200
    assert mqtt_cell_status.times_called == 1
    assert sql.select_bookings_info(pgsql) == [
        (BOOKING_ID1, 'VALIDATED', CONTRACTOR_ID1, None),
        (BOOKING_ID2, 'VALIDATED', CONTRACTOR_ID1, None),
    ]
    assert sql.select_accumulators_info(pgsql) == [
        (ACCUMULATOR_ID1, None, CABINET_ID1, None),
        (ACCUMULATOR_ID2, None, CABINET_ID1, None),
    ]
    assert sql.select_cells_info(pgsql) == [
        (CELL_ID1, ACCUMULATOR_ID1, None),
        (CELL_ID2, ACCUMULATOR_ID2, None),
    ]


@pytest.mark.pgsql(
    'scooter_accumulator', files=['booking_with_accumulator.sql'],
)
async def test_booking_with_accumulator(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_ids': BOOKING_ID1}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'booking_with_accumulator',
        'booking_id': BOOKING_ID1,
    }


@pytest.mark.pgsql('scooter_accumulator', files=['cell_is_open.sql'])
async def test_cell_is_open(
        taxi_scooter_accumulator, testpoint, tp_validate_cell_is_open,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cell_status(data):
        return tp_validate_cell_is_open

    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={'booking_ids': ','.join([BOOKING_ID1, BOOKING_ID2])},
        json={},
    )

    assert response.status_code == 400
    assert mqtt_cell_status.times_called == 1
    assert response.json() == {
        'code': 'cell_is_open',
        'booking_id': BOOKING_ID1,
    }


@pytest.mark.pgsql(
    'scooter_accumulator', files=['accumulator_was_not_returned.sql'],
)
async def test_accumulator_was_not_returned(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        params={
            'booking_ids': ','.join([BOOKING_ID1, BOOKING_ID2, BOOKING_ID3]),
        },
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'accumulator_was_not_returned',
        'booking_id': BOOKING_ID3,
    }


@pytest.mark.pgsql('scooter_accumulator', files=['non_processed_booking.sql'])
@pytest.mark.parametrize(
    'booking_id, message',
    [
        pytest.param(
            BOOKING_ID1, 'booking state: kCreated', id='PROCESSED status',
        ),
        pytest.param(
            BOOKING_ID2,
            'deferred_processed not in cabinet_without_validation',
            id='CREATED status',
        ),
    ],
)
async def test_non_processed_booking(
        taxi_scooter_accumulator, booking_id, message,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_ids': booking_id}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'non_processed_booking',
        'booking_id': booking_id,
        'message': message,
    }


# @pytest.mark.pgsql(
#     'scooter_accumulator', files=['non_deferred_processed_booking.sql'],
# )
# @pytest.mark.parametrize(
#     'booking_id, message',
#     [
#         pytest.param(
#             BOOKING_ID1,
#             'not deferred_processed in cabinet_without_validation',
#             id='PROCESSED status',
#         ),
#         pytest.param(
#             BOOKING_ID2, 'booking state: kCreated', id='CREATED status',
#         ),
#         pytest.param(
#             BOOKING_ID3,
#             'not deferred_processed in cabinet_without_validation',
#             id='IN_PROCESS status',
#         ),
#     ],
# )
# async def test_non_deferred_processed_booking(
#         taxi_scooter_accumulator, booking_id, message,
# ):
#     response = await taxi_scooter_accumulator.post(
#         ENDPOINT, params={'booking_ids': booking_id}, json={},
#     )

#     assert response.status_code == 400
#     assert response.json() == {
#         'code': 'non_processed_booking',
#         'booking_id': booking_id,
#         'message': message,
#     }
