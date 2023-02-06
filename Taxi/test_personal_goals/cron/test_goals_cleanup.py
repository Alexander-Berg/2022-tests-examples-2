# pylint: disable=redefined-outer-name
import pytest

from personal_goals.generated.cron import run_cron


async def run_cleanup():
    await run_cron.main(['personal_goals.crontasks.goals_cleanup', '-t', '0'])


@pytest.mark.pgsql('personal_goals', files=['cleanup_goals.sql'])
async def test_cleanup_default_config(pg_goals):
    await run_cleanup()

    goals = await pg_goals.goals.all()
    goal_ids = [x['id'] for x in goals]
    assert goal_ids == ['goal_4']


@pytest.mark.config(PERSONAL_GOALS_GOALS_CLEANUP_LIMIT=1)
@pytest.mark.pgsql('personal_goals', files=['cleanup_goals.sql'])
async def test_cleanup_limit(pg_goals):
    goals = await pg_goals.goals.all()
    assert len(goals) == 4

    await run_cleanup()

    goals = await pg_goals.goals.all()
    assert len(goals) == 3
