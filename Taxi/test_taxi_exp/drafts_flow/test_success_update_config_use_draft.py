import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

CONFIG_NAME = 'existed_config'


@pytest.mark.parametrize(
    'config_body,expected_is_technical',
    [
        pytest.param(
            experiment.generate_config(
                name=CONFIG_NAME, department='market', last_modified_at=1,
            ),
            False,
            id='create_by_default',
        ),
        pytest.param(
            experiment.generate_config(
                name=CONFIG_NAME,
                is_technical=True,
                department='market',
                last_modified_at=1,
            ),
            True,
            id='is_technical_true',
        ),
        pytest.param(
            experiment.generate_config(
                name=CONFIG_NAME,
                is_technical=False,
                department='market',
                last_modified_at=1,
            ),
            False,
            id='is_technical_false',
        ),
        pytest.param(
            experiment.generate_config(
                name=CONFIG_NAME,
                department='market',
                last_modified_at=1,
                financial=None,
            ),
            False,
            id='null_financial',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'prestable_flow': True}},
        'settings': {
            'common': {
                'departments': {'market': {'map_to_namespace': 'market'}},
            },
        },
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'existed_config.sql'))
async def test_update_config(
        taxi_exp_client, config_body, expected_is_technical,
):
    response = await helpers.update_config_by_draft(
        taxi_exp_client, config_body, raw_answer=True,
    )
    assert response.status == 200

    body = await response.json()
    assert body['change_doc_id'] == f'update_config_{CONFIG_NAME}'
    assert body['data']['status_wait_prestable'] == 'no_warning'
    assert body['tplatform_namespace'] == 'market'
    assert 'diff' in body
    assert body['data']['is_technical']
    assert body['data']['config']['financial'] is True

    response_body = await helpers.update_config_by_draft(
        taxi_exp_client, config_body,
    )
    assert response_body['is_technical'] == expected_is_technical
    assert response_body['financial'] is True
