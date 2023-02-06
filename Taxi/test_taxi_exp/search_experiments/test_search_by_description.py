import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'params,expected_names',
    [
        (
            {'description': 'XXX'},
            ['first_experiment', 'second_experiment', 'third_experiment'],
        ),
        ({'description': 'ZZZ'}, ['second_experiment', 'third_experiment']),
        ({'description': 'AAA'}, ['third_experiment']),
        ({'description': 'это'}, ['this_exp_1', 'this_exp_2']),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test(taxi_exp_client, params, expected_names):
    data = experiment.generate_default()

    # adding experiments
    for name, description in (
            ('first_experiment', 'XXX_YYY'),
            ('second_experiment', 'XXX_YYY_ZZZ'),
            ('third_experiment', 'XXX_YYY_ZZZ_AAA'),
            ('this_exp_1', 'ЭТО ЭКСПЕРИМЕНТ'),
            ('this_exp_2', 'это эксперимент'),
    ):
        data['description'] = description
        data['name'] = name
        await helpers.add_checked_exp(taxi_exp_client, data)

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == expected_names
