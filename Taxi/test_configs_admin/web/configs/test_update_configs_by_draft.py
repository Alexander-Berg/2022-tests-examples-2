from typing import Dict
from typing import NamedTuple

import pytest

from taxi.util import audit

from test_configs_admin import helpers


class Case(NamedTuple):
    params: Dict
    requestbody: Dict
    expected_check: Dict
    status: int
    audit_namespace_is_updated: bool = False


DEFAULT_DATA = {'old_value': 49, 'new_value': 100}


@pytest.mark.parametrize(
    'params,requestbody,expected_check,status,audit_namespace_is_updated',
    [
        # успешно сохраняем все значения
        pytest.param(*case, id='success_{}'.format(message_id))
        for message_id, case in [
            (
                'create_boolean_common_value',
                Case(
                    params={
                        'name': 'SUPPORT_METRICS_SIMULTANEOUS_CALCULATION',
                    },
                    requestbody={'old_value': True, 'new_value': False},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_'
                            'SUPPORT_METRICS_SIMULTANEOUS_CALCULATION'
                        ),
                        'data': {
                            'old_value': True,
                            'new_value': False,
                            'self_ok': True,
                        },
                        'diff': {
                            'new': {'value': False},
                            'current': {'value': True},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'create_common_value',  # старое значение берется из дефолта
                Case(
                    params={'name': 'NON_FILLED_SIMPLE_CONFIG'},
                    requestbody={'old_value': 10, 'new_value': 100},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_NON_FILLED_SIMPLE_CONFIG'
                        ),
                        'data': {
                            'old_value': 10,
                            'new_value': 100,
                            'self_ok': True,
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 10},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'update_common_value_by_version',
                Case(
                    params={'name': 'SIMPLE_CONFIG_WITH_SERVICES'},
                    requestbody={'version': 67, 'new_value': 100},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_CONFIG_WITH_SERVICES'
                        ),
                        'data': {
                            'version': 67,
                            'new_value': 100,
                            'self_ok': True,
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 49},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'update_common_value',  # старое значение берется из общего
                Case(
                    params={'name': 'SIMPLE_CONFIG_WITH_SERVICES'},
                    requestbody=DEFAULT_DATA,
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_CONFIG_WITH_SERVICES'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 100,
                            'self_ok': True,
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 49},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'create_service_value',
                Case(
                    params={
                        'name': 'SIMPLE_CONFIG_WITH_SERVICES',
                        'service_name': 'billing-api',
                    },
                    requestbody=DEFAULT_DATA,
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_'
                            'SIMPLE_CONFIG_WITH_SERVICES_billing-api'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 100,
                            'self_ok': True,
                            'service_name': 'billing-api',
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 49},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'update_service_value',
                Case(
                    params={
                        'name': 'SIMPLE_CONFIG_WITH_SERVICES',
                        'service_name': 'device-devicenotify',
                    },
                    requestbody={'old_value': 113, 'new_value': 100},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_'
                            'SIMPLE_CONFIG_WITH_SERVICES_device-devicenotify'
                        ),
                        'data': {
                            'old_value': 113,
                            'new_value': 100,
                            'self_ok': True,
                            'service_name': 'device-devicenotify',
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 113},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'create_stage_value',
                Case(
                    params={
                        'name': 'SIMPLE_CONFIG_WITH_SERVICES',
                        'stage_name': 'register',
                    },
                    requestbody=DEFAULT_DATA,
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_'
                            'SIMPLE_CONFIG_WITH_SERVICES_register'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 100,
                            'self_ok': True,
                            'stage_name': 'register',
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 49},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'update_stage_value',
                Case(
                    params={
                        'name': 'SIMPLE_CONFIG_WITH_SERVICES',
                        'stage_name': 'filled_register',
                    },
                    requestbody={'old_value': 23, 'new_value': 100},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_'
                            'SIMPLE_CONFIG_WITH_SERVICES_filled_register'
                        ),
                        'data': {
                            'old_value': 23,
                            'new_value': 100,
                            'self_ok': True,
                            'stage_name': 'filled_register',
                        },
                        'diff': {
                            'new': {'value': 100},
                            'current': {'value': 23},
                        },
                    },
                    status=200,
                ),
            ),
        ]
    ]
    + [
        # Успешно обновляем все поля
        pytest.param(*case, id='success_update_field_{}'.format(message_id))
        for message_id, case in [
            (
                'add_ticket_queue_for_changes',
                Case(
                    params={'name': 'NON_FILLED_SIMPLE_CONFIG'},
                    requestbody={
                        'old_value': 10,
                        'new_value': 10,
                        'ticket_queue_for_changes': 'DEVICES',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_NON_FILLED_SIMPLE_CONFIG'
                        ),
                        'data': {
                            'old_value': 10,
                            'new_value': 10,
                            'self_ok': True,
                            'ticket_queue_for_changes': 'DEVICES',
                        },
                        'diff': {
                            'new': {
                                'value': 10,
                                'ticket_queue_for_changes': 'DEVICES',
                            },
                            'current': {'value': 10},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'remove_all_fields',
                Case(
                    params={'name': 'CONFIG_WITH_FIELDS'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                        'audit_namespace': 'taxi',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_CONFIG_WITH_FIELDS'
                        ),
                        'tplatform_namespace': 'taxi',
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': False,
                            'approvers_group': 'DEVICES_dev',
                            'is_technical': False,
                            'audit_namespace': 'taxi',
                        },
                        'tickets': {
                            'create_data': {
                                'description': (
                                    '((https://tariff-editor-unstable.taxi.'
                                    'tst.yandex-team.ru/dev/configs/edit/'
                                    'CONFIG_WITH_FIELDS CONFIG_WITH_FIELDS))'
                                ),
                                'summary': (
                                    'Config value update: CONFIG_WITH_FIELDS'
                                ),
                                'ticket_queue': 'TAXIADMIN',
                            },
                        },
                        'diff': {
                            'new': {'value': 49, 'is_technical': False},
                            'current': {
                                'value': 49,
                                'related_ticket': 'TAXIADMIN-123',
                                'ticket_queue_for_changes': 'TAXIADMIN',
                                'comment': 'test_comment',
                                'is_technical': True,
                                'team': 'DEVICES',
                            },
                        },
                    },
                    status=200,
                ),
            ),
            (
                'add_all_fields',
                Case(
                    params={'name': 'NON_FILLED_SIMPLE_CONFIG'},
                    requestbody={
                        'old_value': 10,
                        'new_value': 10,
                        'related_ticket': 'TAXIADMIN-123',
                        'ticket_queue_for_changes': 'TAXIADMIN',
                        'comment': 'test_comment',
                        'is_technical': True,
                        'team': 'devices',
                        'audit_namespace': 'taxi',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_NON_FILLED_SIMPLE_CONFIG'
                        ),
                        'data': {
                            'old_value': 10,
                            'new_value': 10,
                            'self_ok': False,
                            'related_ticket': 'TAXIADMIN-123',
                            'ticket_queue_for_changes': 'TAXIADMIN',
                            'comment': 'test_comment',
                            'is_technical': True,
                            'team': 'devices',
                            'audit_namespace': 'taxi',
                        },
                        'diff': {
                            'new': {
                                'value': 10,
                                'related_ticket': 'TAXIADMIN-123',
                                'ticket_queue_for_changes': 'TAXIADMIN',
                                'comment': 'test_comment',
                                'is_technical': True,
                                'team': 'devices',
                                'audit_namespace': 'taxi',
                            },
                            'current': {'value': 10, 'is_technical': False},
                        },
                    },
                    status=200,
                    audit_namespace_is_updated=True,
                ),
            ),
        ]
    ]
    + [
        # падения:
        # если меняем поля (кроме значения)
        # для сервисного или стейджевого значения
        # если меняем главное значение у конфига
        # без права менять главное значение
        pytest.param(*case, id='fail_update_{}'.format(message_id))
        for message_id, case in [
            (
                'field_comment_to_service',
                Case(
                    params={
                        'name': 'DEVICENOTIFY_USER_TTL',
                        'service_name': 'test',
                    },
                    requestbody={'old_value': 92, 'new_value': 92},
                    expected_check={
                        'code': 'UPDATE_RESTRICTED_VALUE',
                        'message': (
                            'fail change comment by service_name '
                            'from test_comment to None'
                        ),
                    },
                    status=400,
                ),
            ),
            (
                'field_ticket_queue_to_stage',
                Case(
                    params={
                        'name': 'DEVICENOTIFY_USER_TTL',
                        'stage_name': 'register',
                    },
                    requestbody={
                        'old_value': 92,
                        'new_value': 92,
                        'ticket_queue_for_changes': 'DEVICES',
                    },
                    expected_check={
                        'code': 'UPDATE_RESTRICTED_VALUE',
                        'message': (
                            'fail change comment by stage_name '
                            'from test_comment to None'
                        ),
                    },
                    status=400,
                ),
            ),
            (
                'main_value_for_config_with_block_it',
                Case(
                    params={'name': 'NO_EDIT_MAIN_VALUE'},
                    requestbody={'old_value': 10, 'new_value': 92},
                    expected_check={
                        'code': 'DISALLOW_UPDATE_VALUE',
                        'message': (
                            'Change of main value of '
                            'this config is blocked by tag'
                        ),
                    },
                    status=400,
                ),
            ),
        ]
    ]
    + [
        # проверяем неймспейсы
        pytest.param(*case, id='check_namespace_{}'.format(message_id))
        for message_id, case in [
            (
                'update_common_value_with_common_audit_namespace',
                Case(
                    params={'name': 'CONFIG_WITH_COMMON_NAMESPACE'},
                    requestbody={'old_value': False, 'new_value': True},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_CONFIG_WITH_COMMON_NAMESPACE'
                        ),
                        'data': {
                            'old_value': False,
                            'new_value': True,
                            'self_ok': True,
                        },
                        'diff': {
                            'new': {'value': True},
                            'current': {'value': False},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'update_common_value_with_any_audit_namespace',
                Case(
                    params={'name': 'CONFIG_WITH_ANY_NAMESPACE'},
                    requestbody={'old_value': False, 'new_value': True},
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_CONFIG_WITH_ANY_NAMESPACE'
                        ),
                        'data': {
                            'old_value': False,
                            'new_value': True,
                            'self_ok': True,
                        },
                        'tplatform_namespace': 'taxi',
                        'diff': {
                            'new': {'value': True},
                            'current': {'value': False},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'update_common_audit_namespace',
                Case(
                    params={'name': 'CONFIG_WITH_COMMON_NAMESPACE'},
                    requestbody={
                        'old_value': False,
                        'new_value': True,
                        'audit_namespace': 'taxi',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_CONFIG_WITH_COMMON_NAMESPACE'
                        ),
                        'data': {
                            'old_value': False,
                            'new_value': True,
                            'self_ok': True,
                            'audit_namespace': 'taxi',
                        },
                        'diff': {
                            'new': {'value': True, 'audit_namespace': 'taxi'},
                            'current': {
                                'value': False,
                                'audit_namespace': 'common',
                            },
                        },
                    },
                    audit_namespace_is_updated=True,
                    status=200,
                ),
            ),
            (
                'update_any_audit_namespace',
                Case(
                    params={'name': 'CONFIG_WITH_ANY_NAMESPACE'},
                    requestbody={
                        'old_value': False,
                        'new_value': True,
                        'audit_namespace': 'common',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_CONFIG_WITH_ANY_NAMESPACE'
                        ),
                        'data': {
                            'old_value': False,
                            'new_value': True,
                            'self_ok': True,
                            'audit_namespace': 'common',
                        },
                        'tplatform_namespace': 'taxi',
                        'diff': {
                            'new': {
                                'value': True,
                                'audit_namespace': 'common',
                            },
                            'current': {
                                'value': False,
                                'audit_namespace': 'taxi',
                            },
                        },
                    },
                    audit_namespace_is_updated=True,
                    status=200,
                ),
            ),
        ]
    ]
    + [
        # проверяем технические конфиги - установка/снятие
        # побочка - approvers_group
        pytest.param(*case, id='check_is_technical_{}'.format(message_id))
        for message_id, case in [
            (
                'set_true',
                Case(
                    params={'name': 'SIMPLE_CONFIG_WITH_SERVICES'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': True,
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_CONFIG_WITH_SERVICES'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': True,
                            'is_technical': True,
                        },
                        'diff': {
                            'new': {'value': 49, 'is_technical': True},
                            'current': {'value': 49, 'is_technical': False},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'set_false',
                Case(
                    params={'name': 'SIMPLE_CONFIG_WITH_SERVICES'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_CONFIG_WITH_SERVICES'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': True,
                            'is_technical': False,
                        },
                        'diff': {
                            'new': {'value': 49},
                            'current': {'value': 49},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'change_true_to_false_and_view_default_approvers_group',
                Case(
                    params={'name': 'SIMPLE_TECH_CONFIG'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_TECH_CONFIG'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': True,
                            'is_technical': False,
                            'approvers_group': '_developers_',
                        },
                        'diff': {
                            'new': {'value': 49, 'is_technical': False},
                            'current': {'value': 49, 'is_technical': True},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'change_true_to_false_and_view_custom_approvers_group',
                Case(
                    params={'name': 'SIMPLE_TECH_CONFIG_WITH_TEAM'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                        'team': 'devices',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_TECH_CONFIG_WITH_TEAM'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': True,
                            'is_technical': False,
                            'approvers_group': 'devices_dev',
                            'team': 'devices',
                        },
                        'diff': {
                            'new': {'value': 49, 'is_technical': False},
                            'current': {'value': 49, 'is_technical': True},
                        },
                    },
                    status=200,
                ),
            ),
        ]
    ]
    + [
        # проверяем самоок и команду
        # блокировка самоока по тегу - самоока нет никогда
        # установка - снятие команды
        # побочка - self_ok, audit_groups
        pytest.param(*case, id='check_team_and_self_ok_{}'.format(message_id))
        for message_id, case in [
            (
                'allow_self_ok',
                Case(
                    params={'name': 'SIMPLE_TECH_CONFIG_WITH_TEAM'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                        'team': 'devices',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_TECH_CONFIG_WITH_TEAM'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': True,
                            'is_technical': False,
                            'approvers_group': 'devices_dev',
                            'team': 'devices',
                        },
                        'diff': {
                            'new': {'value': 49, 'is_technical': False},
                            'current': {'value': 49, 'is_technical': True},
                        },
                    },
                    status=200,
                ),
            ),
            (
                'fail_change_to_unregistered_team',
                Case(
                    params={'name': 'SIMPLE_TECH_CONFIG_WITH_TEAM'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                        'team': 'another_devices',
                    },
                    expected_check={
                        'code': 'TEAM_IS_UNREGISTERED',
                        'message': (
                            'Team `another_devices` for config '
                            '`SIMPLE_TECH_CONFIG_WITH_TEAM` '
                            'is not found in DEV_TEAMS config'
                        ),
                    },
                    status=400,
                ),
            ),
            (
                'change_team_and_disallow_self_ok',
                Case(
                    params={'name': 'SIMPLE_TECH_CONFIG_WITH_TEAM'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                        'team': 'billing',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_SIMPLE_TECH_CONFIG_WITH_TEAM'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': False,
                            'is_technical': False,
                            'approvers_group': 'devices_dev',
                            'team': 'billing',
                        },
                        'diff': {
                            'new': {
                                'value': 49,
                                'is_technical': False,
                                'team': 'billing',
                            },
                            'current': {
                                'value': 49,
                                'is_technical': True,
                                'team': 'devices',
                            },
                        },
                    },
                    status=200,
                ),
            ),
            (
                'disallow_self_ok_by_tag',
                Case(
                    params={'name': 'SIMPLE_CONFIG_WITH_BLOCK_SELF_OK'},
                    requestbody={
                        'old_value': 49,
                        'new_value': 49,
                        'is_technical': False,
                        'team': 'billing',
                    },
                    expected_check={
                        'change_doc_id': (
                            'update_config_value_'
                            'SIMPLE_CONFIG_WITH_BLOCK_SELF_OK'
                        ),
                        'data': {
                            'old_value': 49,
                            'new_value': 49,
                            'self_ok': False,
                            'is_technical': False,
                            'approvers_group': 'devices_dev',
                            'team': 'billing',
                        },
                        'diff': {
                            'new': {
                                'value': 49,
                                'is_technical': False,
                                'team': 'billing',
                            },
                            'current': {
                                'value': 49,
                                'is_technical': True,
                                'team': 'devices',
                            },
                        },
                    },
                    status=200,
                ),
            ),
        ]
    ]
    + [
        # падение при не совпадении значения и схемы
        pytest.param(*case, id='fail_if_{}'.format(message_id))
        for message_id, case in [
            (
                'direct_schema',
                Case(
                    params={'name': 'DEVICENOTIFY_USER_TTL'},
                    requestbody={
                        'old_value': 92,
                        'new_value': '111',
                        'is_technical': False,
                        'team': 'devices',
                    },
                    expected_check={
                        'code': 'VALIDATION_FAILED',
                        'message': (
                            'Config `DEVICENOTIFY_USER_TTL` not updated. '
                            'Reason: errors occurred during validation of '
                            'config DEVICENOTIFY_USER_TTL: \'111\' '
                            'is not of type \'integer\'\n'
                            '\n'
                            'Failed validating \'type\' in schema:\n'
                            '    {\'type\': \'integer\'}\n'
                            '\n'
                            'On instance:\n'
                            '    \'111\''
                        ),
                    },
                    status=400,
                ),
            ),
            (
                'schema_with_definition',
                Case(
                    params={
                        'name': 'DEVICENOTIFY_USER_TTL_WITH_DIRECT_SCHEMA',
                    },
                    requestbody={
                        'old_value': 90,
                        'new_value': '111',
                        'is_technical': False,
                        'team': 'devices',
                    },
                    expected_check={
                        'code': 'VALIDATION_FAILED',
                        'message': (
                            'Config `DEVICENOTIFY_USER_TTL_WITH_DIRECT_SCHEMA`'
                            ' not updated. '
                            'Reason: errors occurred during validation of '
                            'config DEVICENOTIFY_USER_TTL_WITH_DIRECT_SCHEMA:'
                            ' \'111\' is not of type \'integer\'\n'
                            '\n'
                            'Failed validating \'type\' in schema:\n'
                            '    {\'type\': \'integer\'}\n'
                            '\n'
                            'On instance:\n'
                            '    \'111\''
                        ),
                    },
                    status=400,
                ),
            ),
        ]
    ],
)
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
    CONFIG_SCHEMAS_STAGE_NAMES=['register', 'filled_register'],
    DEV_TEAMS={'devices': {}, 'billing': {}},
)
async def test_case(
        patch,
        web_context,
        web_app_client,
        params,
        requestbody,
        expected_check,
        status,
        audit_namespace_is_updated,
        patcher_tvm_ticket_check,
):
    # setup
    patcher_tvm_ticket_check('configs-admin')

    @patch('taxi.util.audit.TicketChecker.check')
    async def _check(ticket, *args, **kwargs):
        if ticket == 'BAD_TICKET':
            raise audit.TicketError

    await web_context.config_schemas_cache.init_cache()
    config_name = params['name']
    audit_namespace_before = await helpers.get_schema_field(
        web_context, config_name, 'audit_namespace',
    )

    # change
    response = await web_app_client.post(
        '/v1/configs/drafts/check/',
        params=params,
        headers={'X-Ya-Service-Ticket': 'good'},
        json=requestbody,
    )
    assert response.status == status, await response.text()

    # semi check
    assert await response.json() == expected_check
    # stop if expected fail
    if status != 200:
        return

    apply_data = (await response.json())['data']
    response = await web_app_client.put(
        '/v1/configs/drafts/apply/',
        params=params,
        headers={'X-Ya-Service-Ticket': 'good'},
        json=apply_data,
    )
    assert response.status == 200, await response.text()

    # check value and fields in db
    if 'service_name' in params:
        doc = await web_context.mongo.configs_by_service.find_one(
            {'service': params['service_name'], 'config_name': config_name},
        )
    elif 'stage_name' in params:
        doc = await web_context.mongo.uconfigs.find_one(
            {'stage_name': params['stage_name'], 'name': config_name},
        )
    else:
        doc = await web_context.mongo.config.find_one({'_id': config_name})
    assert doc['v'] == requestbody['new_value']
    assert doc.get('it') == (requestbody.get('is_technical') or False)

    for rfield, lfield in (
            ('cq', 'custom_st_queue'),
            ('tm', 'team'),
            ('t', 'related_ticket'),
            ('c', 'comment'),
    ):
        if lfield in requestbody:
            assert doc.get(rfield) == requestbody[lfield], lfield

    # check value in api
    for get_func, kwargs in (
            (helpers.get_value_v1, {'name': config_name}),
            (helpers.get_value_v2, {}),
    ):
        doc = await get_func(web_app_client, params=params, **kwargs)
        assert doc.get('value') == requestbody['new_value']

    # check audit_namespace in db
    audit_namespace_after = await helpers.get_schema_field(
        web_context, config_name, 'audit_namespace',
    )
    if audit_namespace_is_updated:
        assert audit_namespace_before != audit_namespace_after
    else:
        assert audit_namespace_before == audit_namespace_after
