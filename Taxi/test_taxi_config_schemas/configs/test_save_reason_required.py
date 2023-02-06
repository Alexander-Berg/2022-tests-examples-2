import pytest

from test_taxi_config_schemas.configs import common


@pytest.mark.parametrize(
    'name,data,status',
    [
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'old_value': 100, 'new_value': 200},
            400,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'old_value': 100, 'new_value': 200, 'reason': 'test_reason'},
            200,
        ),
    ],
)
@pytest.mark.config(ADMIN_EDIT_CONFIG_REASON_REQUIRED=True)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_save_reason_required(
        web_app_client, name, data, status, patcher_tvm_ticket_check,
):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        f'/v1/configs/fallback/{name}/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json=data,
    )
    assert response.status == status
