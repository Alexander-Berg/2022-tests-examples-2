# pylint: disable=too-many-statements
# pylint: disable=invalid-name
import copy

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

FILE_ID = '98c8bfce5f404cf6b479ed34a988efcd'
EXPERIMENT_NAME = 'test_name'
EXPERIMENT_NAME_2 = 'test_name_2'
EXPERIMENT_NAME_WITH_BAD_FILE = 'test_name_with_bad_file'
UNKNOWN_EXPERIMENT_NAME = '_unknown'


@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_experiments(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    await db.add_or_update_file(taxi_exp_app, 'file_1.txt', mds_id=FILE_ID)

    await taxi_exp_app.s3_client.upload_content(key=FILE_ID, body=b'')

    data = experiment.generate(
        EXPERIMENT_NAME,
        match_predicate=(
            experiment.allof_predicate(
                [
                    experiment.inset_predicate([1, 2, 3], set_elem_type='int'),
                    experiment.inset_predicate(
                        ['msk', 'spb'],
                        set_elem_type='string',
                        arg_name='city_id',
                    ),
                    experiment.gt_predicate(
                        '1.1.1',
                        arg_name='app_version',
                        arg_type='application_version',
                    ),
                    experiment.infile_predicate(FILE_ID),
                ],
            )
        ),
        applications=[
            {
                'name': 'android',
                'version_range': {'from': '3.14.0', 'to': '3.20.0'},
            },
        ],
        schema={'type': 'object', 'additionalProperties': False},
    )
    expected_data = copy.deepcopy(data)

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    # check history
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
    )
    body = await response.json()
    body.pop('prestable_flow', None)
    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'revision': 1},
    )
    history_body = (await response.json())['body']

    assert body['created'] == history_body['created']
    assert body == history_body

    # adding experiment 2
    data_without_consumers = experiment.generate(
        EXPERIMENT_NAME_2,
        consumers=[{'name': 'test_consumer'}],
        schema={'type': 'object', 'additionalProperties': False},
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME_2},
        json=data_without_consumers,
    )
    assert response.status == 200, await response.text()

    # adding with bad file
    data_with_bad_file = copy.deepcopy(data)
    data_with_bad_file['match']['predicate']['init']['predicates'][3]['init'][
        'file'
    ] = '67890'
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME_WITH_BAD_FILE},
        json=data_with_bad_file,
    )
    assert response.status == 409

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/experiments/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['experiments']) == 2

    # obtaining list with matching query
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': '_2'},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['experiments']) == 1

    # bad obtaining list with query
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': r'?'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['experiments'] == []

    # limit obtaining list with query
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'limit': 1},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['experiments']) == 1

    # offset obtaining list with query
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'offset': 1},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['experiments']) == 1

    # bad limit obtaining list with query
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'limit': 'a'},
    )
    assert response.status == 400

    # obtaining updates
    result = await helpers.get_updates(taxi_exp_client, newer_than=0)
    assert len(result['experiments']) == 2

    # obtaining updates with limit
    result = await helpers.get_updates(taxi_exp_client, newer_than=0, limit=0)
    assert len(result['experiments']) == 2

    # obtaining updates with limit
    result = await helpers.get_updates(taxi_exp_client, newer_than=0, limit=1)
    assert len(result['experiments']) == 1

    # obtaining updates
    result = await helpers.get_updates(taxi_exp_client, newer_than=1)
    assert len(result['experiments']) == 1

    # updating file
    await taxi_exp_client.put(
        '/v1/files/',
        headers={'YaTaxi-Api-Key': 'secret', 'X-File-Name': 'file_1.txt'},
        data=b'',
        params={'id': FILE_ID, 'version': 1},
    )

    # trying to delete file
    response = await taxi_exp_client.delete(
        '/v1/files/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'id': FILE_ID, 'version': 2},
    )
    assert response.status == 409

    # trying to delete consumer from existing experiment
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer'},
    )
    assert response.status == 409

    # trying to delete application from existing experiment
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/applications/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'android'},
    )
    assert response.status == 409

    # trying to modify with bad last_modified_at
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 0},
        json=data,
    )
    assert response.status == 409

    # trying to modify with bad name
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': UNKNOWN_EXPERIMENT_NAME, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 404

    # trying to modify
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 200

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        params={'name': EXPERIMENT_NAME},
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    last_modified_at = result.pop('last_modified_at')
    result.pop('owners')
    result.pop('watchers')
    result.pop('created')
    result.pop('removed')
    result.pop('last_manual_update')
    result.pop('biz_revision')
    result.pop('prestable_flow')
    assert result == expected_data

    # deleting first experiment
    response = await taxi_exp_client.delete(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_name', 'last_modified_at': last_modified_at},
        json={},
    )
    assert response.status == 200

    # trying to obtain removed experiment
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        params={'name': 'test_name'},
        headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 404

    # obtaining updates
    result = await helpers.get_updates(taxi_exp_client, newer_than=0)
    assert len(result['experiments']) == 2
    removed = [
        experiment
        for experiment in result['experiments']
        if experiment['removed']
    ][0]
    assert removed == {
        'name': 'test_name',
        'removed': True,
        'last_modified_at': 5,
    }

    # deleting second experiment
    response = await taxi_exp_client.delete(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME_2, 'last_modified_at': 2},
        json={},
    )
    assert response.status == 200

    # trying to delete consumer
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/consumers/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'test_consumer'},
    )
    assert response.status == 200

    # trying to delete application
    response = await taxi_exp_client.delete(
        '/v1/experiments/filters/applications/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'android'},
    )
    assert response.status == 200
