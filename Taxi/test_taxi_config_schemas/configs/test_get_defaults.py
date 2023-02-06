import pytest

from test_taxi_config_schemas.configs import common


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
@pytest.mark.parametrize(
    'headers, response_code',
    [
        ({'X-Ya-Service-Ticket': 'bad_key'}, 200),
        ({}, 200),
        ({'X-Ya-Service-Ticket': 'good'}, 200),
    ],
)
async def test_get_defaults(
        web_app_client, headers, response_code, patcher_tvm_ticket_check,
):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        '/v1/configs/defaults/', headers=headers,
    )
    assert response.status == response_code
    if response_code == 401:
        return
    result = await response.json()
    defaults = {config['name']: config['default'] for config in common.CONFIGS}
    expected_response = {
        'commit': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        'defaults': defaults,
    }
    assert result == expected_response
