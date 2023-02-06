import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'params,expected_names',
    [
        (
            {'consumer': 'test_consumer'},
            [
                'first_experiment',
                'four_experiment',
                'second_experiment',
                'third_experiment',
            ],
        ),
        ({'consumer': '_1'}, ['first_experiment', 'third_experiment']),
        ({'consumer': '_2'}, ['second_experiment', 'third_experiment']),
        ({'consumer': '_3'}, ['four_experiment']),
        (
            {'consumers': ['_1', '_3']},
            ['first_experiment', 'four_experiment', 'third_experiment'],
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['fill.sql'])
async def test(taxi_exp_client, params, expected_names):
    data = experiment.generate_default()

    # adding experiments
    for name, consumers in (
            ('first_experiment', [{'name': 'test_consumer_1'}]),
            ('second_experiment', [{'name': 'test_consumer_2'}]),
            (
                'third_experiment',
                [
                    {'name': val}
                    for val in ['test_consumer_1', 'test_consumer_2']
                ],
            ),
            ('four_experiment', [{'name': 'test_consumer_3'}]),
    ):
        data['match']['consumers'] = consumers
        data['name'] = name
        await helpers.add_checked_exp(taxi_exp_client, data)

    if isinstance(params, dict):
        for key, value in params.items():
            if isinstance(value, list):
                params[key] = ','.join(str(item) for item in value)

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == expected_names
