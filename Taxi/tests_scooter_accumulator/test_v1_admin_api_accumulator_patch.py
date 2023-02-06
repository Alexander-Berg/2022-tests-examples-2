import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/admin-api/accumulator'

ACCUM_RESPONSE1 = {
    'accumulator_id': 'accum_id1',
    'serial_number': 'serial_number1',
    'charge': 95,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id4'}},
}

ACCUM_RESPONSE2 = {
    'accumulator_id': 'accum_id_new',
    'serial_number': 'serial_number1',
    'charge': 0,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id3', 'cell_id': 'cell_id5'}},
}

ACCUM_RESPONSE3 = {
    'accumulator_id': 'accum_id_more_new',
    'serial_number': 'serial_number1',
    'charge': 95,
    'place': {'scooter_id': 'scooter_id1'},
}

ACCUM_RESPONSE4 = {
    'accumulator_id': 'accum_id6',
    'serial_number': 'serial_number6',
    'charge': 20,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id4'}},
}

ACCUM_RESPONSE5 = {
    'accumulator_id': 'accum_id1',
    'serial_number': 'serial_number1',
    'charge': 20,
    'place': {},
}

ACCUM_RESPONSE6 = {
    'accumulator_id': 'accum_id1',
    'serial_number': 'serial_number1',
    'charge': 95,
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id1'}},
}

ACCUM_RESPONSE7 = {
    'accumulator_id': 'accum_id7',
    'serial_number': 'serial_number7',
    'charge': 95,
    'place': {
        'cabinet': {'cabinet_id': 'cabinet_id7', 'cell_id': 'cell_id10'},
    },
}


@pytest.mark.parametrize(
    'json_, serial_number, response_expected',
    [
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id4',
                        },
                        'scooter_id': None,
                    },
                    'charge': None,
                },
                'unset': [],
            },
            'serial_number1',
            ACCUM_RESPONSE1,
            id='correct insert cell provided',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id3',
                            'cell_id': None,
                        },
                        'scooter_id': None,
                    },
                    'charge': 0,
                    'accumulator_id': 'accum_id_new',
                },
                'unset': [],
            },
            'serial_number1',
            ACCUM_RESPONSE2,
            id='correct insert cell no provided, accumulator_id update',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {'cabinet_id': None, 'cell_id': None},
                        'scooter_id': 'scooter_id1',
                    },
                    'charge': None,
                    'accumulator_id': 'accum_id_more_new',
                },
                'unset': ['cabinet_id'],
            },
            'serial_number1',
            ACCUM_RESPONSE3,
            id='from cabinet to scooter, accumulator_id update',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id4',
                        },
                        'scooter_id': None,
                    },
                    'charge': 20,
                },
                'unset': ['scooter_id'],
            },
            'serial_number6',
            ACCUM_RESPONSE4,
            id='from scooter to cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {'cabinet_id': None, 'cell_id': None},
                        'scooter_id': None,
                    },
                    'charge': 20,
                },
                'unset': ['cabinet_id'],
            },
            'serial_number1',
            ACCUM_RESPONSE5,
            id='move from cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id1',
                        },
                        'scooter_id': None,
                    },
                    'charge': 95,
                },
                'unset': [],
            },
            'serial_number1',
            ACCUM_RESPONSE6,
            id='emulate retry, cell provided',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id7',
                            'cell_id': None,
                        },
                        'scooter_id': None,
                    },
                    'charge': 95,
                },
                'unset': [],
            },
            'serial_number7',
            ACCUM_RESPONSE7,
            id='emulate retry, cell not provided',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator,
        pgsql,
        json_,
        serial_number,
        response_expected,
):
    response = await taxi_scooter_accumulator.patch(
        ENDPOINT, params={'serial_number': serial_number}, json=json_,
    )

    assert response.status_code == 200

    response_json = response.json()

    accumulator_id = response_json['accumulator_id']

    assert accumulator_id == response_expected['accumulator_id']
    assert response_json['serial_number'] == response_expected['serial_number']
    assert response_json['charge'] == response_expected['charge']
    assert response_json['place'] == response_expected['place']

    if json_['set']['charge'] is None:
        json_['set']['charge'] = 95

    accumulators_info = sql.select_accumulators_info(
        pgsql,
        serial_number=serial_number,
        select_charge=True,
        select_serial_number=True,
    )

    assert accumulators_info == [
        (
            accumulator_id,
            None,
            json_['set']['place']['cabinet']['cabinet_id'],
            json_['set']['place']['scooter_id'],
            json_['set']['charge'],
            serial_number,
        ),
    ]

    if not json_['set']['place']['cabinet']['cell_id']:
        if not accumulator_id == 'accum_id7':
            json_['set']['place']['cabinet']['cell_id'] = 'cell_id5'
        else:
            json_['set']['place']['cabinet']['cell_id'] = 'cell_id10'

    if json_['set']['place']['scooter_id']:
        accumulator_id = None

    if 'cabinet_id' not in set(json_['unset']):
        assert (
            sql.select_cells_info(
                pgsql, json_['set']['place']['cabinet']['cell_id'],
            )
            == [
                (
                    json_['set']['place']['cabinet']['cell_id'],
                    accumulator_id,
                    None,
                ),
            ]
        )
    else:
        assert sql.select_cells_info(pgsql, 'cell_id1') == [
            ('cell_id1', None, None),
        ]


@pytest.mark.parametrize(
    'json_, serial_number',
    [
        pytest.param(
            {'set': {'charge': 33}, 'unset': []},
            'serial_number1',
            id='do not move anywhere, place not provided',
        ),
        pytest.param(
            {'set': {'place': {}, 'charge': 33}, 'unset': []},
            'serial_number1',
            id='do not move anywhere, empty place',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {'cabinet_id': None, 'cell_id': None},
                        'scooter_id': None,
                    },
                    'charge': 33,
                },
                'unset': [],
            },
            'serial_number1',
            id='do not move anywhere, place fields are explicitly NULL',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {'cabinet_id': None, 'cell_id': None},
                        'scooter_id': 'scooter_id1',
                    },
                    'charge': 33,
                },
                'unset': [],
            },
            'serial_number1',
            id='to scooter, stay in cabinet',
        ),
        pytest.param(
            {
                'set': {'charge': 21, 'accumulator_id': 'accum_id_the_newest'},
                'unset': [],
            },
            'serial_number1',
            id='accumulator_id update',
        ),
    ],
)
async def test_not_move_from_prev(
        taxi_scooter_accumulator, pgsql, json_, serial_number,
):
    response = await taxi_scooter_accumulator.patch(
        ENDPOINT, params={'serial_number': serial_number}, json=json_,
    )

    accumulator_id = response.json()['accumulator_id']

    assert response.status_code == 200

    scooter_id = None
    if ('place' in json_['set']) and ('scooter_id' in json_['set']['place']):
        scooter_id = json_['set']['place']['scooter_id']

    assert response.json()['place']['cabinet'] == {
        'cabinet_id': 'cabinet_id2',
        'cell_id': 'cell_id1',
    }

    if scooter_id:
        assert scooter_id == response.json()['place']['scooter_id']

    assert (
        sql.select_accumulators_info(
            pgsql,
            accumulator_id,
            select_charge=True,
            select_serial_number=True,
        )
        == [
            (
                accumulator_id,
                None,
                'cabinet_id2',
                scooter_id,
                json_['set']['charge'],
                'serial_number1',
            ),
        ]
    )

    assert sql.select_cells_info(pgsql, 'cell_id1') == [
        ('cell_id1', accumulator_id, None),
    ]


@pytest.mark.parametrize(
    'json_, serial_number, accum_row, message',
    [
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {'cabinet_id': None, 'cell_id': 'cell_id1'},
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'cell_id without cabinet_id',
            id='cell without cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id1',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number333',
            (),
            'kAccumulatorsCellsUpdate: accumulator with'
            ' serial number `serial_number333` not found.',
            id='no existent accumulator',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id333',
                            'cell_id': None,
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            None,
            id='not existent cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id55',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: cell with id `cell_id55` '
            'was not found.',
            id='not existent cell',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id1',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number2',
            (
                'accum_id2',
                None,
                'aretl8d4gho7e6i3tvn1',
                None,
                'serial_number2',
            ),
            'kAccumulatorsCellsUpdate: cell with id `cell_id1`'
            ' is already occupied'
            ' by accumulator with serial number: `serial_number1`, trying'
            ' to put accumulator with serial number: `serial_number2`. ',
            id='accumulator conflict',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id4',
                            'cell_id': None,
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: no empty and unbooked'
            ' cells in cabinet with id `cabinet_id4`.',
            id='no empty cells',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id5',
                            'cell_id': None,
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: no empty and unbooked cells in cabinet '
            'with id `cabinet_id5`.',
            id='no unbooked cells',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id3',
                            'cell_id': 'cell_id6',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: cell is booked, '
            'bookind_id `booking_id4`.',
            id='cell is booked, cabinet type = cabinet, move from cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id3',
                            'cell_id': 'cell_id6',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number6',
            ('accum_id6', None, None, 'scooter_id1', 'serial_number6'),
            'kAccumulatorsCellsUpdate: cell is booked, '
            'bookind_id `booking_id4`.',
            id='cell is booked, cabinet type = cabinet, move from scooter',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id4',
                            'cell_id': 'cell_id9',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: cell with id `cell_id9`'
            ' is already occupied by '
            'accumulator with serial number: `serial_number5`, trying'
            ' to put accumulator with serial number:'
            ' `serial_number1`.'
            ' kAccumulatorsCellsUpdate: cell is booked, '
            'bookind_id `booking_id7`.',
            id='cell is booked and not emty, cabinet type = cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id6',
                            'cell_id': 'cell_id8',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: cell is booked, bookind_id '
            '`booking_id6`.',
            id='cell is booked, cabinet type = charge station',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id6',
                            'cell_id': None,
                        },
                    },
                },
                'unset': [],
            },
            'serial_number1',
            ('accum_id1', None, 'cabinet_id2', None, 'serial_number1'),
            'kAccumulatorsCellsUpdate: cell no provided for cabinet with '
            'id `cabinet_id6` and type `charge_station`.',
            id='cell no provided for charge station',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id2',
                            'cell_id': 'cell_id4',
                        },
                    },
                },
                'unset': [],
            },
            'serial_number5',
            ('accum_id5', None, 'cabinet_id4', None, 'serial_number5'),
            'kAccumulatorsCellsUpdate: accumulator with serial'
            ' number `serial_number5` exists '
            'in booked cell with id `cell_id9`, bookind_id is `booking_id7`.',
            id='accumulator exists in booked cell, move to cabinet',
        ),
        pytest.param(
            {'set': {'place': {'scooter_id': 'scooter_id1'}}, 'unset': []},
            'serial_number5',
            ('accum_id5', None, 'cabinet_id4', None, 'serial_number5'),
            'kAccumulatorsCellsUpdate: accumulator with'
            ' serial number `serial_number5` exists '
            'in booked cell with id `cell_id9`, bookind_id is `booking_id7`.',
            id='accumulator exists in booked cell, move to scooter',
        ),
        pytest.param(
            {
                'set': {
                    'place': {
                        'cabinet': {
                            'cabinet_id': 'cabinet_id3',
                            'cell_id': 'cell_id6',
                        },
                    },
                },
                'unset': ['cabinet_id'],
            },
            'serial_number6',
            ('accum_id6', None, None, 'scooter_id1', 'serial_number6'),
            'kAccumulatorsCellsUpdate: cabinet_id is null '
            'with cabinet_id `cabinet_id3` provided,'
            ' accumulator serial number: `serial_number6`',
            id='cabinet_id is null with cabinet provided',
        ),
    ],
)
async def test_bad(
        pgsql,
        taxi_scooter_accumulator,
        json_,
        serial_number,
        accum_row,
        message,
):
    response = await taxi_scooter_accumulator.patch(
        ENDPOINT, params={'serial_number': serial_number}, json=json_,
    )

    assert response.status_code == 400

    response_json = response.json()

    assert response_json['code'] == '400'
    if message:
        assert response_json['message'] == message
    else:
        assert response_json['message']

    accumulators_info = sql.select_accumulators_info(
        pgsql, serial_number=serial_number, select_serial_number=True,
    )

    assert accumulators_info == [accum_row]
