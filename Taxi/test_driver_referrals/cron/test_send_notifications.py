# pylint: disable=redefined-outer-name,unused-variable,global-statement
import datetime
import typing

import pytest

from driver_referrals.common import db
from driver_referrals.common import models
from driver_referrals.generated.cron import run_cron
from test_driver_referrals import conftest


async def get_notifications(
        context,
        task_date: typing.Optional[datetime.date] = datetime.date(2019, 4, 20),
        notification_status=models.NotificationStatus.CREATED,
):
    return await db.get_notifications(
        context, task_date=task_date, notification_status=notification_status,
    )


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.config(
    DRIVER_REFERRALS_NOTIFICATIONS_BY_COUNTRIES={
        '__default__': {
            'cargo': [],
            'eda': [],
            'lavka': [],
            'retail': [],
            'taxi': ['rule_assigned'],
            'taxi_walking_courier': [],
        },
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO tasks (id, task_date, billing_done) """
        """VALUES ('task_id', '2019-04-20', '2019-04-20')""",
    ],
    files=['pg_driver_referrals_cron.sql'],
)
async def test_send_notifications_cron(cron_context):
    assert len(await get_notifications(cron_context)) == 1
    async with conftest.TablesDiffCounts(cron_context):
        await run_cron.main(
            ['driver_referrals.jobs.send_notifications', '-t', '0', '-d'],
        )
    assert not await get_notifications(cron_context)
    assert await get_notifications(
        cron_context, notification_status=models.NotificationStatus.SENT,
    )


@pytest.mark.translations(
    taximeter_backend_driver_referrals=conftest.TRANSLATIONS,
)
@pytest.mark.pgsql('driver_referrals', files=['pg_driver_referrals_web.sql'])
async def test_send_notifications_web(cron_context):
    assert len(await get_notifications(cron_context, task_date=None)) == 1
    async with conftest.TablesDiffCounts(cron_context):
        await run_cron.main(
            ['driver_referrals.jobs.send_notifications', '-t', '0', '-d'],
        )
    assert not await get_notifications(cron_context, task_date=None)
    assert await get_notifications(
        cron_context,
        notification_status=models.NotificationStatus.SKIPPED,
        task_date=None,
    )
