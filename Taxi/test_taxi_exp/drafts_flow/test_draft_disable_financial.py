import pytest

from test_taxi_exp import helpers

DEPARTMENT = 'taxi'


@pytest.mark.parametrize('is_config', [False, True])
@pytest.mark.pgsql(
    'taxi_exp',
    files=('default.sql', 'financial_config.sql', 'financial_experiment.sql'),
)
async def test_draft_experiment_disable_financial(taxi_exp_client, is_config):
    name = 'financial_' + ('config' if is_config else 'experiment')

    response_body = await helpers.draft_disable_financial(
        taxi_exp_client, name, is_config, DEPARTMENT,
    )

    assert response_body['name'] == name
    assert response_body['financial'] is False


@pytest.mark.parametrize('is_config', [False, True])
@pytest.mark.parametrize(
    'name_prefix, department, code',
    [
        ('nonexistent', 'taxi', 'NOT_FOUND'),
        ('not_financial', 'taxi', 'ALREADY_NOT_FINANCIAL'),
        ('no_department', 'taxi', 'NO_DEPARTMENT'),
        ('financial', 'aaa', 'WRONG_DEPARTMENT'),
        ('common_department', 'common', 'ERROR_COMMON_DEPARTMENT'),
    ],
)
@pytest.mark.pgsql(
    'taxi_exp',
    files=(
        'default.sql',
        'financial_config.sql',
        'financial_experiment.sql',
        'financial_config_no_department.sql',
        'financial_experiment_no_department.sql',
        'financial_config_common_department.sql',
        'financial_experiment_common_department.sql',
        'not_financial_config.sql',
        'not_financial_experiment.sql',
    ),
)
async def test_draft_experiment_disable_financial_wrong_department(
        taxi_exp_client, name_prefix, is_config, department, code,
):
    type_name = 'config' if is_config else 'experiment'
    exp_name = name_prefix + '_' + type_name

    params = {'name': exp_name, 'department': department}
    response = await taxi_exp_client.put(
        f'/v1/{type_name}s/drafts-disable-financial/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json={},
    )

    assert response.status == 400

    response_code = (await response.json())['code']
    if name_prefix == 'nonexistent':
        assert response_code == type_name.upper() + '_' + code
    else:
        assert response_code == code
