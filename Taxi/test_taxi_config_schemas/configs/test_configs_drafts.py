import pytest

from taxi.util import audit


CONFIGS = [
    {
        'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
        'description': '',
        'group': 'billing',
        'default': 100000000,
        'tags': ['fallback'],
        'validators': ['$integer', {'$gt': 0}],
        'full-description': 'Full description',
        'maintainers': ['dvasiliev89', 'serg-novikov'],
        'wiki': 'https://wiki.yandex-team.ru',
        'turn-off-immediately': True,
    },
    {
        'name': 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'description': '',
        'group': 'chatterbox',
        'default': ['YANDEXTAXI'],
        'tags': [],
        'validators': [{'$sequence_of': ['$string']}],
    },
    {
        'name': 'DEVICENOTIFY_USER_TTL',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'default': 90,
        'tags': ['by-service'],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
    {
        'name': 'DEVICENOTIFY_USER_TTL_WITH_COMMAND',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'team': 'devices',
        'default': 90,
        'tags': [],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
    {
        'name': 'SOME_CONFIG_WITH_DEFINITIONS',
        'description': 'Some config with definitions',
        'group': 'devicenotify',
        'default': {'value': 90},
        'tags': [],
        'schema': {'additionalProperties': {'$ref': 'some_file.yaml#/int'}},
    },
    {
        'name': 'TECHNICAL_CONFIG',
        'description': 'Some config with is_technical field',
        'group': 'tech',
        'default': {'value': 90},
        'tags': [],
        'schema': {'additionalProperties': {'$ref': 'some_file.yaml#/int'}},
    },
    {
        'name': 'TECHNICAL_CONFIG_WITH_COMMAND',
        'description': 'Some config with is_technical field',
        'group': 'devices',
        'default': {'value': 90},
        'tags': [],
        'schema': {'additionalProperties': {'$ref': 'some_file.yaml#/int'}},
    },
    {
        'name': 'CONFIG_WITH_DATE',
        'description': 'Some config with definitions',
        'group': 'devicenotify',
        'default': {'value': 90},
        'tags': ['by-service'],
        'schema': {
            'type': 'object',
            'required': ['value'],
            'properties': {
                'value': {'type': 'integer'},
                'release_date': {'type': 'string', 'format': 'date'},
            },
            'additionalProperties': False,
        },
    },
    {
        'name': 'TECHNICAL_CONFIG_WITH_COMMAND_AND_BLOCK_SELF_OK',
        'description': 'Some config with is_technical field',
        'group': 'devices',
        'default': {'value': 90},
        'tags': ['block-self-ok'],
        'schema': {'additionalProperties': {'$ref': 'some_file.yaml#/int'}},
    },
]


@pytest.mark.parametrize(
    'params,data,expected_check,status',
    [
        pytest.param(
            {'name': 'DEVICENOTIFY_USER_TTL'},
            {'old_value': 90, 'new_value': 100},
            {
                'change_doc_id': 'update_config_value_DEVICENOTIFY_USER_TTL',
                'data': {'old_value': 90, 'new_value': 100, 'self_ok': True},
                'tplatform_namespace': 'taxi',
                'diff': {'new': {'value': 100}, 'current': {'value': 90}},
            },
            200,
            id='success_draft_with_audit_namespace',
        ),
        pytest.param(
            {'name': 'CONFIG_WITH_COMMON_AUDIT_NAMESPACE'},
            {'old_value': True, 'new_value': False},
            {
                'change_doc_id': (
                    'update_config_value_CONFIG_WITH_COMMON_AUDIT_NAMESPACE'
                ),
                'data': {
                    'old_value': True,
                    'new_value': False,
                    'self_ok': True,
                },
                'diff': {'new': {'value': False}, 'current': {'value': True}},
            },
            200,
            id='success_draft_with_common_audit_namespace',
        ),
        pytest.param(
            {'name': 'CONFIG_WITH_COMMON_AUDIT_NAMESPACE'},
            {'old_value': True, 'new_value': False, 'audit_namespace': 'taxi'},
            {
                'change_doc_id': (
                    'update_config_value_CONFIG_WITH_COMMON_AUDIT_NAMESPACE'
                ),
                'data': {
                    'old_value': True,
                    'new_value': False,
                    'self_ok': True,
                    'audit_namespace': 'taxi',
                },
                'diff': {
                    'new': {'value': False, 'audit_namespace': 'taxi'},
                    'current': {'value': True, 'audit_namespace': 'common'},
                },
            },
            200,
            id='success_draft_with_change_common_audit_namespace',
        ),
        pytest.param(
            {'name': 'DEVICENOTIFY_USER_TTL'},
            {'old_value': 90, 'new_value': 100, 'audit_namespace': 'market'},
            {
                'change_doc_id': 'update_config_value_DEVICENOTIFY_USER_TTL',
                'data': {
                    'old_value': 90,
                    'new_value': 100,
                    'self_ok': True,
                    'audit_namespace': 'market',
                },
                'tplatform_namespace': 'taxi',
                'diff': {
                    'new': {'value': 100, 'audit_namespace': 'market'},
                    'current': {'value': 90, 'audit_namespace': 'taxi'},
                },
            },
            200,
            id='success_draft_with_change_audit_namespace',
        ),
        pytest.param(
            {'name': 'TECHNICAL_CONFIG'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100},
                'audit_namespace': 'market',
            },
            {
                'change_doc_id': 'update_config_value_TECHNICAL_CONFIG',
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'self_ok': True,
                    'audit_namespace': 'market',
                    'approvers_group': '_developers_',
                },
                'diff': {
                    'new': {
                        'value': {'value': 100},
                        'audit_namespace': 'market',
                    },
                    'current': {'value': {'value': 90}},
                },
            },
            200,
            id='success_draft_with_add_audit_namespace',
        ),
        pytest.param(
            {'name': 'SOME_CONFIG_WITH_DEFINITIONS'},
            {'old_value': {'value': 90}, 'new_value': {'value': 100}},
            {
                'change_doc_id': (
                    'update_config_value_SOME_CONFIG_WITH_DEFINITIONS'
                ),
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'self_ok': True,
                },
                'tplatform_namespace': 'taxi',
                'diff': {
                    'new': {'value': {'value': 100}},
                    'current': {'value': {'value': 90}},
                },
            },
            200,
            id='success_draft_2',
        ),
        pytest.param(
            {'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'},
            {
                'old_value': 100,
                'new_value': 200,
                'ticket': 'GOOD_TICKET',
                'reason': 'Need update',
            },
            {
                'change_doc_id': (
                    'update_config_value_BILLING_REPORTS_YT_INPUT_ROW_LIMIT'
                ),
                'data': {
                    'old_value': 100,
                    'new_value': 200,
                    'ticket': 'GOOD_TICKET',
                    'self_ok': False,
                    'reason': 'Need update',
                },
                'tplatform_namespace': 'market',
                'tickets': {
                    'create_data': {
                        'summary': (
                            'Config value update: '
                            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'
                        ),
                        'description': (
                            'Change by Need update\n\n'
                            '((https://tariff-editor-unstable.taxi.'
                            'tst.yandex-team.ru/dev/configs/edit/'
                            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT '
                            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT))'
                        ),
                        'ticket_queue': 'BILLING',
                    },
                },
                'diff': {'current': {'value': 100}, 'new': {'value': 200}},
            },
            200,
            id='success_draft_with_ticket',
        ),
        pytest.param(
            {'name': 'DEVICENOTIFY_USER_TTL'},
            {'old_value': 100, 'new_value': 90},
            None,
            409,
            id='fail_if_value_not_actual',
        ),
        pytest.param(
            {'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'},
            {
                'old_value': 100,
                'new_value': 200,
                'ticket': 'GOOD_TICKET',
                'comment': 'test_comment_1',
                'related_ticket': 'GOOD_TICKET',
                'ticket_queue_for_changes': 'BILLING',
            },
            {
                'change_doc_id': (
                    'update_config_value_BILLING_REPORTS_YT_INPUT_ROW_LIMIT'
                ),
                'data': {
                    'old_value': 100,
                    'new_value': 200,
                    'ticket': 'GOOD_TICKET',
                    'comment': 'test_comment_1',
                    'self_ok': False,
                    'related_ticket': 'GOOD_TICKET',
                    'ticket_queue_for_changes': 'BILLING',
                },
                'tplatform_namespace': 'market',
                'tickets': {
                    'create_data': {
                        'summary': (
                            'Config value update: '
                            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'
                        ),
                        'description': (
                            '((https://tariff-editor-unstable.taxi.tst.'
                            'yandex-team.ru/dev/configs/edit/'
                            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT '
                            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT))'
                        ),
                        'ticket_queue': 'BILLING',
                    },
                },
                'diff': {
                    'current': {
                        'value': 100,
                        'comment': 'test_comment',
                        'related_ticket': 'test_ticket',
                        'ticket_queue_for_changes': 'BILLING',
                    },
                    'new': {
                        'value': 200,
                        'comment': 'test_comment_1',
                        'related_ticket': 'GOOD_TICKET',
                        'ticket_queue_for_changes': 'BILLING',
                    },
                },
            },
            200,
            id='success_change_ticket_st_queue_and_comment',
        ),
        pytest.param(
            {'name': 'TECHNICAL_CONFIG'},
            {'old_value': {'value': 90}, 'new_value': {'value': 100}},
            {
                'change_doc_id': 'update_config_value_TECHNICAL_CONFIG',
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'self_ok': True,
                    'approvers_group': '_developers_',
                },
                'diff': {
                    'current': {'value': {'value': 90}},
                    'new': {'value': {'value': 100}},
                },
            },
            200,
            id='success_change_technical_config',
        ),
        pytest.param(
            {'name': 'TECHNICAL_CONFIG'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100},
                'is_technical': False,
            },
            {
                'change_doc_id': 'update_config_value_TECHNICAL_CONFIG',
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'is_technical': False,
                    'self_ok': True,
                    'approvers_group': '_developers_',
                },
                'diff': {
                    'current': {'value': {'value': 90}, 'is_technical': True},
                    'new': {'value': {'value': 100}, 'is_technical': False},
                },
            },
            200,
            id='success_change_technical_config_to_common',
        ),
        pytest.param(
            {'name': 'TECHNICAL_CONFIG'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100},
                'is_technical': True,
            },
            {
                'change_doc_id': 'update_config_value_TECHNICAL_CONFIG',
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'self_ok': True,
                    'is_technical': True,
                    'approvers_group': '_developers_',
                },
                'diff': {
                    'current': {'value': {'value': 90}, 'is_technical': True},
                    'new': {'value': {'value': 100}, 'is_technical': True},
                },
            },
            200,
            id='success_change_technical_config_2',
        ),
        pytest.param(
            {'name': 'USERVER_RPS_CCONTROL_ENABLED', 'service_name': 'test'},
            {'old_value': True, 'new_value': False, 'is_technical': True},
            {
                'change_doc_id': (
                    'update_config_value_USERVER_RPS_CCONTROL_ENABLED_test'
                ),
                'data': {
                    'old_value': True,
                    'new_value': False,
                    'self_ok': True,
                    'service_name': 'test',
                    'is_technical': True,
                    'approvers_group': '_developers_',
                },
                'diff': {
                    'current': {'value': True, 'is_technical': True},
                    'new': {'value': False, 'is_technical': True},
                },
            },
            200,
            id='success_change_service_value_for_technical_config',
        ),
        (
            {'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'},
            {
                'old_value': 100,
                'new_value': 200,
                'ticket': 'GOOD_TICKET',
                'is_technical': True,
            },
            None,
            400,
        ),
        pytest.param(
            {'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT'},
            {'old_value': 100, 'ticket': 'GOOD_TICKET', 'is_technical': True},
            None,
            400,
            id='fail_draft_if_bad_request',
        ),
        pytest.param(
            {
                'name': 'DEVICENOTIFY_USER_TTL',
                'service_name': 'device-devicenotify',
            },
            {'old_value': 1050, 'new_value': 100},
            {
                'change_doc_id': (
                    'update_config_value_DEVICENOTIFY_USER_TTL_'
                    'device-devicenotify'
                ),
                'data': {
                    'old_value': 1050,
                    'new_value': 100,
                    'self_ok': True,
                    'service_name': 'device-devicenotify',
                },
                'tplatform_namespace': 'taxi',
                'diff': {'new': {'value': 100}, 'current': {'value': 1050}},
            },
            200,
            id='success_draft_for_update_service_value',
        ),
        (
            {'name': 'DEVICENOTIFY_USER_TTL'},
            {
                'old_value': 90,
                'new_value': 90,
                'ticket_queue_for_changes': 'DEVICES',
            },
            {
                'change_doc_id': 'update_config_value_DEVICENOTIFY_USER_TTL',
                'data': {
                    'old_value': 90,
                    'new_value': 90,
                    'self_ok': True,
                    'ticket_queue_for_changes': 'DEVICES',
                },
                'tplatform_namespace': 'taxi',
                'diff': {
                    'new': {
                        'value': 90,
                        'ticket_queue_for_changes': 'DEVICES',
                    },
                    'current': {'value': 90},
                },
            },
            200,
        ),
        (
            {
                'name': 'DEVICENOTIFY_USER_TTL',
                'service_name': 'device-devicenotify',
            },
            {'old_value': 1050, 'new_value': 1050, 'is_technical': True},
            None,
            400,
        ),
        pytest.param(
            {
                'name': 'DEVICENOTIFY_USER_TTL',
                'service_name': 'device-devicenotify',
                'stage_name': 'test',
            },
            {'old_value': 1050, 'new_value': 1050},
            None,
            400,
            marks=pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['test']),
            id='fail_update_if_sent_stage_and_service',
        ),
        pytest.param(
            {'name': 'DEVICENOTIFY_USER_TTL'},
            {'old_value': 90, 'new_value': 100, 'team': 'devices'},
            {
                'change_doc_id': 'update_config_value_DEVICENOTIFY_USER_TTL',
                'data': {
                    'old_value': 90,
                    'new_value': 100,
                    'self_ok': False,
                    'team': 'devices',
                },
                'tplatform_namespace': 'taxi',
                'diff': {
                    'new': {'value': 100, 'team': 'devices'},
                    'current': {'value': 90},
                },
            },
            200,
            marks=pytest.mark.config(DEV_TEAMS={'devices': {}}),
        ),
        pytest.param(
            {'name': 'TECHNICAL_CONFIG_WITH_COMMAND'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100},
                'is_technical': True,
                'team': 'hardware_devices',
            },
            {
                'change_doc_id': (
                    'update_config_value_TECHNICAL_CONFIG_WITH_COMMAND'
                ),
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'self_ok': True,
                    'team': 'hardware_devices',
                    'approvers_group': 'hardware_devices_dev',
                    'is_technical': True,
                },
                'diff': {
                    'new': {
                        'value': {'value': 100},
                        'is_technical': True,
                        'team': 'hardware_devices',
                    },
                    'current': {
                        'value': {'value': 90},
                        'is_technical': True,
                        'team': 'hardware_devices',
                    },
                },
            },
            200,
            marks=pytest.mark.config(DEV_TEAMS={'hardware_devices': {}}),
        ),
        pytest.param(
            {'name': 'DEVICENOTIFY_USER_TTL_WITH_COMMAND'},
            {
                'old_value': 90,
                'new_value': 100,
                'team': 'devices',
                'is_technical': False,
            },
            {
                'change_doc_id': (
                    'update_config_value_DEVICENOTIFY_USER_TTL_WITH_COMMAND'
                ),
                'data': {
                    'old_value': 90,
                    'new_value': 100,
                    'self_ok': True,
                    'team': 'devices',
                    'is_technical': False,
                    'approvers_group': 'devices',
                },
                'diff': {
                    'new': {
                        'value': 100,
                        'is_technical': False,
                        'team': 'devices',
                    },
                    'current': {
                        'value': 90,
                        'is_technical': False,
                        'team': 'devices',
                    },
                },
            },
            200,
            marks=pytest.mark.config(DEV_TEAMS={'devices': {}}),
            id='success_update_dev_team',
        ),
        pytest.param(
            {'name': 'CONFIG_WITH_DATE'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 90, 'release_date': 'a'},
            },
            None,
            400,
            id='fail_config_with_date',
        ),
        pytest.param(
            {'name': 'CONFIG_WITH_DATE'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 90, 'release_date': '2012-01-12'},
            },
            {
                'change_doc_id': 'update_config_value_CONFIG_WITH_DATE',
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 90, 'release_date': '2012-01-12'},
                    'self_ok': True,
                },
                'diff': {
                    'new': {
                        'value': {'value': 90, 'release_date': '2012-01-12'},
                    },
                    'current': {'value': {'value': 90}},
                },
            },
            200,
            id='config_with_date',
        ),
        pytest.param(
            {'name': 'TECHNICAL_CONFIG_WITH_COMMAND_AND_BLOCK_SELF_OK'},
            {
                'old_value': {'value': 90},
                'new_value': {'value': 100},
                'is_technical': True,
                'team': 'hardware_devices',
            },
            {
                'change_doc_id': (
                    'update_config_value_'
                    'TECHNICAL_CONFIG_WITH_COMMAND_AND_BLOCK_SELF_OK'
                ),
                'data': {
                    'old_value': {'value': 90},
                    'new_value': {'value': 100},
                    'self_ok': False,
                    'team': 'hardware_devices',
                    'approvers_group': 'hardware_devices_dev',
                    'is_technical': True,
                },
                'diff': {
                    'new': {
                        'value': {'value': 100},
                        'is_technical': True,
                        'team': 'hardware_devices',
                    },
                    'current': {
                        'value': {'value': 90},
                        'is_technical': True,
                        'team': 'hardware_devices',
                    },
                },
            },
            200,
            marks=pytest.mark.config(DEV_TEAMS={'hardware_devices': {}}),
            id='config_with_block_self_ok_by_tag',
        ),
    ],
)
@pytest.mark.config(
    CONFIG_SCHEMAS_RUNTIME_FEATURES={
        'mongo_cache_schemas': 'enabled',
        'update_audit_namespace': 'enabled',
    },
)
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
)
@pytest.mark.custom_patch_configs_by_group(configs=CONFIGS)
@pytest.mark.usefixtures(
    'patch_collect_definitions', 'patch_call_command', 'update_schemas_cache',
)
async def test_save_config(
        patch,
        web_context,
        web_app_client,
        params,
        data,
        expected_check,
        status,
        patcher_tvm_ticket_check,
):
    @patch('taxi.util.audit.TicketChecker.check')
    async def _check(ticket, *args, **kwargs):
        if ticket == 'BAD_TICKET':
            raise audit.TicketError

    patcher_tvm_ticket_check('config-schemas')

    response = await web_app_client.post(
        '/v1/configs/drafts/check/',
        params=params,
        headers={'X-Ya-Service-Ticket': 'good'},
        json=data,
    )
    message = await response.text()
    assert response.status == status, message
    if status != 200:
        return
    body = await response.json()
    assert body == expected_check, message

    response = await web_app_client.put(
        '/v1/configs/drafts/apply/',
        params=params,
        headers={'X-Ya-Service-Ticket': 'good'},
        json=body['data'],
    )
    message = await response.text()
    assert response.status == 200, message
    if 'service_name' not in params:
        doc = await web_context.mongo.config.find_one({'_id': params['name']})
    else:
        doc = await web_context.mongo.configs_by_service.find_one(
            {'config_name': params['name'], 'service': params['service_name']},
        )
    assert doc['v'] == data['new_value']
    assert doc.get('it') == (data.get('is_technical') or False)
    if data.get('audit_namespace'):
        schema_doc = await web_context.mongo.uconfigs_schemas.find_one(
            {'_id': params['name']},
        )
        assert schema_doc.get('audit_namespace') == data['audit_namespace']
