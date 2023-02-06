# pylint: disable=redefined-outer-name
import datetime

import pytest

from fleet_support_chat.generated.cron import cron_context as context_module
from fleet_support_chat.generated.cron import run_cron


async def _run_cron_task():
    await run_cron.main(
        [
            'fleet_support_chat.crontasks.support_chat_events_cleaner',
            '-t',
            '0',
        ],
    )


async def _count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.write_pool.fetchval(
        'SELECT COUNT(id) FROM support_chat_events;',
    )


@pytest.mark.config(OPTEUM_SUPPORT_CHAT_EVENTS_CLEANER={'enable': False})
@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_config_disabled(cron_context: context_module.Context):
    await _run_cron_task()
    count = await _count(cron_context)

    assert count == 8


@pytest.mark.config(
    FLEET_SUPPORT_CHAT_EVENTS_CLEANER={
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
        return datetime.datetime.fromisoformat('2020-01-22T10:07:00')

    await _run_cron_task()
    count = await _count(cron_context)

    assert count == 5
