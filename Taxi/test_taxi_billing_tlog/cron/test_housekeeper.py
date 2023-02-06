import pytest

from taxi_billing_tlog.crontasks import housekeeper


@pytest.mark.pgsql(
    'billing_tlog@0',
    files=('journal.sql', 'consumer_offset.sql', 'payments.sql'),
)
@pytest.mark.config(
    BILLING_TLOG_PG_HOUSEKEEPER_ENABLED=True,
    BILLING_TLOG_PG_JOURNAL_ROWS_TO_KEEP=3,
    BILLING_TLOG_PG_ACTIVE_CONSUMERS=['consumer_1', 'consumer_2'],
    BILLING_TLOG_JOURNAL_TABLES={
        'payments': {
            'active_consumers': ['consumer_3'],
            'is_housekeeping_enabled': True,
        },
    },
)
@pytest.mark.parametrize(
    'expected_journal_size, expected_payments_size',
    [
        pytest.param(4, 5),
        pytest.param(
            4,
            6,
            marks=pytest.mark.config(
                BILLING_TLOG_JOURNAL_TABLES={
                    'payments': {
                        'active_consumers': ['consumer_3'],
                        'is_housekeeping_enabled': False,
                    },
                },
            ),
            id='Do not truncate if housekeeping disabled',
        ),
    ],
)
async def test_smoke(
        cron_context, expected_journal_size, expected_payments_size,
):
    await housekeeper.do_housekeeping(cron_context, log_extra={})

    async def query_size(table: str) -> int:
        return await cron_context.pg.master_pool.fetchval(
            'SELECT COUNT(*) FROM tlog.{table}'.format(table=table),
        )

    journal_size = await query_size('journal')
    payments_size = await query_size('payments')

    assert journal_size == expected_journal_size
    assert payments_size == expected_payments_size
