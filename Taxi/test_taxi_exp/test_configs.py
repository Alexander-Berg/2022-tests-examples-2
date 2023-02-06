# pylint: disable=too-many-statements
import copy

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment


FILE_ID = '98c8bfce5f404cf6b479ed34a988efcd'
CONFIG_NAME = 'test_config_name'


def _clear_response(response):
    response.pop('last_modified_at')
    response.pop('closed')
    response.pop('removed')
    response.pop('owners')
    response.pop('watchers')
    response.pop('created')
    response.pop('last_manual_update')
    response.pop('biz_revision')
    response['match'].pop('action_time')
    return response


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_config_removing': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_configs(taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    await db.add_or_update_file(taxi_exp_app, 'file_1.txt', mds_id=FILE_ID)

    await taxi_exp_app.s3_client.upload_content(key=FILE_ID, body=b'')

    data = experiment.generate_config(
        name=CONFIG_NAME, match_predicate={'type': 'true'}, default_value={},
    )
    expected_data = copy.deepcopy(data)
    expected_data.pop('closed', None)

    # success adding config
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME},
        json=data,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME},
    )
    assert response.status == 200
    result = _clear_response(await response.json())

    assert result == expected_data

    # fail adding config without clauses
    del data['clauses'][-1]
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME},
        json=data,
    )
    assert response.status == 409

    # obtaining list
    response = await taxi_exp_client.get(
        '/v1/configs/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['configs']) == 1

    # obtaining updates
    result = await helpers.get_configs_updates(taxi_exp_client, newer_than=0)
    assert len(result['configs']) == 1

    # deleting config
    response = await taxi_exp_client.delete(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME, 'last_modified_at': 1},
        json={},
    )
    assert response.status == 200

    # don't create config with filled apps
    data = experiment.generate(
        name=CONFIG_NAME,
        match_predicate={'type': 'true'},
        default_value={},
        applications=[{'name': 'android', 'version_range': {'from': '1.1.1'}}],
    )
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + 'err1'},
        json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert result['code'] == 'APPLICATIONS_IN_CONFIG'

    # don't create config with non default global predicate
    data = experiment.generate(
        name=CONFIG_NAME,
        match_predicate=experiment.gt_predicate('zone_id'),
        default_value={},
    )
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + 'err2'},
        json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert result['code'] == 'CONFIG_INTEGRITY_ERROR'

    # don't create config with non filled default value
    data = experiment.generate(
        name=CONFIG_NAME,
        match_predicate=experiment.gt_predicate('zone_id'),
        default_value=None,
    )
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + 'err3'},
        json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert result['code'] == 'CONFIG_INTEGRITY_ERROR'

    # don't create config with bad true predicate version
    data = experiment.generate(
        name=CONFIG_NAME,
        match_predicate={'type': 'true', 'init': {'arg_name': 'tttt'}},
        default_value={},
    )
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + 'err4'},
        json=data,
    )
    assert response.status == 400
    result = await response.json()
    assert result['code'] == 'CHECK_PREDICATES_SCHEMA_ERROR'

    # success create config with true predicate version
    data = experiment.generate(
        name=CONFIG_NAME,
        match_predicate={'type': 'true', 'init': {}},
        default_value={},
    )
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + 'err4'},
        json=data,
    )
    assert response.status == 200

    # succes update config
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + 'err4', 'last_modified_at': 4},
        json=data,
    )
    assert response.status == 200
