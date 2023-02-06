# pylint: disable=too-many-locals,too-many-statements

from datetime import datetime, timedelta, timezone
import argparse

from scripts.dev.set_shift_local_time import main


async def test_simple(tap, dataset, now, tzone):
    with tap.plan(33, 'Простановка локального времени сменам'):
        cluster1 = await dataset.cluster(tz='Asia/Omsk') # UTC+06:00
        store1 = await dataset.store(cluster=cluster1)
        cluster2 = await dataset.cluster() # UTC+03:00
        store2 = await dataset.store(cluster=cluster2)
        cluster3 = await dataset.cluster(tz='Europe/London') # DST: UTC+01 / UTC
        store3 = await dataset.store(cluster=cluster3)

        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at1 = _now + timedelta(hours=1)
        closes_at1 = _now + timedelta(hours=2)
        _now = now(tz=tzone('UTC')).replace(microsecond=0)
        started_at2 = _now + timedelta(hours=1)
        closes_at2 = _now + timedelta(hours=2)

        shift1 = await dataset.courier_shift(
            store=store1,
            started_at=started_at1,
            closes_at=closes_at1,
            tz=None,
        )
        shift2 = await dataset.courier_shift(
            store=store1,
            started_at=datetime(2021, 10, 1, 11, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 10, 1, 15, 0, 0, tzinfo=timezone.utc),
            tz='Europe/London',
        )
        shift3 = await dataset.courier_shift(
            store=store2,
            started_at=started_at2,
            closes_at=closes_at2,
        )
        shift4 = await dataset.courier_shift(
            store=store2,
            started_at=started_at2,
            closes_at=closes_at2,
            tz='Europe/Moscow',
        )
        shift5 = await dataset.courier_shift(
            store=store2,
            started_at=started_at1,
            closes_at=closes_at1,
            tz='Asia/Omsk',
        )
        # Разный DST
        shift6 = await dataset.courier_shift(
            store=store3,
            started_at=datetime(2021, 10, 1, 11, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 10, 1, 15, 0, 0, tzinfo=timezone.utc),
            tz=None,
        )
        shift7 = await dataset.courier_shift(
            store=store3,
            started_at=datetime(2021, 12, 1, 11, 0, 0, tzinfo=timezone.utc),
            closes_at=datetime(2021, 12, 2, 0, 0, 0, tzinfo=timezone.utc),
            tz=None,
        )
        # tz не меняется, локальное время обнулено
        shift8 = await dataset.courier_shift(
            store=store2,
            started_at=started_at2,
            closes_at=closes_at2,
            tz='Europe/Moscow',
        )
        shift8.local_started_at = None
        shift8.local_closed_at = None
        await shift8.save()

        local_started_at1 = started_at1.replace(tzinfo=None)
        local_started_at2 = started_at2.replace(tzinfo=None)

        tap.eq(
            shift1.local_started_at,
            None,
            'Нет локального времени'
        )
        tap.eq(shift1.tz, None, 'Нет временной зоны')
        tap.eq(
            shift2.local_started_at,
            datetime(2021, 10, 1, 12, 0, 0),
            'UTC LON DST+1'
        )
        tap.eq(shift2.tz, 'Europe/London', 'Europe/London')
        tap.eq(
            shift3.local_started_at,
            local_started_at2 + timedelta(hours=3),
            'UTC MSK'
        )
        tap.eq(shift4.tz, 'Europe/Moscow', 'Europe/Moscow')
        tap.eq(
            shift4.local_started_at,
            local_started_at2 + timedelta(hours=3),
            'UTC MSK'
        )
        tap.eq(shift4.tz, 'Europe/Moscow', 'Europe/Moscow')
        tap.eq(
            shift5.local_started_at,
            local_started_at1 + timedelta(hours=3),
            'MSK OMSK'
        )
        tap.eq(shift5.tz, 'Asia/Omsk', 'Asia/Omsk')
        tap.eq(
            shift6.local_started_at,
            None,
            'Нет локального времени'
        )
        tap.eq(shift6.tz, None, 'Нет временной зоны')
        tap.eq(
            shift7.local_started_at,
            None,
            'Нет локального времени'
        )
        tap.eq(shift7.tz, None, 'Нет временной зоны')
        tap.eq(
            shift8.local_started_at,
            None,
            'Нет локального времени'
        )
        tap.eq(shift8.tz, 'Europe/Moscow', 'Europe/Moscow')

        # Выполняем скрипт
        args = argparse.Namespace(
            anew=True,
            apply=True,
            cursor=None,
        )
        tap.eq(await main(args), None, 'Скрипт выполнился')

        await shift1.reload()
        tap.eq(
            shift1.local_started_at,
            local_started_at1 + timedelta(hours=3),
            'MSK OMSK'
        )
        tap.eq(shift1.tz, 'Asia/Omsk', 'Asia/Omsk')

        await shift2.reload()
        tap.eq(
            shift2.local_started_at,
            datetime(2021, 10, 1, 17, 0, 0),
            'LON OMSK'
        )
        tap.eq(shift2.tz, 'Asia/Omsk', 'Asia/Omsk')

        await shift3.reload()
        tap.eq(
            shift3.local_started_at,
            local_started_at2 + timedelta(hours=3),
            'UTC MSK'
        )
        tap.eq(shift3.tz, 'Europe/Moscow', 'Europe/Moscow')

        await shift4.reload()
        tap.eq(
            shift4.local_started_at,
            local_started_at2 + timedelta(hours=3),
            'UTC MSK'
        )
        tap.eq(shift4.tz, 'Europe/Moscow', 'Europe/Moscow')

        await shift5.reload()
        tap.eq(
            shift5.local_started_at,
            local_started_at1,
            'MSK MSK'
        )
        tap.eq(shift5.tz, 'Europe/Moscow', 'Europe/Moscow')

        await shift6.reload()
        tap.eq(
            shift6.local_started_at,
            datetime(2021, 10, 1, 12, 0, 0),
            'UTC LON DST+1'
        )
        tap.eq(shift6.tz, 'Europe/London', 'Europe/London')

        await shift7.reload()
        tap.eq(
            shift7.local_started_at,
            datetime(2021, 12, 1, 11, 0, 0),
            'UTC LON'
        )
        tap.eq(shift7.tz, 'Europe/London', 'Europe/London')

        await shift8.reload()
        tap.eq(
            shift8.local_started_at,
            local_started_at2 + timedelta(hours=3),
            'Проставлено локальное время'
        )
        tap.eq(shift8.tz, 'Europe/Moscow', 'Не менялся TZ')


async def test_no_updates(tap, dataset, now, tzone):
    with tap.plan(5, 'Не генерируются онбовления'):
        cluster = await dataset.cluster() # UTC+03:00
        store = await dataset.store(cluster=cluster)

        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        started_at = _now + timedelta(hours=1)
        closes_at = _now + timedelta(hours=2)
        _now = now(tz=tzone('UTC')).replace(microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            started_at=started_at,
            closes_at=closes_at,
            tz='Asia/Omsk',
        )
        shift_updated = shift.updated
        shift_lsn = shift.lsn

        local_started_at = started_at.replace(tzinfo=None)

        # Выполняем скрипт
        args = argparse.Namespace(
            anew=True,
            apply=True,
            cursor=None,
        )
        tap.eq(await main(args), None, 'Скрипт выполнился')

        await shift.reload()
        tap.eq(
            shift.local_started_at,
            local_started_at,
            'MSK MSK'
        )
        tap.eq(shift.tz, 'Europe/Moscow', 'Europe/Moscow')
        tap.eq(shift.updated, shift_updated, 'updated не обновился')
        tap.eq(shift.lsn, shift_lsn, 'lsn не обновился')
