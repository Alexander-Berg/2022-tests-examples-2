from typing import Dict
from typing import NamedTuple
from typing import Optional

import pytest

from configs_admin import static


class Case(NamedTuple):
    name: str
    data: Dict
    params: Optional[Dict] = None
    status: int = 200
    expected: Optional[Dict] = None
    change_static_config: Optional[static.StaticConfig] = None

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101


@pytest.mark.parametrize(
    Case.get_args(),
    [
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data={'old_value': 90, 'new_value': 100},
            ),
            id='success update value',
        ),
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data={'version': 73, 'new_value': 100},
            ),
            id='v2_version_success_update_value',
        ),
        pytest.param(
            *Case(
                name='NO_SCHEMA_CONFIG',
                data={'old_value': {'value': 90}, 'new_value': 100},
                change_static_config=static.StaticConfig.from_other_config(
                    static.STATIC_CONFIG,
                    {'flags': {'enable_check_by_schema': False}},
                ),
            ),
            id='success update value for config without schema',
        ),
        pytest.param(
            *Case(
                name='UNKNOWN_CONFIG',
                data={'old_value': {'value': 90}, 'new_value': {'value': 100}},
                change_static_config=static.StaticConfig.from_other_config(
                    static.STATIC_CONFIG,
                    {'flags': {'enable_check_by_schema': False}},
                ),
            ),
            id='create config if config not found',
        ),
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL',
                data={'old_value': 190, 'new_value': 100},
                status=409,
                expected={
                    'code': 'CURRENT_VALUE_IS_NOT_ACTUAL',
                    'message': (
                        'Value "190" for config "DEVICENOTIFY_USER_TTL" '
                        'is not actual any more'
                    ),
                },
            ),
            id='fail_if_config_value_not_actual',
        ),
        pytest.param(
            *Case(
                name='SOME_CONFIG_BY_SERVICE',
                data={
                    'old_value': {'value': 1110},
                    'new_value': {'value': 100},
                },
                params={'service_name': 'test'},
                status=409,
                expected={
                    'code': 'CURRENT_VALUE_IS_NOT_ACTUAL',
                    'message': (
                        'Value "{\'value\': 1110}" for config '
                        '"SOME_CONFIG_BY_SERVICE" is not actual any more'
                    ),
                },
            ),
            id='fail if config service value not actual',
        ),
        pytest.param(
            *Case(
                name='SOME_CONFIG_BY_SERVICE',
                data={
                    'old_value': {'value': 1111},
                    'new_value': {'value': 100},
                },
                params={'service_name': 'test'},
            ),
            id='success update service value allowed by by-service tag',
        ),
        pytest.param(
            *Case(
                name='SOME_CONFIG_BY_SERVICE_DISALLOWED',
                data={
                    'old_value': {'value': 1111},
                    'new_value': {'value': 100},
                },
                params={'service_name': 'test'},
                status=400,
                expected={
                    'code': 'DISALLOW_UPDATE_VALUE',
                    'message': (
                        'Change of service value for config '
                        '`SOME_CONFIG_BY_SERVICE_DISALLOWED` is blocked '
                        'because there is no tag `by-service` for this config'
                    ),
                },
            ),
            id='fail update service value without by-service tag',
        ),
        pytest.param(
            *Case(
                name='BLOCKED_CONFIG',
                data={
                    'old_value': {'value': 1111},
                    'new_value': {'value': 100},
                },
                status=409,
                expected={
                    'code': 'BLOCK_SET_VALUE_BY_SCHEMA_UPDATE',
                    'message': (
                        'Config `BLOCKED_CONFIG` can`t be updated because '
                        'schema update is in progress, update lock expires '
                        'at 2119-03-06T11:00:00'
                    ),
                },
            ),
            id='fail update blocked config',
        ),
        pytest.param(
            *Case(
                name='BLOCKED_CONFIG',
                data={
                    'old_value': {'value': 1111},
                    'new_value': {'value': 100},
                },
                params={'service_name': 'test'},
                status=409,
                expected={
                    'code': 'BLOCK_SET_VALUE_BY_SCHEMA_UPDATE',
                    'message': (
                        'Config `BLOCKED_CONFIG` can`t be updated because '
                        'schema update is in progress, update lock expires '
                        'at 2119-03-06T11:00:00'
                    ),
                },
            ),
            id='fail update blocked config service value',
        ),
        pytest.param(
            *Case(
                name='DEVICENOTIFY_USER_TTL_WITH_FAR_DEF',
                data={'old_value': 90, 'new_value': 100},
            ),
            marks=pytest.mark.filldb(uconfigs_meta='success_far_update'),
            id='success_update_value_of_config_with_far_link',
        ),
    ],
)
async def test_save_config(
        web_context,
        web_app_client,
        patcher_tvm_ticket_check,
        static_config,
        name,
        data,
        status,
        params,
        expected,
        change_static_config,
):
    patcher_tvm_ticket_check('config-schemas')
    if change_static_config:
        static_config(change_static_config)
    await web_context.config_schemas_cache.init_cache()

    data['name'] = name
    if params:
        data.update(params)
    response = await web_app_client.post(
        '/v2/configs/', headers={'X-Ya-Service-Ticket': 'good'}, json=data,
    )
    assert response.status == status, await response.text()
    if status == 200:
        if params and 'service_name' in params:
            doc = await web_context.mongo.configs_by_service.find_one(
                {'service': params['service_name'], 'config_name': name},
            )
        else:
            doc = await web_context.mongo.config.find_one({'_id': name})
        assert doc
        assert doc['v'] == data['new_value']
    else:
        result = await response.json()
        assert result == expected
