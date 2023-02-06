import pytest


@pytest.mark.parametrize(
    'name,params,status,expected',
    [
        pytest.param(
            'SOME_CONFIG',
            {},
            200,
            {
                'description': 'Some config with definitions',
                'group': 'devicenotify',
                'is_fallback': False,
                'is_technical': False,
                'name': 'SOME_CONFIG',
                'default': None,
                'schema': {
                    'type': 'object',
                    'required': ['value'],
                    'properties': {
                        'value': {'type': 'integer'},
                        'release_date': {'type': 'string', 'format': 'date'},
                    },
                    'additionalProperties': False,
                },
                'schema_definitions': {},
                'tags': ['by-service'],
                'value': {'value': 90},
                'maintainers': [],
                'services': [],
            },
            id='success get config',
        ),
        pytest.param(
            'UNKNOWN_CONFIG',
            {},
            404,
            {
                'code': 'CONFIG_NOT_FOUND',
                'message': 'Config `UNKNOWN_CONFIG` not found',
            },
            id='config not found',
        ),
        pytest.param(
            'DEVICENOTIFY_USER_TTL',
            {},
            200,
            {
                'group': 'devicenotify',
                'name': 'DEVICENOTIFY_USER_TTL',
                'schema': {'type': 'integer'},
                'schema_definitions': {},
                'description': 'TTL пользователя при его неактивности',
                'tags': ['by-service'],
                'is_fallback': False,
                'is_technical': False,
                'value': 91,
                'default': 10,
                'maintainers': [],
                'services': ['device-devicenotify'],
            },
            id='success_return_config_with_changed_common_value',
        ),
        pytest.param(
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {},
            200,
            {
                'group': 'billing',
                'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                'validators': ['$integer', {'$gt': 0}],
                'description': '',
                'full_description': 'Full description',
                'wiki': 'https://wiki.yandex-team.ru',
                'tags': ['fallback'],
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'turn_off_immediately': True,
                'value': 100,
                'default': 100000000,
                'comment': 'test_comment',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'ticket_queue_for_changes': 'BILLING',
            },
            id='success_return_fallback_config',
        ),
        pytest.param(
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'service_name': 'billing-bank-orders'},
            200,
            {
                'group': 'billing',
                'service_name': 'billing-bank-orders',
                'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                'validators': ['$integer', {'$gt': 0}],
                'description': '',
                'full_description': 'Full description',
                'wiki': 'https://wiki.yandex-team.ru',
                'tags': ['fallback'],
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'turn_off_immediately': True,
                'value': 93,
                'default': 100000000,
                'comment': 'test_comment',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'ticket_queue_for_changes': 'BILLING',
            },
            id='success_return_service_value',
        ),
        pytest.param(
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'service_name': 'non-existed-service'},
            200,
            {
                'group': 'billing',
                'service_name': 'non-existed-service',
                'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                'validators': ['$integer', {'$gt': 0}],
                'description': '',
                'full_description': 'Full description',
                'wiki': 'https://wiki.yandex-team.ru',
                'tags': ['fallback'],
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'turn_off_immediately': True,
                'value': 100,
                'default': 100000000,
                'comment': 'test_comment',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'ticket_queue_for_changes': 'BILLING',
            },
            id='success_get_common_value_if_service_value_not_found_in_db',
        ),
        pytest.param(
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'service_name': 'billing-marketplace-api', 'stage_name': 'aaaaa'},
            400,
            {
                'code': 'INCORRECT_ARGUMENTS_COMBINATION',
                'message': 'Do not use stage and service at the same time',
            },
            marks=pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['aaaaa']),
            id='fail_params_is_not_correct',
        ),
        pytest.param(
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'stage_name': 'aaaaa'},
            200,
            {
                'comment': 'test_comment',
                'default': 100000000,
                'description': '',
                'full_description': 'Full description',
                'group': 'billing',
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'tags': ['fallback'],
                'ticket_queue_for_changes': 'BILLING',
                'turn_off_immediately': True,
                'validators': ['$integer', {'$gt': 0}],
                'stage_name': 'aaaaa',
                'value': 567,
                'wiki': 'https://wiki.yandex-team.ru',
            },
            marks=pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['aaaaa']),
            id='success_get_stage_value',
        ),
    ]
    + [
        # проверка работы с версиями
        pytest.param(
            *case, id=f'v2_success_return_config_with_changed_{message}',
        )
        for case, message in [
            (
                (
                    'CONFIG_WITH_VERSION',
                    {},
                    200,
                    {
                        'group': 'group_with_version',
                        'name': 'CONFIG_WITH_VERSION',
                        'schema': {'type': 'integer'},
                        'schema_definitions': {},
                        'description': 'Конфиг, у которого есть версия',
                        'tags': ['by-service'],
                        'is_fallback': False,
                        'is_technical': False,
                        'value': 91,
                        'default': 10,
                        'maintainers': [],
                        'services': ['versions'],
                        'value_version': 2,
                    },
                ),
                'common_value',
            ),
            (
                (
                    'CONFIG_WITH_VERSION',
                    {'service_name': 'versions'},
                    200,
                    {
                        'group': 'group_with_version',
                        'name': 'CONFIG_WITH_VERSION',
                        'schema': {'type': 'integer'},
                        'schema_definitions': {},
                        'description': 'Конфиг, у которого есть версия',
                        'tags': ['by-service'],
                        'is_fallback': False,
                        'is_technical': False,
                        'value': 191,
                        'default': 10,
                        'maintainers': [],
                        'services': ['versions'],
                        'service_name': 'versions',
                        'value_version': 12,
                    },
                ),
                'service_value',
            ),
            (
                (
                    'CONFIG_WITH_VERSION',
                    {'stage_name': 'versions'},
                    200,
                    {
                        'group': 'group_with_version',
                        'name': 'CONFIG_WITH_VERSION',
                        'schema': {'type': 'integer'},
                        'schema_definitions': {},
                        'description': 'Конфиг, у которого есть версия',
                        'tags': ['by-service'],
                        'is_fallback': False,
                        'is_technical': False,
                        'value': 11,
                        'default': 10,
                        'maintainers': [],
                        'services': ['versions'],
                        'value_version': 121,
                        'stage_name': 'versions',
                    },
                ),
                'stage_value',
            ),
        ]
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
    CONFIG_SCHEMAS_STAGE_NAMES=['versions'],
)
async def test_get_config(
        web_app_client,
        patcher_tvm_ticket_check,
        name,
        params,
        status,
        expected,
):
    patcher_tvm_ticket_check('config-schemas')
    params['name'] = name
    response = await web_app_client.get(
        '/v2/configs/', headers={'X-Ya-Service-Ticket': 'good'}, params=params,
    )
    assert response.status == status, await response.text()
    result = await response.json()
    assert status == response.status
    assert result == expected