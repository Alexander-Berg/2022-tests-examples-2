import pytest

from test_taxi_config_schemas.configs import common


ADDITIONAL_CONFIGS: list = [
    {
        'name': 'DEVICENOTIFY_USER_TTL_v2',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'default': 90,
        'tags': [],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
    {
        'name': 'DEVICENOTIFY_USER_TTL_v3',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'default': 90,
        'tags': [],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
    {
        'name': 'TECHNICAL_CONFIG',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'default': 90,
        'tags': [],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
]

TEST_DATA = (
    [
        pytest.param(
            params,
            expected_names,
            expected_redefined,
            expected_status,
            expected_error_message,
            marks=pytest.mark.custom_patch_configs_by_group(
                configs=common.CONFIGS,
            ),
        )
        for (
                params,
                expected_names,
                expected_redefined,
                expected_status,
                expected_error_message,
        ) in (
            (
                {},
                [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',  # billing
                    'CONFIG_WITH_BLOCKED_UPDATE_MAIN_VALUE',
                    'DEVICENOTIFY_USER_TTL',  # devicenotify
                    'FRIEND_BRANDS',  # chatterbox
                    'SOME_CONFIG_WITH_DEFINITIONS',  # devicenotify
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',  # chatterbox
                ],
                [True, False, True, False, False, False],
                200,
                None,
            ),
            (
                {'name': 'TRACK'},
                ['STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES'],
                [False],
                200,
                None,
            ),
            (
                {'name': 'll'},
                [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
                ],
                [True, False],
                200,
                None,
            ),
            (
                {'name': 'll', 'group': 'billing'},
                ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
                [True],
                200,
                None,
            ),
            (
                {'description': 'TTL'},
                ['DEVICENOTIFY_USER_TTL'],
                [True],
                200,
                None,
            ),
            (
                {'group': 'chatterbox'},
                ['FRIEND_BRANDS', 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES'],
                [False, False],
                200,
                None,
            ),
            (
                {'limit': 1},
                ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
                [True],
                200,
                None,
            ),
            (
                {'last_viewed_config': 'FRIEND_BRANDS'},
                [
                    'SOME_CONFIG_WITH_DEFINITIONS',
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
                ],
                [False, False],
                200,
                None,
            ),
            (
                {'last_viewed_config': 'DEVICENOTIFY_USER_TTL', 'limit': 1},
                ['FRIEND_BRANDS'],
                [False],
                200,
                None,
            ),
            (
                {'service_name': 'billing-marketplace-api'},
                ['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
                [True],
                200,
                None,
            ),
            ({'service_name': 'unknown-service'}, [], [], 200, None),
            (
                {'with_overrides': 'True'},
                [
                    'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',  # billing
                    'DEVICENOTIFY_USER_TTL',  # devicenotify
                ],
                [True, True],
                200,
                None,
            ),
            (
                {'with_overrides': 'False'},
                [
                    'CONFIG_WITH_BLOCKED_UPDATE_MAIN_VALUE',
                    'FRIEND_BRANDS',  # chatterbox
                    'SOME_CONFIG_WITH_DEFINITIONS',  # devicenotify
                    'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',  # chatterbox
                ],
                [False, False, False, False],
                200,
                None,
            ),
            (
                {'with_overrides': 'KKKK'},
                None,
                None,
                400,
                {
                    'message': 'Some parameters are invalid',
                    'code': 'REQUEST_VALIDATION_ERROR',
                    'details': {
                        'reason': (
                            'Invalid value for with_overrides: '
                            '\'KKKK\' is not instance of bool'
                        ),
                    },
                },
            ),
        )
    ]
    + [
        pytest.param(
            params,
            expected_names,
            expected_redefined,
            expected_status,
            expected_error_message,
            marks=pytest.mark.custom_patch_configs_by_group(
                configs=common.CONFIGS + ADDITIONAL_CONFIGS,
            ),
        )
        for (
                params,
                expected_names,
                expected_redefined,
                expected_status,
                expected_error_message,
        ) in (
            (
                {'service_name': 'device-devicenotify'},
                [
                    'DEVICENOTIFY_USER_TTL',
                    'DEVICENOTIFY_USER_TTL_v2',
                    'DEVICENOTIFY_USER_TTL_v3',
                ],
                [True, True, True],
                200,
                None,
            ),
            (
                {
                    'service_name': 'device-devicenotify',
                    'with_overrides': 'False',
                },
                [],
                [],
                200,
                None,
            ),
            (
                {
                    'service_name': 'device-devicenotify',
                    'with_overrides': 'True',
                },
                [
                    'DEVICENOTIFY_USER_TTL',
                    'DEVICENOTIFY_USER_TTL_v2',
                    'DEVICENOTIFY_USER_TTL_v3',
                ],
                [True, True, True],
                200,
                None,
            ),
            (
                {'is_technical': 'True'},
                ['TECHNICAL_CONFIG'],
                [False],
                200,
                None,
            ),
        )
    ]
)


@pytest.mark.parametrize(
    (
        'params,'
        'expected_names,expected_redefined,'
        'expected_status,expected_error_message'
    ),
    TEST_DATA,
)
@pytest.mark.config(
    TVM_ENABLED=True,
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_get_config_list(
        web_app_client,
        patcher_tvm_ticket_check,
        params,
        expected_names,
        expected_redefined,
        expected_status,
        expected_error_message,
):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        '/v1/configs/list/',
        params=params,
        headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == expected_status, await response.text()
    result = await response.json()
    if expected_status == 400:
        assert result == expected_error_message
        return
    assert [item['name'] for item in result['items']] == expected_names
    assert [
        item['has_overrides'] for item in result['items']
    ] == expected_redefined
    if not params:
        ticket_required_configs = {
            item['name'] for item in result['items'] if item['ticket_required']
        }
        assert ticket_required_configs == {
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
        }
