import datetime

import pytest
import pytz

from libstall.model import coerces
from scripts.dev import fill_schets


@pytest.mark.parametrize(['tz', 'expected_start_time'], [
    ('Asia/Yekaterinburg', '2021-11-17T12:00+05:00'),
    ('Europe/Moscow', '2021-11-17T12:00+03:00'),
    ('Europe/London', '2021-11-17T12:00+00:00'),
    ('Europe/Paris', '2021-11-17T12:00+01:00'),
])
async def test_common(tap, dataset, time_mock, tz, expected_start_time):
    with tap:
        time_mock.set(datetime.datetime(
            2021, 11, 15, 12, 0,
            tzinfo=pytz.utc,
        ))

        creator = await dataset.user()
        approver = await dataset.user()
        store = await dataset.store(tz=tz)

        schets = (await dataset.SchetTask.list(
            by='full',
            conditions=[('store_id', store.store_id)],
        )).list
        tap.ok(not schets, 'schets empty')

        await fill_schets.apply_schets_template(
            template={
                'schets': [{
                    'handler': 'crons_healthcheck',
                    'schedule': {
                        'start_time': '2021-11-17T12:00',
                        'interval': {'days': 1}
                    }
                }]
            },
            store=store,
            store_schets=[],
            created_by=creator.user_id,
            approved_by=approver.user_id,
            start_after_approve=True,
            apply=True,
        )

        schets = (await dataset.SchetTask.list(
            by='full',
            conditions=[('store_id', store.store_id)],
        )).list
        tap.ok(schets, 'schets not empty')
        tap.eq(len(schets), 1, 'created one schet')

        with schets[0] as schet:
            tap.eq(schet.store_id, store.store_id, 'store_id ok')
            tap.eq(schet.company_id, store.company_id, 'company_id ok')
            tap.eq(schet.created_by, creator.user_id, 'created_by ok')
            tap.eq(schet.tz, store.tz, 'tz ok')
            tap.ok(schet.schedule, 'schedule approved')
            tap.eq(schet.approved_by, approver.user_id, 'approved_by ok')
            tap.eq(schet.status, 'pending', 'schet started')
            tap.eq(
                schet.schedule.interval,
                datetime.timedelta(days=1),
                'interval ok'
            )
            tap.eq(
                schet.schedule.start_time,
                coerces.date_time(expected_start_time),
                'start_time ok'
            )
