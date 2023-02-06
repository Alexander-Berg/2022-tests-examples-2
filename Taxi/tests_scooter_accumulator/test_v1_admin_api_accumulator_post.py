import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/admin-api/accumulator'
CONSUMER_ID = 'consumer_id1'


ACCUM_RESPONSE1 = {
    'accumulator_id': 'accum_id_new',
    'serial_number': 'serial_number_new',
    'charge': 0,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id4'}},
}

ACCUM_RESPONSE2 = {
    'accumulator_id': 'accum_id_new',
    'serial_number': 'serial_number_new',
    'charge': 0,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id3', 'cell_id': 'cell_id5'}},
}

ACCUM_RESPONSE3 = {
    'accumulator_id': 'accum_id_new',
    'serial_number': 'serial_number_new',
    'charge': 0,
    'place': {'scooter_id': 'scooter_id1'},
}

ACCUM_RESPONSE4 = {
    'accumulator_id': 'accum_id1',
    'serial_number': 'serial_number1',
    'charge': 95,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id1'}},
}


@pytest.mark.parametrize(
    'idempotency_token, json_, response_expected',
    [
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id2',
                'cell_id': 'cell_id4',
                'scooter_id': None,
                'charge': None,
            },
            ACCUM_RESPONSE1,
            id='correct insert cell provided',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id3',
                'cell_id': None,
                'scooter_id': None,
                'charge': 0,
            },
            ACCUM_RESPONSE2,
            id='correct insert cell no provided',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': None,
                'cell_id': None,
                'scooter_id': 'scooter_id1',
                'charge': 0,
            },
            ACCUM_RESPONSE3,
            id='correct insert in scooter',
        ),
        pytest.param(
            '0000000000000001',
            {
                'accumulator_id': 'accum_id1',
                'serial_number': 'serial_number1',
                'cabinet_id': 'cabinet_id2',
                'cell_id': 'cell_id1',
                'scooter_id': None,
                'charge': 95,
            },
            ACCUM_RESPONSE4,
            id='emulate retry',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator,
        pgsql,
        idempotency_token,
        json_,
        response_expected,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        json=json_,
        params={'consumer_id': CONSUMER_ID},
    )

    assert response.status_code == 200

    response_json = response.json()

    assert (
        response_json['accumulator_id'] == response_expected['accumulator_id']
    )
    assert response_json['serial_number'] == response_expected['serial_number']
    assert response_json['charge'] == response_expected['charge']
    assert response_json['place'] == response_expected['place']

    if not json_['charge']:
        json_['charge'] = 0

    assert (
        sql.select_accumulators_info(
            pgsql,
            json_['accumulator_id'],
            select_charge=True,
            select_serial_number=True,
        )
        == [
            (
                json_['accumulator_id'],
                None,
                json_['cabinet_id'],
                json_['scooter_id'],
                json_['charge'],
                json_['serial_number'],
            ),
        ]
    )

    if json_['cell_id']:
        assert sql.select_cells_info(pgsql, json_['cell_id']) == [
            (json_['cell_id'], json_['accumulator_id'], None),
        ]


@pytest.mark.parametrize(
    'idempotency_token, json_, accum_row, message',
    [
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id1',
                'serial_number': 'serial_number_new',
                'cabinet_id': None,
                'cell_id': None,
            },
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            None,
            id='existent accumulator id',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number1',
                'cabinet_id': None,
                'cell_id': None,
            },
            (),
            None,
            id='existent serial_number',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': None,
                'cell_id': 'cell_id1',
            },
            (),
            'cell_id without cabinet_id',
            id='cell without cabinet',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id333',
                'cell_id': None,
            },
            (),
            None,
            id='not existent cabinet',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id2',
                'cell_id': 'cell_id55',
            },
            (),
            'kAccumulatorsInsert: cell with id `cell_id55` was not found.',
            id='not existent cell',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id2',
                'cell_id': 'cell_id1',
            },
            (),
            'kAccumulatorsInsert: cell with id `cell_id1`'
            ' is already occupied by'
            ' accumulator with id: `accum_id1`,'
            ' trying to put accumulator with id: `accum_id_new`. ',
            id='accumulator conflict',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id4',
                'cell_id': None,
            },
            (),
            'kAccumulatorsInsert: no empty and unbooked cells in cabinet '
            'with id `cabinet_id4`.',
            id='no empty cells',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id5',
                'cell_id': None,
            },
            (),
            'kAccumulatorsInsert: no empty and unbooked cells in cabinet '
            'with id `cabinet_id5`.',
            id='no unbooked cells',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id3',
                'cell_id': 'cell_id6',
            },
            (),
            'kAccumulatorsInsert: cell is booked, bookind_id `booking_id4`.',
            id='cell is booked, cabinet type = cabinet',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id4',
                'cell_id': 'cell_id9',
            },
            (),
            'kAccumulatorsInsert: cell with id `cell_id9`'
            ' is already occupied by accumulator with'
            ' id: `accum_id5`, trying to put accumulator'
            ' with id: `accum_id_new`. kAccumulatorsInsert: cell is booked,'
            ' bookind_id `booking_id7`.',
            id='cell is booked and not emty, cabinet type = cabinet',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id6',
                'cell_id': 'cell_id8',
            },
            (),
            'kAccumulatorsInsert: cell is booked, bookind_id `booking_id6`.',
            id='cell is booked, cabinet type = charge station',
        ),
        pytest.param(
            '0000000000000006',
            {
                'accumulator_id': 'accum_id_new',
                'serial_number': 'serial_number_new',
                'cabinet_id': 'cabinet_id6',
                'cell_id': None,
            },
            (),
            'kAccumulatorsInsert: cell no provided for cabinet with '
            'id `cabinet_id6` and type `charge_station`.',
            id='cell no provided for charge station',
        ),
    ],
)
async def test_bad(
        pgsql,
        taxi_scooter_accumulator,
        idempotency_token,
        json_,
        accum_row,
        message,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        params={'consumer_id': CONSUMER_ID},
        json=json_,
    )

    assert response.status_code == 400

    response_json = response.json()

    assert response_json['code'] == '400'
    if message:
        assert response_json['message'] == message
    else:
        assert response_json['message']
    assert sql.select_accumulators_info(
        pgsql, json_['accumulator_id'], select_serial_number=True,
    ) == [accum_row]
