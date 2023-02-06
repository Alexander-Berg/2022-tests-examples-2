# pylint: disable=redefined-outer-name
import pytest

from supportai import models as db_models
from supportai.generated.cron import run_cron


@pytest.mark.now('2021-08-02T10:00:00')
@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_cleanup_expired_debug(cron_context):
    await run_cron.main(
        ['supportai.crontasks.cleanup_expired_debug', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:
        debug = await db_models.Debug.select_by_project_chat_iteration(
            cron_context,
            conn,
            project_slug='test_project',
            chat_id='1234',
            iteration_number=1,
        )

        assert debug is None

        debug = await db_models.Debug.select_by_project_chat_iteration(
            cron_context,
            conn,
            project_slug='test_project',
            chat_id='1234',
            iteration_number=2,
        )

        assert debug is not None
