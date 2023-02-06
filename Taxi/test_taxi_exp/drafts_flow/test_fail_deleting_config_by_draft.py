import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment

CONFIG_NAME = 'existed_config'


@pytest.mark.parametrize(
    'config_body,expected_error_status,expected_error_body',
    [
        pytest.param(
            experiment.generate_config(
                name=CONFIG_NAME + '_NOT', last_modified_at=1,
            ),
            404,
            {
                'message': (
                    'Config existed_config in tariff-editor '
                    'namespace with rev 1 not found'
                ),
                'code': 'CONFIG_NOT_FOUND',
            },
            id='delete_non_existent_config',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_fail_deleting_config(
        taxi_exp_client,
        config_body,
        expected_error_status,
        expected_error_body,
):
    await helpers.init_config(taxi_exp_client, config_body)

    response = await helpers.delete_config_by_draft(
        taxi_exp_client, name=CONFIG_NAME, last_modified_at=1, raw_answer=True,
    )
    assert response.status == expected_error_status
    response_body = await response.json()
    assert response_body == expected_error_body
