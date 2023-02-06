import typing

import pytest


class Case(typing.NamedTuple):
    data: typing.Dict
    status: int
    code: str


@pytest.mark.parametrize(
    'data,status,code',
    [
        pytest.param(
            *Case(
                data={
                    'experiment_name': 'non_existed_experiment',
                    'last_updated_at': 1,
                },
                status=409,
                code='UPLIFT_DISABLED',
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {
                        'common': {'enable_uplift_experiment': False},
                    },
                },
            ),
        ),
        Case(
            data={
                'experiment_name': 'non_existed_experiment',
                'last_updated_at': 1,
            },
            status=404,
            code='EXPERIMENT_NOT_FOUND',
        ),
        Case(
            data={
                'experiment_name': 'test_experiment',
                'last_updated_at': 1000,
            },
            status=400,
            code='EXPERIMENT_INCORRECT_REVISION',
        ),
        Case(
            data={
                'experiment_name': 'experiment_with_empty_default',
                'last_updated_at': 2,
            },
            status=400,
            code='DEFAULT_VALUE_IS_EMPTY',
        ),
        Case(
            data={
                'experiment_name': 'disabled_experiment',
                'last_updated_at': 3,
            },
            status=409,
            code='EXPERIMENT_IS_DISABLED',
        ),
        Case(
            data={
                'experiment_name': 'closed_experiment',
                'last_updated_at': 4,
            },
            status=409,
            code='EXPERIMENT_ALREADY_CLOSED',
        ),
        Case(
            data={
                'experiment_name': 'experiment_with_bad_default_value',
                'last_updated_at': 6,
            },
            status=400,
            code='BAD_DEFAULT_VALUE',
        ),
        Case(
            data={
                'experiment_name': 'experiment_with_existed_config',
                'last_updated_at': 7,
            },
            status=409,
            code='CONFIG_ALREADY_EXISTS',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['experiments_to_uplifting.sql'])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
async def test_bad_request(data, status, code, taxi_exp_client):
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json=data,
    )
    assert response.status == status, await response.text()
    json = await response.json()
    assert json['code'] == code
