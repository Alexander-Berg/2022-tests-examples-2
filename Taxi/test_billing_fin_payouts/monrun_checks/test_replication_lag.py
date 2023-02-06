import datetime

import pytest


from billing_fin_payouts.monrun_checks import replication_lag


@pytest.mark.config(
    BILLING_FIN_PAYOUTS_FETCH_STATS_ENABLED=True,
    BILLING_FIN_PAYOUTS_TABLE_SETTINGS={
        'payouts.payout_batches': {
            'primary_key_field': 'batch_id',
            'created_at_field': 'created_at_utc',
        },
    },
    BILLING_FIN_PAYOUTS_CLEANUP_SETTINGS={
        '__default__': {
            'enabled': False,
            'ttl_days': 1,
            'consumers': [],
            'bulk_size': 1000,
            'iterations': 3,
        },
        'payouts.payout_batches': {
            'enabled': True,
            'ttl_days': 1,
            'offset_days': 2,
            'consumers': [
                'upload_payout_ready_batches_to_arnold',
                'upload_payout_ready_batches_to_hahn',
                'upload_export_batches_to_arnold',
                'billing_fin_payouts.crontasks.upload_export_batches_to_hahn',
            ],
            'bulk_size': 1,
            'iterations': 3,
        },
    },
)
@pytest.mark.pgsql(
    'billing_fin_payouts',
    files=['payout_batches.sql', 'consumer_cursors.sql'],
)
async def test_replication_lag(cron_context):
    lags = await replication_lag.load_stats(cron_context)
    assert lags == [
        replication_lag.Lag(
            consumer_id='upload_payout_ready_batches_to_arnold',
            value=datetime.timedelta(days=2, seconds=29),
        ),
        replication_lag.Lag(
            consumer_id='upload_export_batches_to_arnold',
            value=datetime.timedelta(days=1, seconds=16),
        ),
        replication_lag.Lag(
            consumer_id='upload_payout_ready_batches_to_hahn',
            value=datetime.timedelta(0),
        ),
    ]

    out = await replication_lag.run_check(cron_context)
    assert out == (
        '0; '
        'consumer=upload_payout_ready_batches_to_arnold lag=2 days, 0:00:29; '
        'consumer=upload_export_batches_to_arnold lag=1 day, 0:00:16'
    )
