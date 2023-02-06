import pytest

from test_taxi_config_schemas.configs import common


@pytest.mark.parametrize(
    'params,expected_names',
    [
        ({}, []),
        (
            {
                'exact_names': [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                    'FRIEND_BRANDS',
                ],
            },
            ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT', 'FRIEND_BRANDS'],
        ),
        (
            {
                'exact_names': [
                    'FRIEND_BRANDS',
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                ],
            },
            ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT', 'FRIEND_BRANDS'],
        ),
        (
            {
                'order_by': 'exact_names_asc',
                'exact_names': [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                    'FRIEND_BRANDS',
                ],
            },
            ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT', 'FRIEND_BRANDS'],
        ),
        (
            {
                'order_by': 'exact_names_desc',
                'exact_names': [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                    'FRIEND_BRANDS',
                ],
            },
            ['FRIEND_BRANDS', 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
        ),
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_search_configs(
        web_app_client, params, patcher_tvm_ticket_check, expected_names,
):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        '/v1/configs/search/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json=params,
    )
    assert response.status == 200
    result = await response.json()
    names = [item['name'] for item in result['items']]
    assert names == expected_names
