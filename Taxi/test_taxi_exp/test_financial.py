import copy

import pytest

from test_taxi_exp.helpers import experiment


CONFIG_NAME = 'test_config_name'


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'enable_config_removing': True,
                'financial_check_disabled': False,
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_financial(taxi_exp_client):
    data = experiment.generate_config(
        name=CONFIG_NAME,
        match_predicate={'type': 'true'},
        default_value={},
        financial=True,
    )

    # success adding config, financial is explicitly true
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
    result = await response.json()
    assert result['financial'] is True

    # success adding config, financial is true by default
    null_financial_data = copy.deepcopy(data)
    null_financial_data.pop('financial')
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + '1'},
        json=null_financial_data,
    )
    assert response.status == 200, await response.text()

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME + '1'},
    )
    assert response.status == 200
    result = await response.json()
    assert result['financial'] is True

    # fail adding config with false financial
    fail_data = copy.deepcopy(data)
    fail_data['financial'] = False
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME},
        json=fail_data,
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'FINANCIAL_FALSE_IN_NEW_EXPERIMENT'
    assert body['message'] == 'New experiments are always financial'

    # failure update config with financial to false
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME, 'last_modified_at': 1},
        json=fail_data,
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'ILLEGALLY_SETTING_FINANCIAL_TO_FALSE'
    assert body['message'] == (
        'Illegally setting financial to false. '
        'Financial impact property cannot be set to false via standard update'
    )

    # do not change financial if there is no financial field in update
    null_financial_data = copy.deepcopy(data)
    null_financial_data.pop('financial')
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME, 'last_modified_at': 1},
        json=null_financial_data,
    )
    assert response.status == 200

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME},
    )
    assert response.status == 200
    result = await response.json()
    assert result['financial'] is True

    # success update config with true financial
    response = await taxi_exp_client.put(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': CONFIG_NAME, 'last_modified_at': 3},
        json=data,
    )
    assert response.status == 200
    assert result['financial'] is True
