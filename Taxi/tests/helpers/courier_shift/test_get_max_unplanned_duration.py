import asyncio
import datetime

import pytest

from libstall.model import coerces
from stall.helpers.courier_shift_h import get_max_unplanned_duration


async def test_max_day_hours(tap, dataset):
    with tap.plan(4, 'не превышаем лимит в день'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        courier = await dataset.courier(
            cluster=cluster,
            extra_vars={
                'can_take_unplanned_shift': True,
            }
        )
        store = await dataset.store(cluster=cluster)

        await asyncio.gather(
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-19T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-19T16:00:00+00:00'),
                status='complete',
            ),
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-19T22:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-20T04:00:00+00:00'),
                status='complete',
            ),
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-24T10:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-24T22:00:00+00:00'),
                status='complete',
            ),
        )

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-20T10:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=8),
               'осталось 8 часов с учётом потраченного лимита в 4 часа')

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-21T10:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=12),
               'остались все 12 часов так как смен на день нет')

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-21T20:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=4),
               'осталось 4 часа до полуночи')

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-24T12:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=0),
               'время уже полностью занято')


@pytest.mark.parametrize('settings,remaining_hours', [
    ({'week_from_sunday': True}, 2),
    ({'week_from_sunday': False}, 6),
    ({'week_from_sunday': None}, 6),
    ({}, 6),
])
async def test_max_week_hours(tap, dataset, settings, remaining_hours):
    with tap.plan(1, 'не превышаем лимит в неделю'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
                'max_week_hours': 24,
                **settings,
            }
        )
        courier = await dataset.courier(
            cluster=cluster,
            extra_vars={
                'can_take_unplanned_shift': True,
            }
        )
        store = await dataset.store(cluster=cluster)

        await asyncio.gather(
            # пятница прошлой недели
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-17T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-17T16:00:00+00:00'),
                status='complete',
            ),
            # с воскресенья прошлой недели по понедельник текущей
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-19T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-19T16:00:00+00:00'),
                status='complete',
            ),
            # с воскресенья по понедельник уже текущей недели
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-19T22:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-20T04:00:00+00:00'),
                status='complete',
            ),
            # пятница текущей недели
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-24T10:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-24T22:00:00+00:00'),
                status='complete',
            ),
            # с воскресенья текущей недели по понедельник следующей
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-26T22:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-27T04:00:00+00:00'),
                status='complete',
            ),
        )

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-22T10:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=remaining_hours),
               f'остаток лимита в неделю – {remaining_hours} часов')


async def test_closest_shift(tap, dataset):
    with tap.plan(3, 'не пересекаемся с ближайшей сменой'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        courier = await dataset.courier(
            cluster=cluster,
            extra_vars={
                'can_take_unplanned_shift': True,
            }
        )
        store = await dataset.store(cluster=cluster)

        shift = await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=coerces.date_time('2022-06-24T14:00:00+00:00'),
            closes_at=coerces.date_time('2022-06-24T18:00:00+00:00'),
            status='waiting',
        )

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-24T00:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=8),
               'остаток лимита в день – 8 часов')

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-24T10:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=4),
               'до ближайшей смены 4 часа')

        shift.status = 'processing'
        await shift.save()

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-24T15:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=0),
               'смена уже идёт')


async def test_cannot_take(tap, dataset):
    with tap.plan(1, 'курьер не может брать свободные слоты'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'max_day_hours': 12,
            }
        )
        courier = await dataset.courier(cluster=cluster)
        await dataset.store(cluster=cluster)

        max_duration = await get_max_unplanned_duration(
            courier=courier, setup=cluster.courier_shift_setup,
            now_=coerces.date_time('2022-06-22T10:00:00+00:00'),
        )
        tap.eq(max_duration, datetime.timedelta(hours=0),
               'максимальная длительность 0')
