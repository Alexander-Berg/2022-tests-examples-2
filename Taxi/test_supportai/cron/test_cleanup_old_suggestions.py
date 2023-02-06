# pylint: disable=redefined-outer-name
import pytest

from supportai import models as db_models
from supportai.generated.cron import run_cron


@pytest.mark.now('2021-08-03T10:00:00')
@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_cleanup_old_suggestions(cron_context):
    async with cron_context.pg.slave_pool.acquire() as conn:
        suggestions = await db_models.FeatureSuggestion.get_top_suggestions(
            cron_context,
            conn,
            feature='feature1',
            project_slug='ya_lavka',
            top=10,
        )

        assert len(suggestions) == 3

    await run_cron.main(
        ['supportai.crontasks.cleanup_old_suggestions', '-t', '0'],
    )

    async with cron_context.pg.slave_pool.acquire() as conn:
        suggestions = await db_models.FeatureSuggestion.get_top_suggestions(
            cron_context,
            conn,
            feature='feature1',
            project_slug='ya_lavka',
            top=10,
        )

        assert suggestions == []
