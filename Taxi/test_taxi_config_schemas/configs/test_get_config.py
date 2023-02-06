import pytest

from taxi_config_schemas.repo_manager import errors
from test_taxi_config_schemas.configs import common


@pytest.mark.parametrize(
    'name,params,status,expected',
    [
        (
            'SOME_CONFIG_WITH_DEFINITIONS',
            {},
            200,
            {
                'description': 'Some config with definitions',
                'group': 'devicenotify',
                'is_fallback': False,
                'is_technical': False,
                'name': 'SOME_CONFIG_WITH_DEFINITIONS',
                'schema': {
                    'type': 'object',
                    'required': ['value'],
                    'properties': {
                        'value': {'type': 'integer'},
                        'release_date': {'type': 'string', 'format': 'date'},
                    },
                    'additionalProperties': False,
                },
                'tags': ['by-service'],
                'ticket_required': False,
                'value': {'value': 90},
                'tplatform_namespace': 'taxi',
            },
        ),
        (
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
                'ticket_required': True,
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'turn_off_immediately': True,
                'value': 100,
                'comment': 'test_comment',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'ticket_queue_for_changes': 'BILLING',
                'tplatform_namespace': 'market',
            },
        ),
        ('BILLING_REPORTS_YT_INPUT_ROW_LIMIT_2', {}, 404, {}),
        (
            'DEVICENOTIFY_USER_TTL',
            {},
            200,
            {
                'group': 'devicenotify',
                'name': 'DEVICENOTIFY_USER_TTL',
                'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
                'description': 'TTL пользователя при его неактивности',
                'tags': ['by-service'],
                'ticket_required': False,
                'is_fallback': False,
                'is_technical': False,
                'value': 90,
                'services': ['device-devicenotify'],
                'tplatform_namespace': 'taxi',
            },
        ),
        (
            'FRIEND_BRANDS',
            {},
            200,
            {
                'ticket_required': False,
                'is_fallback': False,
                'is_technical': False,
                'name': 'FRIEND_BRANDS',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {'type': 'string', 'minLength': 1},
                    },
                },
                'description': 'Бренды с общими данными пользователей',
                'value': [['yataxi', 'yango']],
                'group': 'chatterbox',
                'tags': [],
                'team': 'promotions',
                'tplatform_namespace': 'grocery',
            },
        ),
        (
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
                'ticket_required': True,
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'turn_off_immediately': True,
                'value': 93,
                'comment': 'test_comment',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'ticket_queue_for_changes': 'BILLING',
                'tplatform_namespace': 'market',
            },
        ),
        (
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'service_name': 'billing-marketplace-api'},
            200,
            {
                'group': 'billing',
                'service_name': 'billing-marketplace-api',
                'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
                'validators': ['$integer', {'$gt': 0}],
                'description': '',
                'full_description': 'Full description',
                'wiki': 'https://wiki.yandex-team.ru',
                'tags': ['fallback'],
                'ticket_required': True,
                'is_fallback': True,
                'is_technical': False,
                'maintainers': ['dvasiliev89', 'serg-novikov'],
                'turn_off_immediately': True,
                'value': 107,
                'comment': 'test_comment',
                'related_ticket': 'test_ticket',
                'services': ['billing-bank-orders', 'billing-marketplace-api'],
                'ticket_queue_for_changes': 'BILLING',
                'tplatform_namespace': 'market',
            },
        ),
        pytest.param(
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
            {'service_name': 'billing-marketplace-api', 'stage_name': 'aaaaa'},
            400,
            {},
            marks=pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['aaaaa']),
        ),
    ],
)
@pytest.mark.parametrize(
    'is_good_patch',
    [
        pytest.param(
            False,
            id='mongo_cache',
            marks=(
                pytest.mark.config(
                    CONFIG_SCHEMAS_RUNTIME_FEATURES={
                        'mongo_cache_schemas': 'enabled',
                    },
                ),
                pytest.mark.usefixtures('patch_bad_call_command'),
            ),
        ),
        pytest.param(
            True,
            id='git_cache',
            marks=(
                pytest.mark.config(
                    CONFIG_SCHEMAS_RUNTIME_FEATURES={
                        'mongo_cache_schemas': 'disabled',
                    },
                ),
                pytest.mark.usefixtures('patch_call_command'),
            ),
        ),
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
)
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
async def test_get_config(
        web_app_client,
        patcher_tvm_ticket_check,
        patch,
        name,
        params,
        status,
        expected,
        is_good_patch,
):
    if is_good_patch:

        @patch('taxi_config_schemas.repo_manager.util.GitHelper._call_command')
        async def _call_command(*args, **kwargs):
            return b'', b''

    else:

        @patch('taxi_config_schemas.repo_manager.util.GitHelper._call_command')
        async def _call_command(*args, **kwargs):
            raise errors.GitError('Unknown git error')

    await web_app_client.app['context'].config_schemas_cache.refresh_cache()
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        f'/v1/configs/{name}/',
        headers={'X-Ya-Service-Ticket': 'good'},
        params=params,
    )
    assert response.status == status
    if status == 200:
        result = await response.json()
        if is_good_patch:
            expected.pop('tplatform_namespace', None)
        assert result == expected
