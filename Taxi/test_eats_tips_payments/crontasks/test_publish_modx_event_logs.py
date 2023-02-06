import psycopg2.extras
import pytest

from eats_tips_payments.generated.cron import run_cron


@pytest.mark.mysql('chaevieprosto', files=['mysql_event_log.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_modx_meta.sql'])
async def test_publish_event_logs(patch, mock_stats, pgsql):
    await run_cron.main(
        ['eats_tips_payments.crontasks.publish_modx_event_logs', '-t', '0'],
    )

    cursor = pgsql['eats_tips_payments'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        """
        SELECT value
        FROM eats_tips_payments.modx_meta
        WHERE name = 'event_logs_cursor'
        """,
    )
    rows = cursor.fetchone()
    assert rows['value'] == '3'
