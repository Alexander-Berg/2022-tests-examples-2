import pytest


from billing_fin_payouts.monrun_checks import table_stats


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_FETCH_STATS_ENABLED=True,
    BILLING_FIN_PAYOUTS_TABLE_SETTINGS={
        'interface.revenues': {
            'primary_key_field': 'id',
            'created_at_field': 'created_at_utc',
        },
    },
)
@pytest.mark.pgsql('billing_fin_payouts')
async def test_table_stats(cron_context):
    stats = await table_stats.load_stats(cron_context)
    assert len(stats) == 1
    out = await table_stats.run_check(cron_context)
    assert out.startswith('0;')
