import pytest

from taxi_config_schemas.crontasks import send_alerts_for_expire

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
        'name': 'SOME_CONFIG_WITH_EXPIRED',
        'description': 'Some config with definitions',
        'group': 'devicenotify',
        'maintainers': ['dvasiliev89', 'serg-novikov'],
        'default': {'value': 90},
        'tags': ['temporary'],
        'schema': {
            'type': 'object',
            'additionalProperties': False,
            'required': ['value'],
            'properties': {'value': {'type': 'number'}},
        },
        'end-of-life': '2000-01-01',
    },
]


@pytest.mark.config(
    TVM_ENABLED=True,
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
    CONFIG_SCHEMAS_RUNTIME_FEATURES={
        'taxi_config_schemas.crontasks.send_alerts_for_expire': 'enabled',
        'default_maintainers': 'test_login',
        'send_alert_for_expire': 'enabled',
    },
)
@pytest.mark.custom_patch_configs_by_group(configs=CONFIGS)
@pytest.mark.usefixtures('patch_call_command')
async def test(sticker_mockserver, cron_context):
    await cron_context.config_schemas_cache.refresh_cache()

    await send_alerts_for_expire.AlertManager(cron_context).run()

    assert sticker_mockserver.calls
