import pytest

from taxi_exp.lib import predicates
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files

EXPERIMENT_NAME = 'experiment_with_tag_and_file'
TAG = 'yandex_phone_id'
MODIFICATION = 'close'


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
async def test_create_config_by_experiment_with_file_and_tag(taxi_exp_client):
    # upload file
    response = await files.post_file(taxi_exp_client, 'filename', b'content')
    data = await response.json()
    ordinal_file_id = data['id']

    # create tag
    response = await files.post_trusted_file(
        taxi_exp_client, 'yandex_phone_id', b'phone_id1\nphone_id2\n',
    )
    data = await response.json()

    # create experiment
    experiment_body = experiment.generate(
        EXPERIMENT_NAME,
        default_value={},
        match_predicate={
            'type': 'any_of',
            'init': {
                'predicates': [
                    {
                        'type': 'in_file',
                        'init': {
                            'set_elem_type': 'string',
                            'file': ordinal_file_id,
                            'arg_name': 'phone_id',
                        },
                    },
                    {'type': 'user_has', 'init': {'tag': 'yandex_phone_id'}},
                ],
            },
        },
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment_body,
    )
    assert response.status == 200

    # check count
    assert await db.count(taxi_exp_client.app) == 1

    # uplift experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json={
            'experiment_name': EXPERIMENT_NAME,
            'last_updated_at': 1,
            'modification': MODIFICATION,
        },
    )
    assert response.status == 200

    # check
    assert await db.count(taxi_exp_client.app) == 2

    # check transform user_has to in_file
    data = await helpers.get_configs_updates(
        taxi_exp_client, newer_than=1, limit=1,
    )
    config = data['configs'][0]
    predicate = config['match']['predicate']
    assert predicate['type'] == 'true'
    assert predicate['init'] == {}

    assert all(
        (
            (
                sub_clause['type'] == predicates.IN_FILE
                for sub_clause in clause['predicate']['init']['predicates']
            )
            for clause in config['clauses']
        ),
    )

    # check link file and tag to config
    tags = await db.tags_by_config(taxi_exp_client.app, EXPERIMENT_NAME)
    assert tags[0] == TAG
    files_ = await db.files_by_config(taxi_exp_client.app, EXPERIMENT_NAME)
    assert files_[0] == ordinal_file_id
