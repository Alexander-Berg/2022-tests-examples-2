import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/cabinet/cell/check-processed'

TESTPOINT_NAME = 'mqtt_publish'

BOOKING_ID1 = 'booking_id1'
BOOKING_ID2 = 'booking_id2'
BOOKING_ID3 = 'booking_id3'
BOOKING_ID4 = 'booking_id4'
BOOKING_ID5 = 'booking_id5'
CONTRACTOR_ID1 = 'contractor_id1'
CELL_ID1 = 'cell_id1'
CELL_ID2 = 'cell_id2'
CELL_ID3 = 'cell_id3'
CELL_ID4 = 'cell_id4'
CELL_ID5 = 'cell_id5'
ACCUMULATOR_ID1 = 'accum_id1'
ACCUMULATOR_ID2 = 'accum_id2'


@pytest.mark.parametrize(
    'mqtt_fixture_times_called, booking_status',
    [
        pytest.param(
            0,
            'PROCESSED',
            id='closed cell without accumulator',
            marks=pytest.mark.pgsql(
                'scooter_accumulator', files=['in_process_closed_cell.sql'],
            ),
        ),
        pytest.param(
            1,
            'PROCESSED',
            id=(
                'closed cell with accumulator, '
                'but fixture will return `no accumulator`'
            ),
            marks=pytest.mark.pgsql(
                'scooter_accumulator',
                files=['in_process_closed_cell_with_acc.sql'],
            ),
        ),
        pytest.param(
            1,
            'PROCESSED',
            id='opened cell without accumulator',
            marks=pytest.mark.pgsql(
                'scooter_accumulator', files=['in_process_opened_cell.sql'],
            ),
        ),
        pytest.param(
            0,
            'PROCESSED',
            id='booking in `PROCESSED` status',
            marks=pytest.mark.pgsql(
                'scooter_accumulator', files=['processed_cell.sql'],
            ),
        ),
        pytest.param(
            0,
            'DEFERRED_PROCESSED',
            id='booking in `DEFERRED_PROCESSED` status',
            marks=pytest.mark.pgsql(
                'scooter_accumulator', files=['deferred_processed_cell.sql'],
            ),
        ),
        pytest.param(
            0,
            'PROCESSED',
            id='booking in `PROCESSED` status in cabinet_without_validation',
            marks=pytest.mark.pgsql(
                'scooter_accumulator',
                files=['processed_cabinet_without_validation.sql'],
            ),
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator,
        testpoint,
        tp_cell_statuses,
        pgsql,
        mqtt_fixture_times_called,
        booking_status,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_cell_statuses[data['commands'][0]['arguments']['cell_id']]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': BOOKING_ID1}, json={},
    )

    assert response.status_code == 200
    assert response.json() == {'cell_id': CELL_ID3}
    assert mqtt_cabinet_response.times_called == mqtt_fixture_times_called

    assert sql.select_bookings_info(pgsql, BOOKING_ID1) == [
        (BOOKING_ID1, booking_status, CONTRACTOR_ID1, ACCUMULATOR_ID1),
    ]
    assert sql.select_cells_info(pgsql, CELL_ID3, select_is_open=True) == [
        (CELL_ID3, None, BOOKING_ID1, False),
    ]


@pytest.mark.parametrize(
    'booking_id, booking_status, cell_id, '
    'booking_accumulator_id, cell_accumulator_id',
    [
        pytest.param(
            BOOKING_ID1,
            'CREATED',
            CELL_ID1,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID1,
            id='booking in CREATED status',
        ),
        pytest.param(
            BOOKING_ID2,
            'VALIDATED',
            CELL_ID2,
            ACCUMULATOR_ID2,
            None,
            id='booking in VALIDATED status',
        ),
        pytest.param(
            BOOKING_ID3,
            'REVOKED',
            CELL_ID3,
            None,
            None,
            id='booking in REVOEKD status',
        ),
    ],
)
@pytest.mark.pgsql('scooter_accumulator', files=['bad_booking_status.sql'])
async def test_bad_booking_status(
        taxi_scooter_accumulator,
        pgsql,
        booking_id,
        booking_status,
        cell_id,
        booking_accumulator_id,
        cell_accumulator_id,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': booking_id}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'cell_id': cell_id,
        'code': 'check_processed_failed',
        'message': f'booking has `{booking_status}` status',
    }

    assert sql.select_bookings_info(pgsql, booking_id) == [
        (booking_id, booking_status, CONTRACTOR_ID1, booking_accumulator_id),
    ]
    assert sql.select_cells_info(pgsql, cell_id, select_is_open=True) == [
        (cell_id, cell_accumulator_id, booking_id, False),
    ]


@pytest.mark.parametrize(
    'booking_id, booking_status, message_end, cell_id, '
    'booking_accumulator_id, cell_accumulator_id',
    [
        pytest.param(
            BOOKING_ID1,
            'CREATED',
            '',
            CELL_ID1,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID1,
            id='booking in CREATED status',
        ),
        pytest.param(
            BOOKING_ID2,
            'VALIDATED',
            '',
            CELL_ID2,
            ACCUMULATOR_ID2,
            None,
            id='booking in VALIDATED status',
        ),
        pytest.param(
            BOOKING_ID3,
            'REVOKED',
            '',
            CELL_ID3,
            None,
            None,
            id='booking in REVOEKD status',
        ),
        pytest.param(
            BOOKING_ID4,
            'DEFERRED_PROCESSED',
            ' not in cabinet_without_validation',
            CELL_ID4,
            None,
            None,
            id='booking in DEFERRED_PROCESSED status',
        ),
    ],
)
@pytest.mark.pgsql(
    'scooter_accumulator',
    files=['bad_cabinet_without_validation_booking_status.sql'],
)
async def test_bad_cabinet_without_validation_booking_status(
        taxi_scooter_accumulator,
        pgsql,
        booking_id,
        booking_status,
        message_end,
        cell_id,
        booking_accumulator_id,
        cell_accumulator_id,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': booking_id}, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'cell_id': cell_id,
        'code': 'check_processed_failed',
        'message': f'booking has `{booking_status}` status{message_end}',
    }

    assert sql.select_bookings_info(pgsql, booking_id) == [
        (booking_id, booking_status, CONTRACTOR_ID1, booking_accumulator_id),
    ]
    assert sql.select_cells_info(pgsql, cell_id, select_is_open=True) == [
        (cell_id, cell_accumulator_id, booking_id, False),
    ]


@pytest.mark.parametrize(
    'booking_id, cell_id, booking_accumulator_id, cell_accumulator_id, '
    'is_open, response_json',
    [
        pytest.param(
            BOOKING_ID1,
            CELL_ID1,
            ACCUMULATOR_ID1,
            ACCUMULATOR_ID1,
            False,
            {
                'cell_id': CELL_ID1,
                'code': 'accumulator_was_not_taken',
                'message': f'please take accumulator from cell `{CELL_ID1}`',
            },
            id='accumulator_was_not_taken',
        ),
        pytest.param(
            BOOKING_ID2,
            CELL_ID2,
            ACCUMULATOR_ID2,
            None,
            True,
            {
                'cell_id': CELL_ID2,
                'code': 'cell_was_not_closed',
                'message': f'please close cell `{CELL_ID2}`',
            },
            id='cell_was_not_closed',
        ),
        pytest.param(
            BOOKING_ID3,
            CELL_ID3,
            None,
            None,
            False,
            {
                'cell_id': CELL_ID3,
                'code': 'accumulator_was_not_returned',
                'message': f'please put accumulator to cell `{CELL_ID3}`',
            },
            id='accumulator_was_not_returned',
        ),
    ],
)
@pytest.mark.pgsql('scooter_accumulator', files=['bad_cell_states.sql'])
async def test_bad_cell_states(
        taxi_scooter_accumulator,
        testpoint,
        tp_cell_statuses,
        pgsql,
        booking_id,
        cell_id,
        booking_accumulator_id,
        cell_accumulator_id,
        is_open,
        response_json,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_cell_statuses[data['commands'][0]['arguments']['cell_id']]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': booking_id}, json={},
    )

    assert response.status_code == 400
    assert response.json() == response_json
    assert mqtt_cabinet_response.times_called == 1

    assert sql.select_bookings_info(pgsql, booking_id) == [
        (booking_id, 'IN_PROCESS', CONTRACTOR_ID1, booking_accumulator_id),
    ]
    assert sql.select_cells_info(pgsql, cell_id, select_is_open=True) == [
        (cell_id, cell_accumulator_id, booking_id, is_open),
    ]


@pytest.mark.parametrize(
    'data',
    [
        pytest.param(
            {
                'booking_id': 'booking_id1',
                'cell_id': 'cell_id4',
                'booking_accumulator_id': '',
                'cell_accumulator_id': 'fake_id24',
                'is_open': False,
                'response_json': {'cell_id': 'cell_id4'},
            },
            id='new_fake_id',
        ),
    ],
)
@pytest.mark.pgsql('scooter_accumulator', files=['no_fake_id_in_cabinet.sql'])
async def test_no_fake_id_in_cabinet(
        taxi_scooter_accumulator, testpoint, tp_cell_statuses, pgsql, data,
):
    @testpoint(TESTPOINT_NAME)
    def mqtt_cabinet_response(data):
        return tp_cell_statuses[data['commands'][0]['arguments']['cell_id']]

    response = await taxi_scooter_accumulator.post(
        ENDPOINT, params={'booking_id': data['booking_id']}, json={},
    )

    assert response.status_code == 200
    assert response.json() == data['response_json']
    assert mqtt_cabinet_response.times_called == 1

    assert sql.select_cells_info(pgsql) == [
        ('cell_id1', 'accum_id1', None),
        ('cell_id2', 'fake_id23', None),
        ('cell_id4', 'fake_id24', 'booking_id1'),
    ]
