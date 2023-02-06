import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'with_traits_experiment'


@pytest.mark.parametrize(
    'first_body,first_trait_tags,second_body,second_trait_tags',
    [
        (
            experiment.generate(name=EXPERIMENT_NAME, enable_debug=True),
            ['enable-debug'],
            experiment.generate(
                name=EXPERIMENT_NAME, last_modified_at=1, enable_debug=False,
            ),
            [],
        ),
        (
            experiment.generate(name=EXPERIMENT_NAME, enable_debug=False),
            [],
            experiment.generate(
                name=EXPERIMENT_NAME, last_modified_at=1, enable_debug=True,
            ),
            ['enable-debug'],
        ),
        (
            experiment.generate(name=EXPERIMENT_NAME, enable_debug=True),
            ['enable-debug'],
            experiment.generate(
                name=EXPERIMENT_NAME, last_modified_at=1, enable_debug=True,
            ),
            ['enable-debug'],
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test(
        taxi_exp_client,
        first_body,
        first_trait_tags,
        second_body,
        second_trait_tags,
):
    result = await helpers.init_exp(taxi_exp_client, first_body)
    assert result['trait_tags'] == first_trait_tags

    result = await helpers.update_exp(taxi_exp_client, second_body)
    assert result['trait_tags'] == second_trait_tags
