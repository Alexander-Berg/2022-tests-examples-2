import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT = 'exp1'

NAMESPACES = ['market', 'not_market', None]


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_uplift_if_config_exists_in_different_namespace(taxi_exp_client):
    experiment_body = experiment.generate(name=EXPERIMENT, default_value={})
    await helpers.init_exp(
        taxi_exp_client, experiment_body, namespace='market',
    )

    experiment_body = experiment.generate_config(name=EXPERIMENT)
    await helpers.init_config(
        taxi_exp_client, experiment_body, namespace='not_market',
    )

    await helpers.uplift_to_config(
        taxi_exp_client, EXPERIMENT, namespace='market',
    )
