import pytest


@pytest.mark.parametrize(
    ['query', 'expected_ids'],
    [
        pytest.param('', {str(i) for i in range(1, 14)}, id='Full list'),
        pytest.param(
            '?kind=recharging_wire',
            [
                '1',
                '10',
                '11',
                '12',
                '13',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
            ],
            id='By kind',
        ),
        pytest.param('?depot_id=depot2', ['4', '5', '6'], id='By depot'),
        pytest.param(
            '?performer_id=performer5', ['8', '9', '11'], id='By performer',
        ),
        pytest.param(
            '?available=true',
            ['12', '13'],
            id='Available(w/o performer and task_id)',
        ),
        pytest.param(
            '?depot_id=depot1&performer_id=performer5',
            ['8'],
            id='By depot & performer',
        ),
        pytest.param(
            '?kind=recharging_wire&available=false',
            ['1', '10', '11', '2', '3', '4', '5', '6', '7', '8', '9'],
            id='By kind & available',
        ),
        pytest.param(
            '?recharge_task_id=recharge_task4',
            ['6', '9'],
            id='By recharge_task_id',
        ),
    ],
)
async def test_tackles_filter(taxi_scooters_misc, query, expected_ids):
    res = await taxi_scooters_misc.get(f'/v1/tackles/list{query}')
    assert res.status_code == 200
    ids = sorted([tackle['id'] for tackle in res.json()['tackles']])
    assert ids == sorted(expected_ids)


async def test_tackles_struct(taxi_scooters_misc):
    res = await taxi_scooters_misc.get(f'/v1/tackles/list')
    assert res.status_code == 200
    assert res.json()['tackles'][0] == {
        'id': '1',
        'kind': 'recharging_wire',
        'depot_id': 'depot1',
        'recharge_task_id': 'recharge_task1',
        'performer_id': 'performer1',
        'version': 1,
    }


@pytest.mark.parametrize(
    ['available', 'expected_code'],
    [
        pytest.param(
            'true',
            400,
            id='Trying to filter with performer and available: true both',
        ),
        pytest.param(
            'false', 200, id='By performer(degenerate available field)',
        ),
    ],
)
async def test_tackles_error(taxi_scooters_misc, available, expected_code):
    res = await taxi_scooters_misc.get(
        f'/v1/tackles/list?performer_id=performer1&available={available}',
    )
    assert res.status_code == expected_code
