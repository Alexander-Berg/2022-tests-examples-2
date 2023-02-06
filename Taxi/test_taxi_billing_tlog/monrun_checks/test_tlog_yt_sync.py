import pytest


from taxi_billing_tlog.monrun_checks import tlog_yt_sync


@pytest.mark.config(
    BILLING_TLOG_PG_ACTIVE_CONSUMERS=['upload_expenses_to_hahn'],
    BILLING_TLOG_JOURNAL_TABLES={
        'topic_payments': {
            'active_consumers': ['upload_payments_to_hahn'],
            'is_housekeeping_enabled': True,
        },
    },
)
@pytest.mark.pgsql(
    'billing_tlog@0',
    files=('journal.sql', 'topic_payments.sql', 'consumer_offset.sql'),
)
async def test_tlog_yt_sync(cron_context):
    rows = await tlog_yt_sync.load_stats(cron_context)
    assert [dict(row) for row in rows] == [
        {'consumer_id': 'upload_payments_to_hahn', 'lag': 300},
        {'consumer_id': 'upload_expenses_to_hahn', 'lag': 180},
    ]
