import pytest


async def test_picker_change_priority_post_empty_db(taxi_eats_picker_supply):
    response = await taxi_eats_picker_supply.post(
        '/api/v1/picker/change-priority',
        {'picker_id': '123456', 'add': 1.0, 'multiply': 2.0},
    )

    assert response.status == 404
    assert response.json() == {
        'code': '404',
        'message': 'Picker wasn\'t found',
    }


async def test_picker_change_priority_post_without_picker_id(
        taxi_eats_picker_supply, create_picker,
):
    create_picker('123456')
    response = await taxi_eats_picker_supply.post(
        '/api/v1/picker/change-priority', {'add': 1.0, 'multiply': 2.0},
    )

    assert response.status == 400


@pytest.mark.parametrize(
    'params, expected',
    [
        pytest.param(
            {'picker_id': '123456', 'add': 1.0, 'multiply': 2.0},
            {'picker_id': '123456', 'priority': 3.0},
            id='Test with add and multiply',
        ),
        pytest.param(
            {'picker_id': '123456', 'multiply': 2.0},
            {'picker_id': '123456', 'priority': 2.0},
            id='Test with multiply only',
        ),
        pytest.param(
            {'picker_id': '123456', 'add': 4.0},
            {'picker_id': '123456', 'priority': 5.0},
            id='Test with add only',
        ),
        pytest.param(
            {'picker_id': '123456', 'add': 0.0, 'multiply': 2.0},
            {'picker_id': '123456', 'priority': 2.0},
            id='Test with multiply and add=0',
        ),
        pytest.param(
            {'picker_id': '123456', 'add': 4.0, 'multiply': 1.0},
            {'picker_id': '123456', 'priority': 5.0},
            id='Test with add and multiply=1',
        ),
        pytest.param(
            {'picker_id': '123456'},
            {'picker_id': '123456', 'priority': 1.0},
            id='Test without add and multiply',
        ),
    ],
)
async def test_picker_change_priority_post(
        taxi_eats_picker_supply, create_picker, get_picker, params, expected,
):
    picker_id = create_picker(params['picker_id'])
    response = await taxi_eats_picker_supply.post(
        '/api/v1/picker/change-priority', params,
    )

    assert response.status == 200
    rez = get_picker(picker_id)
    assert rez[1] == expected['picker_id']
    assert rez[8] == expected['priority']
