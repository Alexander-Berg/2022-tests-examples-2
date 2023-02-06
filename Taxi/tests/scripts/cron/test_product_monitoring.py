import asyncio
import calendar
import logging

from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from _pytest.logging import LogCaptureFixture
from easytap.pytest_plugin import PytestTap

from scripts.cron.product_monitoring import process

import tests.dataset as dt

from libstall.log import metrics_log


@contextmanager
def propagate_log(logger: logging.Logger):
    propagate_backup = logger.propagate
    logger.propagate = True
    try:
        yield
    finally:
        logger.propagate = propagate_backup


async def test_product_monitoring(
        tap: PytestTap, dataset: dt, caplog: LogCaptureFixture
):
    with tap, propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        time_now = datetime.now()
        curr_weekday = calendar.day_name[time_now.weekday()].lower()
        another_weekday = calendar.day_name[
            (time_now - timedelta(1)).weekday()
        ].lower()
        created_zones = []

        cluster = await dataset.cluster(title='Москва')
        store_1 = await dataset.store(cluster=cluster)
        # не работает в данный момент времени из-за type
        created_zones.append(await dataset.zone(
            store=store_1,
            status='active',
            effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc),
            timetable=[{
                'type': another_weekday,
                'begin': '00:00',
                'end': '00:00',
            }]
        ))
        # оба отрезка рабочие, считается 1 зона
        created_zones.append(await dataset.zone(
            store=store_1,
            status='active',
            effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc),
            timetable=[
                {
                    'type': curr_weekday,
                    'begin': '00:00',
                    'end': '00:00',
                },
                {
                    'type': 'everyday',
                    'begin': '00:00',
                    'end': '00:00',
                }
            ]
        ))

        store_2 = await dataset.store(cluster=cluster)
        for status in ('template', 'disabled'):
            created_zones.append(await dataset.zone(
                store=store_2,
                status=status,
                effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc)
            ))
        # 1 отрезок рабочий
        created_zones.append(await dataset.zone(
            store=store_1,
            status='active',
            effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc),
            timetable=[
                {
                    'type': curr_weekday,
                    'begin': time_now - timedelta(minutes=1),
                    'end': '00:00',
                },
                {
                    'type': another_weekday,
                    'begin': '00:00',
                    'end': '00:00',
                }
            ]
        ))
        # 1 отрезок рабочий
        created_zones.append(await dataset.zone(
            store=store_1,
            status='active',
            effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc),
            timetable=[
                {
                    'type': curr_weekday,
                    'begin': time_now - timedelta(minutes=1),
                    'end': '23:00',
                }
            ]
        ))
        # старая зона
        created_zones.append(await dataset.zone(
            store=store_2,
            status='active',
            effective_from=datetime(2021, 1, 1, tzinfo=timezone.utc),
            effective_till=datetime(2021, 1, 31, 23, 59,
                                    59, tzinfo=timezone.utc),
        ))
        # будущая зона
        created_zones.append(await dataset.zone(
            store=store_2,
            status='active',
            effective_from=datetime.now() + timedelta(days=2),
            effective_till=None,
        ))

        await dataset.store(cluster=cluster, status='active')
        await dataset.store(cluster=cluster, status='disabled')

        await asyncio.sleep(5)  # зоны беспощадно флапают

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(conditions=[('cluster_id', cluster.cluster_id)])

        sent_metrics = {
            rec.ctx['name']: rec.ctx['value']
            for rec in caplog.records
            if rec.name == metrics_log.name and 'name' in rec.ctx
        }

        tap.eq_ok(len(caplog.records), 3, '3 метрики')
        tap.eq_ok(
            sent_metrics['monitoring.active_stores'], 3, 'Количество лавок')
        tap.eq_ok(
            sent_metrics['monitoring.active_zones'],
            7,  # 4 созданные + 3 круглосуточные из фикстур активных сторов
            'Количество зон'
        )
        tap.eq_ok(
            sent_metrics['monitoring.running_zones'],
            6,  # 3 созданные + 3 круглосуточные из фикстур активных сторов
            'Количество зон'
        )


async def test_empty_cluster(
        tap: PytestTap, dataset: dt, caplog: LogCaptureFixture
):
    with tap, propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):
        cluster = await dataset.cluster()

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(conditions=[('cluster_id', cluster.cluster_id)])

        sent_metrics = {
            rec.ctx['name']: rec.ctx['value']
            for rec in caplog.records
            if rec.name == metrics_log.name and 'name' in rec.ctx
        }

        tap.eq_ok(
            sent_metrics['monitoring.active_stores'], 0, 'Количество лавок')
        tap.eq_ok(
            sent_metrics['monitoring.active_zones'], 0, 'Количество зон')


async def test_cluster_name(
        tap: PytestTap, dataset: dt, caplog: LogCaptureFixture
):
    with tap, propagate_log(metrics_log), \
            caplog.at_level(logging.INFO, logger=metrics_log.name):

        cluster = await dataset.cluster(title='Москва')
        await dataset.store(cluster=cluster)

        caplog.at_level(logging.INFO, logger=metrics_log.name)
        await process(conditions=[('cluster_id', cluster.cluster_id)])

        sent_metrics = {
            (rec.ctx['name'], rec.ctx['cluster_name']): rec.ctx['value']
            for rec in caplog.records
            if rec.name == metrics_log.name and 'name' in rec.ctx
        }

        tap.eq_ok(len(caplog.records), 3, '3 метрики')
        tap.in_ok(
            ('monitoring.active_stores', 'Moskva'), sent_metrics,
            'Имя кластера перевелось для active_stores'
        )
        tap.in_ok(
            ('monitoring.active_zones', 'Moskva'), sent_metrics,
            'Имя кластера перевелось для active_zones'
        )
        tap.in_ok(
            ('monitoring.running_zones', 'Moskva'), sent_metrics,
            'Имя кластера перевелось для running_zones'
        )
