# pylint: disable=redefined-outer-name,unused-variable
import pytest

from logs_errors_filters.generated.cron import run_cron
from logs_errors_filters.utils import db_helpers


@pytest.mark.pgsql('logs_errors_filters', files=['test_disabler.sql'])
@pytest.mark.config(
    LOGSERRORS_DISABLING_SETTINGS={
        'auto_disabling': True,
        'filter_ttl_days': 45,
    },
)
@pytest.mark.now('2019-10-19T12:00:00')
async def test_disabler(patch, cron_context):
    await run_cron.main(['logs_errors_filters.crontasks.disabler', '-t', '0'])
    query = 'SELECT * FROM logs_errors_filters.filters ORDER BY id;'
    rows = await db_helpers.get_query_rows(query, (), cron_context)
    assert rows[0]['enabled'] is True
    assert rows[1]['enabled'] is False
