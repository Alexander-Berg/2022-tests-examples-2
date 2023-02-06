import pytest

from taxi.util import audit

from test_taxi_config_schemas.configs import common


@pytest.mark.parametrize(
    'name,is_fallback,data,params,status',
    [
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            True,
            {'old_value': 100, 'new_value': 200, 'ticket': 'GOOD_TICKET'},
            None,
            200,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            False,
            {'old_value': 100, 'new_value': 200, 'ticket': 'GOOD_TICKET'},
            None,
            400,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            True,
            {'old_value': 100, 'new_value': 200, 'ticket': 'BAD_TICKET'},
            None,
            400,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            True,
            {'old_value': 100, 'new_value': 200},
            None,
            400,
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT_2',
            True,
            {'old_value': 100, 'new_value': 200},
            None,
            404,
        ),
        (
            'DEVICENOTIFY_USER_TTL',
            False,
            {'old_value': 90, 'new_value': 100},
            None,
            200,
        ),
        (
            'SOME_CONFIG_WITH_DEFINITIONS',
            False,
            {'old_value': {'value': 90}, 'new_value': {'value': 100}},
            None,
            200,
        ),
        (
            'SOME_CONFIG_WITH_DEFINITIONS',
            False,
            {'old_value': {'value': 90}, 'new_value': {'value': 100}},
            {'service_name': 'test'},
            200,
        ),
        (
            'FRIEND_BRANDS',
            False,
            {'old_value': {'items': ['a']}, 'new_value': {'items': ['b']}},
            {'service_name': 'test'},
            400,
        ),
        pytest.param(
            'SOME_CONFIG_WITH_DEFINITIONS',
            False,
            {'old_value': {'value': 90}, 'new_value': {'value': 100}},
            {'service_name': 'test', 'stage_name': 'test'},
            400,
            marks=pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['test']),
        ),
        pytest.param(
            'CONFIG_WITH_BLOCKED_UPDATE_MAIN_VALUE',
            False,
            {'old_value': {'value': 90}, 'new_value': {'value': 90}},
            {},
            200,
        ),
        pytest.param(
            'CONFIG_WITH_BLOCKED_UPDATE_MAIN_VALUE',
            False,
            {'old_value': {'value': 90}, 'new_value': {'value': 100}},
            {},
            400,
        ),
        (
            'SOME_CONFIG_WITH_DEFINITIONS',
            False,
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100, 'release_date': 'a'},
            },
            None,
            400,
        ),
        (
            'SOME_CONFIG_WITH_DEFINITIONS',
            False,
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100, 'release_date': '2012-01-12'},
            },
            None,
            200,
        ),
    ],
)
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures(
    'patch_collect_definitions', 'patch_call_command', 'update_schemas_cache',
)
async def test_save_config(
        patch,
        web_context,
        web_app_client,
        name,
        is_fallback,
        data,
        status,
        params,
        patcher_tvm_ticket_check,
):
    @patch('taxi.util.audit.TicketChecker.check')
    async def _check(ticket, *args, **kwargs):
        if ticket == 'BAD_TICKET':
            raise audit.TicketError

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        f'/v1/configs/{"fallback/" if is_fallback else ""}{name}/',
        headers={'X-Ya-Service-Ticket': 'good'},
        params=params or {},
        json=data,
    )
    assert response.status == status, await response.text()
    if status == 200:
        if params and 'service_name' in params:
            doc = await web_context.mongo.configs_by_service.find_one(
                {'service': params['service_name'], 'config_name': name},
            )
        else:
            doc = await web_context.mongo.config.find_one({'_id': name})
        assert doc['v'] == data['new_value']
