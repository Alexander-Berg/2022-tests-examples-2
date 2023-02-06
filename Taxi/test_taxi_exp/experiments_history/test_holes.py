import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files


EXPERIMENT_1_NAME = 'experiment_1'
EXPERIMENT_2_NAME = 'experiment_2'
EXPERIMENT_3_NAME = 'experiment_without_tag'
TAG = 'tag'


async def check_experiments_by_tag(app):
    result = await db.get_experiments_by_tag(app, TAG)
    assert len(result) == 2
    assert result[0]['name'] == EXPERIMENT_1_NAME
    assert result[1]['name'] == EXPERIMENT_2_NAME


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_holes(taxi_exp_client):
    # create tag
    response = await files.post_trusted_file(
        taxi_exp_client, TAG, b'trusted content',
    )
    assert response.status == 200

    # body experiment with tag
    data = experiment.generate(
        match_predicate=experiment.userhas_predicate(TAG),
    )

    # experiment1 with tag
    await helpers.init_exp(taxi_exp_client, data, name=EXPERIMENT_1_NAME)

    # experiment2 with tag
    await helpers.init_exp(taxi_exp_client, data, name=EXPERIMENT_2_NAME)

    # experiment3 without tag
    await helpers.init_exp(
        taxi_exp_client, experiment.generate(), name=EXPERIMENT_3_NAME,
    )

    # check experimets links to tag
    await check_experiments_by_tag(taxi_exp_client.app)
    # check len history
    assert len(await db.get_experiments_history(taxi_exp_client.app)) == 3

    # update tag
    response = await files.post_trusted_file(
        taxi_exp_client, TAG, b'trusted content new',
    )
    assert response.status == 200

    # check experimets links to tag
    await check_experiments_by_tag(taxi_exp_client.app)
    # check experiments history
    result = await db.get_experiments_history(taxi_exp_client.app)
    assert len(result) == 5
