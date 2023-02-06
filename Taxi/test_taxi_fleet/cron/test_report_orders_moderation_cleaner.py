# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi_fleet.generated.cron import cron_context as context_module
from taxi_fleet.generated.cron import run_cron


async def _run_cron_task():
    await run_cron.main(
        ['taxi_fleet.crontasks.report_orders_moderation_cleaner', '-t', '0'],
    )


async def _count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.main_master.fetchval(
        'SELECT COUNT(id) FROM orders_moderation_status;',
    )


@pytest.mark.config(OPTEUM_REPORT_ORDERS_MODERATION_CLEANER={'enable': False})
@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_config_disabled(cron_context: context_module.Context):
    await _run_cron_task()
    count = await _count(cron_context)

    assert count == 8


@pytest.mark.config(
    OPTEUM_REPORT_ORDERS_MODERATION_CLEANER={
        'days': 3,
        'batch_limit': 3,
        'delay': 0.1,
        'enable': True,
        'max_batches_per_run': 2,
    },
)
@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success(cron_context: context_module.Context, patch):
    @patch('datetime.datetime.today')
    def datetime_today():  # pylint: disable-msg=W0612
        return datetime.datetime.fromisoformat('2020-01-08T10:07:00')

    await _run_cron_task()
    count = await _count(cron_context)

    assert count == 3
