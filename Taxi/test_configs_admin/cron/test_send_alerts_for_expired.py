import pytest

from configs_admin.crontasks import send_alerts_for_expire


@pytest.mark.config(
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['BILLING_REPORTS_YT_INPUT_ROW_LIMIT'],
    CONFIG_SCHEMAS_RUNTIME_FEATURES={
        'configs_admin.crontasks.send_alerts_for_expire': 'enabled',
        'default_maintainers': 'test_login',
        'send_alert_for_expire': 'enabled',
    },
)
async def test(sticker_mockserver, cron_context):
    await cron_context.config_schemas_cache.refresh_cache()

    await send_alerts_for_expire.AlertManager(cron_context).run()

    assert sticker_mockserver.calls
