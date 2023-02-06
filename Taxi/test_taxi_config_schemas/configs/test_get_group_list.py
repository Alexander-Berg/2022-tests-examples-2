import pytest

from test_taxi_config_schemas.configs import common


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_get_group_list(web_app_client, patcher_tvm_ticket_check):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        '/v1/configs/groups/list/', headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == [
        {'name': 'billing'},
        {'name': 'chatterbox'},
        {'name': 'devicenotify'},
    ]
