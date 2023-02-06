import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

TECH_CONFIG_NAME = 'tech_config'
CONFIG_NAME = 'config'
EXP_NAME = 'exp'


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_search_with_order(taxi_exp_client):
    # create config, tech_config and exp
    body = experiment.generate_config(name=TECH_CONFIG_NAME, is_technical=True)
    await helpers.init_config(taxi_exp_client, body)

    body = experiment.generate_config(name=CONFIG_NAME)
    await helpers.init_config(taxi_exp_client, body)

    body = experiment.generate(name=EXP_NAME)
    await helpers.init_exp(taxi_exp_client, body)

    # search all configs
    response = await taxi_exp_client.get(
        '/v1/configs/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = [exp['name'] for exp in (await response.json())['configs']]
    assert result == ['config', 'tech_config']

    # search tech configs
    response = await taxi_exp_client.get(
        '/v1/configs/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'is_technical': 'true'},
    )
    assert response.status == 200
    result = [exp['name'] for exp in (await response.json())['configs']]
    assert result == ['tech_config']

    # search non-tech configs
    response = await taxi_exp_client.get(
        '/v1/configs/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'is_technical': 'false'},
    )
    assert response.status == 200
    result = [exp['name'] for exp in (await response.json())['configs']]
    assert result == ['config']
