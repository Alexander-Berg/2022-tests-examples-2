import asyncio
import datetime

import typing

from libstall.model import coerces
from stall.helpers.courier_shift_h import get_summary_durations
from stall.model.courier_shift import CourierShift


async def test_common(tap, dataset):
    with tap.plan(12, 'суммарное время за день и за неделю'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        shifts = typing.cast(
            typing.List[CourierShift],
            await asyncio.gather(
                # вс 5 часов
                dataset.courier_shift(
                    cluster=cluster, store=store,
                    started_at=coerces.date_time('2022-06-19T12:00:00+00:00'),
                    closes_at=coerces.date_time('2022-06-19T17:00:00+00:00'),
                ),
                # вс 1 час + пн 4 часа
                dataset.courier_shift(
                    cluster=cluster, store=store,
                    started_at=coerces.date_time('2022-06-19T23:00:00+00:00'),
                    closes_at=coerces.date_time('2022-06-20T04:00:00+00:00'),
                ),
                # пн 5 часов
                dataset.courier_shift(
                    cluster=cluster, store=store,
                    started_at=coerces.date_time('2022-06-20T12:00:00+00:00'),
                    closes_at=coerces.date_time('2022-06-20T17:00:00+00:00'),
                ),
                # вт 5 часов
                dataset.courier_shift(
                    cluster=cluster, store=store,
                    started_at=coerces.date_time('2022-06-21T12:00:00+00:00'),
                    closes_at=coerces.date_time('2022-06-21T17:00:00+00:00'),
                ),
            )
        )

        day_duration, week_duration = await get_summary_durations(
            shifts, coerces.date_time('2022-06-18T12:00:00+00:00'),
        )
        tap.eq(day_duration, datetime.timedelta(hours=0),
               'сб (пн-вс): 0 часов за день')
        tap.eq(week_duration, datetime.timedelta(hours=6),
               'сб (пн-вс): 6 часов за неделю')

        day_duration, week_duration = await get_summary_durations(
            shifts, coerces.date_time('2022-06-18T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq(day_duration, datetime.timedelta(hours=0),
               'сб (вс-сб): 0 часов за день')
        tap.eq(week_duration, datetime.timedelta(hours=0),
               'сб (вс-сб): 0 часов за неделю')

        day_duration, week_duration = await get_summary_durations(
            shifts, coerces.date_time('2022-06-19T12:00:00+00:00'),
        )
        tap.eq(day_duration, datetime.timedelta(hours=6),
               'вс (пн-вс): 6 часов за день')
        tap.eq(week_duration, datetime.timedelta(hours=6),
               'вс (пн-вс): 6 часов за неделю')

        day_duration, week_duration = await get_summary_durations(
            shifts, coerces.date_time('2022-06-19T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq(day_duration, datetime.timedelta(hours=6),
               'вс (вс-сб): 6 часов за день')
        tap.eq(week_duration, datetime.timedelta(hours=20),
               'вс (вс-сб): 20 часов за неделю')

        day_duration, week_duration = await get_summary_durations(
            shifts, coerces.date_time('2022-06-20T12:00:00+00:00'),
        )
        tap.eq(day_duration, datetime.timedelta(hours=9),
               'пн (пн-вс): 9 часов за день')
        tap.eq(week_duration, datetime.timedelta(hours=14),
               'пн (пн-вс): 14 часов за неделю')

        day_duration, week_duration = await get_summary_durations(
            shifts, coerces.date_time('2022-06-20T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq(day_duration, datetime.timedelta(hours=9),
               'пн (вс-сб): 9 часов за день')
        tap.eq(week_duration, datetime.timedelta(hours=20),
               'пн (вс-сб): 20 часов за неделю')
