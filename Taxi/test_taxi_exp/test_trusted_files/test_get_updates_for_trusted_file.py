import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files


TAG_NAME = 'test_tag'


async def _upload_trusted(client, tag, body):
    response = await files.post_trusted_file(client, tag, body)
    assert response.status == 200
    return (await response.json())['id']


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
                },
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_get_updates_for_trusted_files(taxi_exp_client):
    # add tagged file
    file_id = await _upload_trusted(taxi_exp_client, TAG_NAME, b'trusted')

    # add experiment with tag
    data = experiment.generate(
        name='experiment_with_by_command',
        match_predicate={'type': 'user_has', 'init': {'tag': TAG_NAME}},
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'experiment_with_by_command'},
        json=data,
    )
    assert response.status == 200
    result = await db.tags_by_experiment(
        taxi_exp_client.app, 'experiment_with_by_command',
    )
    assert set(result) == {TAG_NAME}

    # get transformed experiment
    result = await helpers.get_updates(taxi_exp_client, newer_than=0)

    # check transformation
    expected_predicate = {
        'type': 'in_file',
        'init': {
            'set_elem_type': 'string',
            'file': file_id,
            'arg_name': TAG_NAME,
        },
    }
    predicate = result['experiments'][0]['match']['predicate']
    assert predicate == expected_predicate

    # update tagged file
    file_id = await _upload_trusted(taxi_exp_client, TAG_NAME, b'trusted2')
    result = await db.tags_by_experiment(
        taxi_exp_client.app, 'experiment_with_by_command',
    )
    assert set(result) == {TAG_NAME}

    # get transformed experiment newer_than must be updated
    result = await helpers.get_updates(taxi_exp_client, newer_than=1)
    predicate = result['experiments'][0]['match']['predicate']
    expected_predicate['init']['file'] = file_id
    assert predicate == expected_predicate

    # add new tagged file
    another_file_id = await _upload_trusted(
        taxi_exp_client, 'another_test_tag', b'trusted',
    )
    result = await db.tags_by_experiment(
        taxi_exp_client.app, 'experiment_with_by_command',
    )
    assert set(result) == {TAG_NAME}

    # trying to modify experiment
    last_modified_at = await helpers.get_last_modified_at(
        taxi_exp_client, 'experiment_with_by_command',
    )
    data = experiment.generate(
        name='experiment_with_by_command',
        match_predicate={
            'type': 'all_of',
            'init': {
                'predicates': [
                    {'type': 'user_has', 'init': {'tag': TAG_NAME}},
                    {'type': 'user_has', 'init': {'tag': 'another_test_tag'}},
                ],
            },
        },
    )
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={
            'name': 'experiment_with_by_command',
            'last_modified_at': last_modified_at,
        },
        json=data,
    )
    assert response.status == 200

    # check that experiemnt has two tags
    result = await db.tags_by_experiment(
        taxi_exp_client.app, 'experiment_with_by_command',
    )
    assert set(result) == {TAG_NAME, 'another_test_tag'}

    # get transformed experiment
    result = await helpers.get_updates(
        taxi_exp_client, newer_than=last_modified_at,
    )

    # check transformation
    expected_predicate = {
        'type': 'all_of',
        'init': {
            'predicates': [
                {
                    'type': 'in_file',
                    'init': {
                        'set_elem_type': 'string',
                        'file': file_id,
                        'arg_name': TAG_NAME,
                    },
                },
                {
                    'type': 'in_file',
                    'init': {
                        'set_elem_type': 'string',
                        'file': another_file_id,
                        'arg_name': 'another_test_tag',
                    },
                },
            ],
        },
    }
    predicate = result['experiments'][0]['match']['predicate']
    assert predicate == expected_predicate
