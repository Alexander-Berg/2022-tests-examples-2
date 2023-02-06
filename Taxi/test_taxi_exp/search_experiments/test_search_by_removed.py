import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_APPLICATION.format('ios'),
        db.ADD_APPLICATION.format('android'),
        db.ADD_CONSUMER.format('test_consumer'),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_experiment_removing': True}},
        # 'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
async def test_search_by_consumer(taxi_exp_client):
    data = experiment.generate_default()

    data = experiment.generate_default()

    # adding experiments
    last_modified_at = 0
    for exp_name, is_removed in (
            ('first_experiment', False),
            ('second_experiment', True),
            ('third_experiment', False),
            ('four_experiment', True),
    ):
        response = await taxi_exp_client.post(
            '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params={'name': exp_name},
            json=data,
        )
        assert response.status == 200, await response.text()
        last_modified_at += 1
        if is_removed:
            response = await taxi_exp_client.delete(
                '/v1/experiments/',
                headers={'YaTaxi-Api-Key': 'secret'},
                params={
                    'name': exp_name,
                    'last_modified_at': last_modified_at,
                },
            )
            assert response.status == 200, await response.text()
            last_modified_at += 1

    # check
    # get non-removed
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={},
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == [
        'first_experiment',
        'third_experiment',
    ]

    # get removed
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'show_removed': 'true'},
    )
    assert response.status == 200
    result = await response.json()
    assert [item['name'] for item in result['experiments']] == [
        'four_experiment',
        'second_experiment',
    ]
