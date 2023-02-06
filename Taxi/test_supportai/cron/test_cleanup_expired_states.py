# pylint: disable=redefined-outer-name
import pytest

from supportai import models as db_models
from supportai.generated.cron import run_cron


@pytest.mark.now('2021-08-02T10:00:00')
@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_cleanup_expired_states(cron_context):
    await run_cron.main(
        ['supportai.crontasks.cleanup_expired_states', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:
        state = await db_models.State.select_by_project_and_chat(
            cron_context, conn, project_id='test_project', chat_id='1',
        )

        assert state is not None

        state = await db_models.State.select_by_project_and_chat(
            cron_context, conn, project_id='test_project', chat_id='2',
        )

        assert state is None
