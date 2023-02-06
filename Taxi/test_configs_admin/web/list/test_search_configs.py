import pytest


@pytest.mark.parametrize(
    'params,expected_names',
    [
        pytest.param({}, [], id='success_search_empty_in_empty_out'),
        pytest.param(
            {
                'exact_names': [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                    'FRIEND_BRANDS',
                ],
            },
            ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT', 'FRIEND_BRANDS'],
            id='success_search_with_exact_names',
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
async def test_search_configs(
        web_app_client,
        web_context,
        params,
        patcher_tvm_ticket_check,
        expected_names,
):
    await web_context.config_schemas_cache.init_cache()
    patcher_tvm_ticket_check('configs-admin')
    response = await web_app_client.post(
        '/v1/configs/search/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json=params,
    )
    assert response.status == 200
    result = await response.json()
    names = [item['name'] for item in result['items']]
    assert names == expected_names
