# pylint: disable=redefined-outer-name
import pytest

from personal_goals.generated.cron import run_cron


async def run_cleanup():
    await run_cron.main(
        ['personal_goals.crontasks.notifications_cleanup', '-t', '0'],
    )


@pytest.mark.now('2019-08-15T12:00:00+0')
@pytest.mark.pgsql('personal_goals', files=['cleanup_notifications.sql'])
async def test_cleanup_default_config(pg_goals):
    notifications = await pg_goals.notifications.all()
    assert len(notifications) == 8

    await run_cleanup()

    notifications = await pg_goals.notifications.all()
    notification_ids = [x['id'] for x in notifications]
    assert notification_ids == ['n_id_1', 'n_id_2', 'n_id_3', 'n_id_4']


@pytest.mark.config(PERSONAL_GOALS_NOTIFICATIONS_CLEANUP_LIMIT=1)
@pytest.mark.now('2019-08-15T12:00:00+0')
@pytest.mark.pgsql('personal_goals', files=['cleanup_notifications.sql'])
async def test_cleanup_limit(pg_goals):
    notifications = await pg_goals.notifications.all()
    assert len(notifications) == 8

    await run_cleanup()

    notifications = await pg_goals.notifications.all()
    assert len(notifications) == 7


@pytest.mark.config(PERSONAL_GOALS_NOTIFICATIONS_CLEANUP_TTL=100)
@pytest.mark.now('2019-08-15T12:00:00+0')
@pytest.mark.pgsql('personal_goals', files=['cleanup_notifications.sql'])
async def test_cleanup_ttl(pg_goals):
    notifications = await pg_goals.notifications.all()
    assert len(notifications) == 8

    await run_cleanup()

    notifications = await pg_goals.notifications.all()
    assert len(notifications) == 3
