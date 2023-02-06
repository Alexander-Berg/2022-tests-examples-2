import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


NAME = 'experiment_with_salt'


@pytest.mark.parametrize(
    'expected_segmentation_method',
    [
        pytest.param(
            [],
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_save_salts': False}},
                },
            ),
        ),
        pytest.param(
            ['mod_sha1_with_salt', 'mod_sha1_with_salt'],
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_save_salts': True}},
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test(taxi_exp_client, expected_segmentation_method):
    body = experiment.generate(
        name=NAME,
        match_predicate=experiment.allof_predicate(
            [
                experiment.mod_sha1_predicate(salt='aaaaaaa'),
                experiment.mod_sha1_predicate(salt='bbbbbbb'),
            ],
        ),
    )

    await helpers.init_exp(taxi_exp_client, body)

    response = await db.get_salts(taxi_exp_client.app)
    assert [
        item['segmentation_method'] for item in response
    ] == expected_segmentation_method
