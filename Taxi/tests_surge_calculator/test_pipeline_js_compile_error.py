import pytest


@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_compile_error(taxi_surge_calculator, mock_admin_pipelines):
    request = {'point_a': [37.583369, 55.778821], 'classes': ['econom']}
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 1.0, 'surge': {'value': 1.0}},
        ],
        'experiments': [],
        'experiment_errors': [
            {
                'error': {
                    'message': (
                        'JS compile error: at 0:27 at stage \'main\': '
                        'SyntaxError: Unexpected token \'!\''
                    ),
                },
                'experiment_id': 'a29e6a811131450f9a28337906594208',
                'experiment_name': 'my_experiment',
            },
        ],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    actual = response.json()
    assert response.status == 200

    actual.pop('calculation_id')
    assert actual == expected
