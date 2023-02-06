from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from taxi.util import audit


class Case(NamedTuple):
    name: str
    data: Dict
    use_fallback: bool = False
    params: Optional[Dict] = None
    status: int = 200
    error_response: Optional[Dict] = None


@pytest.mark.parametrize(
    'name,data,use_fallback,params,status,error_response',
    [
        # проверяем сохранение значений конфига, у которого включены сервисы
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data=data,
                use_fallback=False,
                status=status,
                params=params,
                error_response=error_response,
            ),
            id='{}_check_service_{}'.format(
                'fail' if status != 200 else 'success', message_id,
            ),
        )
        for message_id, data, params, status, error_response in [
            (
                # успешное сохранение основного значения
                'common_value',
                {'old_value': 92, 'new_value': 100},
                None,
                200,
                None,
            ),
            (
                # успешное обновление сервисного значения
                'service_value_update',
                {'old_value': 1112, 'new_value': 100},
                {'service_name': 'device-devicenotify'},
                200,
                None,
            ),
            (
                # успешное создание сервисного значения
                'service_value_creation',
                {'old_value': 92, 'new_value': 1001},
                {'service_name': 'digital'},
                200,
                None,
            ),
            (
                # успешное создание основного значения для стейджа
                'stage_creation_for_common',
                {'old_value': 92, 'new_value': 100},
                {'stage_name': 'register'},
                200,
                None,
            ),
            (
                # успешное обновление основного значения для стейджа
                'update_stage_for_common',
                {'old_value': 567, 'new_value': 100},
                {'stage_name': 'filled_register'},
                200,
                None,
            ),
            (
                # падение при попытке сохранить сервисное значение для стейджа
                'stage_for_service',
                {'old_value': 92, 'new_value': 100},
                {'stage_name': 'register', 'service_name': 'digital'},
                400,
                {
                    'code': 'INCORRECT_ARGUMENTS_COMBINATION',
                    'message': 'Do not use stage and service at the same time',
                },
            ),
        ]
    ]
    + [
        # проверяем сохранение значений обычного конфига
        pytest.param(
            *Case(
                name='FRIEND_BRANDS',
                data=data,
                use_fallback=False,
                status=status,
                params=params,
                error_response=error_response,
            ),
            id='{}_check_regular_config_{}'.format(
                'fail' if status != 200 else 'success', message_id,
            ),
        )
        for message_id, data, params, status, error_response in [
            (
                # успешное сохранение основного значения
                'common_value',
                {'old_value': [], 'new_value': ['yataxi']},
                None,
                200,
                None,
            ),
            (
                # успешное создание основного значения для стейджа
                'stage',
                {'old_value': [], 'new_value': ['yango']},
                {'stage_name': 'register'},
                200,
                None,
            ),
            (
                # падение при сохранении основного значения
                # для незарегистрированного стейджа
                'non_register_stage',
                {'old_value': [], 'new_value': ['yyy']},
                {'stage_name': 'no_register'},
                400,
                {
                    'code': 'UNKNOWN_STAGE_NAME',
                    'message': 'unknown stage_name no_register',
                },
            ),
            (
                # падение при сохранении сервисного значения
                'disallow_service',
                {'old_value': [], 'new_value': ['bbbb']},
                {'service_name': 'digital'},
                400,
                {
                    'code': 'PER_SERVICE_VALUE_FORBIDDEN',
                    'message': (
                        'For update value by service need found '
                        '`by-service` tag in schema'
                    ),
                },
            ),
        ]
    ]
    + [
        # проверяем падение при ошибке валидации
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data=data,
                use_fallback=False,
                status=400,
                params=params,
                error_response=error_response,
            ),
            id='check_fails_by_validation_{}'.format(message_id),
        )
        for message_id, data, params, error_response in [
            (
                # падение при ошибке валидации основного значения
                'common_value',
                {'old_value': 92, 'new_value': {'1': '2'}},
                None,
                {
                    'code': 'VALIDATION_FAILED',
                    'message': (
                        'Config `DEVICENOTIFY_USER_TTL` not updated. '
                        'Reason: errors occurred during validation of '
                        'config DEVICENOTIFY_USER_TTL: {\'1\': '
                        '\'2\'} is not of type \'integer\'\n'
                        '\n'
                        'Failed validating \'type\' in schema:\n'
                        '    {\'type\': \'integer\'}\n'
                        '\n'
                        'On instance:\n'
                        '    {\'1\': \'2\'}'
                    ),
                },
            ),
            (
                # падение при ошибке валидации сервисного значения
                'service_value',
                {'old_value': 1112, 'new_value': {'1': '2'}},
                {'service_name': 'device-devicenotify'},
                {
                    'code': 'VALIDATION_FAILED',
                    'message': (
                        'Config `DEVICENOTIFY_USER_TTL` not updated. '
                        'Reason: errors occurred during validation of '
                        'config DEVICENOTIFY_USER_TTL: {\'1\': \'2\'} '
                        'is not of type \'integer\'\n\n'
                        'Failed validating \'type\' in schema:\n'
                        '    {\'type\': \'integer\'}\n'
                        '\n'
                        'On instance:\n'
                        '    {\'1\': \'2\'}'
                    ),
                },
            ),
            (
                # падение при ошибке валидации основного значения стейджа
                'stage_value',
                {'old_value': 567, 'new_value': {'1': '2'}},
                {'stage_name': 'filled_register'},
                {
                    'code': 'VALIDATION_FAILED',
                    'message': (
                        'Config `DEVICENOTIFY_USER_TTL` not updated. '
                        'Reason: errors occurred during validation of '
                        'config DEVICENOTIFY_USER_TTL: {\'1\': \'2\'} '
                        'is not of type \'integer\'\n\n'
                        'Failed validating \'type\' in schema:\n    '
                        '{\'type\': \'integer\'}\n\n'
                        'On instance:\n    {\'1\': \'2\'}'
                    ),
                },
            ),
        ]
    ]
    + [
        # проверяем падение при неактуальном значении
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data=data,
                use_fallback=False,
                status=409,
                params=params,
                error_response={
                    'code': 'CURRENT_VALUE_IS_NOT_ACTUAL',
                    'message': (
                        'Value "10" for config "DEVICENOTIFY_USER_TTL" '
                        'is not actual any more'
                    ),
                },
            ),
            id='check_fails_by_non_actual_{}'.format(message_id),
        )
        for message_id, data, params in [
            ('common_value', {'old_value': 10, 'new_value': 100}, None),
            (
                'service_value',
                {'old_value': 10, 'new_value': 100},
                {'service_name': 'device-devicenotify'},
            ),
            (
                'stage_value',
                {'old_value': 10, 'new_value': 100},
                {'stage_name': 'filled_register'},
            ),
        ]
    ]
    + [
        # проверяем обновление при указании версии значения вместо старого
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data=data,
                use_fallback=False,
                status=200,
                params=params,
                error_response=None,
            ),
            id='success_update_with_version_{}'.format(message_id),
        )
        for message_id, data, params in [
            ('common_value', {'version': 10, 'new_value': 100}, None),
            (
                'service_value',
                {'version': 11, 'new_value': 100},
                {'service_name': 'device-devicenotify'},
            ),
            (
                'stage_value',
                {'version': 12, 'new_value': 100},
                {'stage_name': 'filled_register'},
            ),
        ]
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
    CONFIG_SCHEMAS_STAGE_NAMES=['register', 'filled_register'],
)
async def test_save_config(
        patch,
        web_context,
        web_app_client,
        patcher_tvm_ticket_check,
        # params
        name,
        use_fallback,
        data,
        status,
        params,
        error_response,
):
    await web_context.config_schemas_cache.init_cache()

    @patch('taxi.util.audit.TicketChecker.check')
    async def _check(ticket, *args, **kwargs):
        if ticket == 'BAD_TICKET':
            raise audit.TicketError

    patcher_tvm_ticket_check('configs-admin')
    response = await web_app_client.post(
        f'/v1/configs/{"fallback/" if use_fallback else ""}{name}/',
        headers={'X-Ya-Service-Ticket': 'good'},
        params=params or {},
        json=data,
    )

    assert response.status == status, await response.text()
    if status != 200:
        assert await response.json() == error_response
        return

    if params:
        if 'service_name' in params:
            doc = await web_context.mongo.configs_by_service.find_one(
                {'service': params['service_name'], 'config_name': name},
            )
        elif 'stage_name' in params:
            doc = await web_context.mongo.uconfigs.find_one(
                {'stage_name': params['stage_name'], 'name': name},
            )
    else:
        doc = await web_context.mongo.config.find_one({'_id': name})
    assert doc['v'] == data['new_value']
