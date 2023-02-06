import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXP_SERVICES = [1, 2, 10]


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_search_by_service_id(taxi_exp_client):
    # create experiments with different service_id
    for service in EXP_SERVICES:
        await helpers.init_exp(
            taxi_exp_client,
            experiment.generate(
                name='exp_with_service_' + str(service), service_id=service,
            ),
            namespace='market',
        )

    # search all experiments
    response = await helpers.get_experiments_list(
        taxi_exp_client, namespace='market',
    )
    assert response.status == 200
    result = [exp['name'] for exp in (await response.json())['experiments']]
    assert sorted(result) == sorted(
        ['exp_with_service_' + str(service) for service in EXP_SERVICES],
    )

    # search by specific service
    response = await helpers.get_experiments_list(
        taxi_exp_client, service_id=1, namespace='market',
    )
    assert response.status == 200
    result = [exp['name'] for exp in (await response.json())['experiments']]
    assert result == ['exp_with_service_1']
