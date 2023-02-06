import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/admin-api/accumulator/list'

RESPONSE1 = {
    'accumulators': [
        {
            'accumulator_id': 'accum_id1',
            'charge': 95,
            'place': {
                'cabinet': {
                    'cabinet_id': 'cabinet_id2',
                    'cell_id': 'cell_id4',
                },
            },
            'serial_number': 'serial_number1',
        },
        {
            'accumulator_id': 'accumulator_id_so_new',
            'charge': 33,
            'place': {
                'cabinet': {
                    'cabinet_id': 'cabinet_id3',
                    'cell_id': 'cell_id5',
                },
            },
            'serial_number': 'serial_number6',
        },
        {
            'accumulator_id': 'accumulator_id_new',
            'charge': 55,
            'place': {'scooter_id': 'scooter_id7'},
            'serial_number': 'serial_number7',
        },
    ],
}


@pytest.mark.parametrize(
    'json_, response_expected',
    [
        pytest.param(
            {
                'accumulators_patch_requests': [
                    {
                        'serial_number': 'serial_number1',
                        'patch_request': {
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
                    },
                    {
                        'serial_number': 'serial_number6',
                        'patch_request': {
                            'set': {
                                'place': {
                                    'cabinet': {'cabinet_id': 'cabinet_id3'},
                                    'scooter_id': None,
                                },
                                'charge': 33,
                                'accumulator_id': 'accumulator_id_so_new',
                            },
                            'unset': ['scooter_id'],
                        },
                    },
                    {
                        'serial_number': 'serial_number7',
                        'patch_request': {
                            'set': {
                                'place': {
                                    'cabinet': {'cabinet_id': None},
                                    'scooter_id': 'scooter_id7',
                                },
                                'charge': 55,
                                'accumulator_id': 'accumulator_id_new',
                            },
                            'unset': ['cabinet_id'],
                        },
                    },
                ],
            },
            RESPONSE1,
            id='cell provided, cell not provided, from cell to scooter',
        ),
    ],
)
async def test_ok(taxi_scooter_accumulator, pgsql, json_, response_expected):
    response = await taxi_scooter_accumulator.patch(ENDPOINT, json=json_)

    assert response.status_code == 200

    response_accumulators = response.json()['accumulators']
    expected_accumulators = response_expected['accumulators']
    requests = json_['accumulators_patch_requests']

    for i, _ in enumerate(response_accumulators):
        accumulator_id = response_accumulators[i]['accumulator_id']

        assert accumulator_id == expected_accumulators[i]['accumulator_id']
        assert (
            response_accumulators[i]['serial_number']
            == expected_accumulators[i]['serial_number']
        )
        assert (
            response_accumulators[i]['charge']
            == expected_accumulators[i]['charge']
        )
        assert (
            response_accumulators[i]['place']
            == expected_accumulators[i]['place']
        )

        if requests[i]['patch_request']['set']['charge'] is None:
            requests[i]['patch_request']['set']['charge'] = 95

        accumulators_info = sql.select_accumulators_info(
            pgsql,
            serial_number=requests[i]['serial_number'],
            select_charge=True,
            select_serial_number=True,
        )

        assert accumulators_info == [
            (
                accumulator_id,
                None,
                requests[i]['patch_request']['set']['place']['cabinet'][
                    'cabinet_id'
                ],
                requests[i]['patch_request']['set']['place']['scooter_id'],
                requests[i]['patch_request']['set']['charge'],
                requests[i]['serial_number'],
            ),
        ]

        cell_id = ''
        if (
                'cell_id'
                not in requests[i]['patch_request']['set']['place']['cabinet']
        ):
            if requests[i]['patch_request']['set']['place']['cabinet'][
                    'cabinet_id'
            ]:
                cell_id = 'cell_id5'
            else:
                cell_id = 'cell_id10'
                accumulator_id = None
        else:
            cell_id = requests[i]['patch_request']['set']['place']['cabinet'][
                'cell_id'
            ]

        assert sql.select_cells_info(pgsql, cell_id) == [
            (cell_id, accumulator_id, None),
        ]


@pytest.mark.parametrize(
    'json_, message',
    [
        pytest.param(
            {
                'accumulators_patch_requests': [
                    {
                        'serial_number': 'serial_number1',
                        'patch_request': {
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
                    },
                    {
                        'serial_number': 'serial_number7',
                        'patch_request': {
                            'set': {
                                'place': {
                                    'cabinet': {
                                        'cabinet_id': 'cabinet_id2',
                                        'cell_id': 'cell_id4',
                                    },
                                },
                                'charge': 55,
                            },
                            'unset': [],
                        },
                    },
                ],
            },
            'kAccumulatorsCellsUpdate: cell with id `cell_id4`'
            ' is already occupied by accumulator'
            ' with serial number: `serial_number1`, trying to put accumulator'
            ' with serial number: `serial_number7`. ',
            id='accumulator coflict, move in similar cell',
        ),
        pytest.param(
            {
                'accumulators_patch_requests': [
                    {
                        'serial_number': 'serial_number1',
                        'patch_request': {
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
                    },
                    {
                        'serial_number': 'serial_number7',
                        'patch_request': {
                            'set': {
                                'place': {
                                    'cabinet': {
                                        'cabinet_id': 'cabinet_id4',
                                        'cell_id': 'cell_id9',
                                    },
                                },
                                'charge': 55,
                            },
                            'unset': [],
                        },
                    },
                ],
            },
            'kAccumulatorsCellsUpdate: cell with id `cell_id9`'
            ' is already occupied by'
            ' accumulator with serial number: `serial_number5`,'
            ' trying to put accumulator with serial number:'
            ' `serial_number7`. ',
            id='first correct, second with accumulator conflict',
        ),
        pytest.param(
            {
                'accumulators_patch_requests': [
                    {
                        'serial_number': 'serial_number1',
                        'patch_request': {
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
                    },
                    {
                        'serial_number': 'serial_number7',
                        'patch_request': {
                            'set': {
                                'place': {
                                    'cabinet': {
                                        'cabinet_id': 'cabinet_id1234',
                                        'cell_id': 'cell_id9',
                                    },
                                },
                                'charge': 55,
                            },
                            'unset': [],
                        },
                    },
                ],
            },
            None,
            id='first correct, second with cabinet not exists',
        ),
        pytest.param(
            {
                'accumulators_patch_requests': [
                    {
                        'serial_number': 'serial_number1',
                        'patch_request': {
                            'set': {
                                'charge': 25,
                                'accumulator_id': (
                                    'accumulator_id_extremely_desired'
                                ),
                            },
                            'unset': [],
                        },
                    },
                    {
                        'serial_number': 'serial_number7',
                        'patch_request': {
                            'set': {
                                'place': {
                                    'cabinet': {
                                        'cabinet_id': 'cabinet_id2',
                                        'cell_id': 'cell_id4',
                                    },
                                },
                                'accumulator_id': (
                                    'accumulator_id_extremely_desired'
                                ),
                                'charge': 52,
                            },
                            'unset': [],
                        },
                    },
                ],
            },
            None,
            id='accumulator coflict, set similar accumulator_id to both',
        ),
    ],
)
async def test_bad(taxi_scooter_accumulator, pgsql, json_, message):
    response = await taxi_scooter_accumulator.patch(ENDPOINT, json=json_)

    assert response.status_code == 400
    response_json = response.json()

    assert response_json['code'] == '400'
    if message:
        assert response_json['message'] == message
    else:
        assert response_json['message']
