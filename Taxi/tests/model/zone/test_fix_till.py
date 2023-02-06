from datetime import datetime, timedelta
from libstall.util import tzone

from stall.model.zone import Zone


async def test_fix_till_templates(tap, dataset, job):
    with tap.plan(6, 'Шаблоны не меняются'):
        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zones = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
            ],
            sort=(),
        )

        zone1 = zones.list[0]
        zone1.status = 'template'
        await zone1.save()
        time1 = zone1.effective_from

        zone2 = await dataset.zone(
            store=store,
            status='template',
            effective_from=datetime.now(tz=tzone('UTC')) + timedelta(days=2),
        )
        time2 = zone2.effective_from

        tap.ok(await zone2.approve(user=user), 'Аппрувим')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await zone1.reload() as zone:
            tap.eq(
                zone.effective_from,
                time1,
                'effective_from не менялась'
            )
            tap.eq(zone.effective_till, None, 'effective_till не менялась')

        with await zone2.reload() as zone:
            tap.eq(
                zone.effective_from,
                time2,
                'effective_from не менялась'
            )
            tap.eq(zone.effective_till, None, 'effective_till не менялась')


async def test_fix_till_old(tap, dataset, job, now):
    with tap.plan(6, 'Старые зоны не меняются'):

        store   = await dataset.store()
        user   = await dataset.user(store=store)
        zones = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
            ],
            sort=(),
        )

        zone1 = zones.list[0]

        zone1.effective_from = datetime(2021, 1, 1, tzinfo=tzone('UTC'))
        zone1.effective_till = datetime(2021, 1, 31, 23, 59,
                                        59, tzinfo=tzone('UTC'))

        await zone1.save()

        effective_from2 = now().replace(minute=0, second=0, microsecond=0)
        effective_from2 += timedelta(hours=2)
        zone2   = await dataset.zone(
            store=store,
            status='template',
            effective_from=effective_from2,
        )

        tap.ok(await zone2.approve(user=user), 'Аппрувим')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await zone1.reload() as zone:
            tap.eq(
                zone.effective_from,
                datetime(2021, 1, 1, tzinfo=tzone('UTC')),
                'effective_from старая не менялась'
            )
            tap.eq(
                zone.effective_till,
                datetime(2021, 1, 31, 23, 59, 59, tzinfo=tzone('UTC')),
                'effective_till старая не менялась'
            )

        with await zone2.reload() as zone:
            tap.eq(zone.effective_from, effective_from2,
                   'effective_from не менялась')
            tap.eq(zone.effective_till, None, 'effective_till не менялась')


async def test_fix_till_future(tap, dataset, job, now):
    with tap.plan(6, 'Будущие зоны не меняются, но себе проставляем'):

        effective_from1 = now().replace(minute=0, second=0, microsecond=0)
        effective_from1 += timedelta(days=2)

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        zones = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
            ],
            sort=(),
        )
        with zones.list[0] as zone1:
            zone1.effective_from = effective_from1
            await zone1.save()

        effective_from2 = now().replace(minute=0, second=0, microsecond=0)
        effective_from2 += timedelta(hours=2)

        zone2   = await dataset.zone(
            store=store,
            status='template',
            effective_from=effective_from2,
        )

        tap.ok(await zone2.approve(user=user), 'Аппрувим')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await zone1.reload() as zone:
            tap.eq(
                zone.effective_from,
                effective_from1,
                'effective_from будущие не трогаем'
            )
            tap.eq(
                zone.effective_till,
                None,
                'effective_till будущие не трогаем'
            )

        with await zone2.reload() as zone:
            tap.eq(
                zone.effective_from,
                effective_from2,
                'effective_from не менялась'
            )
            tap.eq(
                zone.effective_till,
                effective_from1 - timedelta(seconds=1),
                'effective_till подстроена под будущее'
            )


async def test_return_none(tap, dataset, job):
    with tap.plan(4, 'Если будущая зона пропадает, то убираем границу'):

        store   = await dataset.store()
        zones = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
            ],
            sort=(),
        )
        zone1 = zones.list[0]
        zone1.effective_from = datetime(2021, 1, 1, tzinfo=tzone('UTC'))
        zone1.effective_till = datetime(
            2021, 2, 28, 23, 59, 59, tzinfo=tzone('UTC'))
        await zone1.save()

        tap.ok(await zone1.save(fix_till=True), 'Запустили перерасчет')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await zone1.reload() as zone:
            tap.eq(
                zone.effective_from,
                datetime(2021, 1, 1, tzinfo=tzone('UTC')),
                'effective_from не трогаем'
            )
            tap.eq(
                zone.effective_till,
                None,
                'effective_till опять без границы'
            )


async def test_active_to_template(tap, dataset, job, now):
    with tap.plan(4, 'Если будущую подтвержденную зону перевести в '
                     '"Черновик", то у текущей убираем границу'):

        store = await dataset.store()
        zones = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
            ],
            sort=(),
        )
        zone1 = zones.list[0]
        zone1.effective_from = datetime(2021, 1, 1, tzinfo=tzone('UTC'))
        zone1.effective_till = now() + timedelta(days=1)
        await zone1.save()

        zone2 = await dataset.zone(
            store=store,
            status='active',
            effective_from=now() + timedelta(days=1, seconds=1),
            effective_till=None,
        )
        zone2.status = 'template'

        tap.ok(await zone2.save(fix_till=True),
               'Сохранили с запуском перерасчета')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await zone1.reload() as zone:
            tap.eq(
                zone.effective_from,
                datetime(2021, 1, 1, tzinfo=tzone('UTC')),
                'effective_from не трогаем'
            )
            tap.eq(
                zone.effective_till,
                None,
                'effective_till опять без границы'
            )


async def test_empty_list(tap, dataset, job):
    with tap.plan(4, 'Пересчет с пустым списком зон'):

        store = await dataset.store()
        zones = await Zone.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
            ],
            sort=(),
        )
        zone1 = zones.list[0]
        zone1.effective_from = datetime(2021, 1, 1, tzinfo=tzone('UTC'))
        zone1.effective_till = None
        zone1.status = 'template'
        await zone1.save()

        tap.ok(await zone1.save(fix_till=True),
               'Сохранили с запуском перерасчета')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await zone1.reload() as zone:
            tap.eq(
                zone.effective_from,
                datetime(2021, 1, 1, tzinfo=tzone('UTC')),
                'effective_from не трогаем'
            )
            tap.eq(
                zone.effective_till,
                None,
                'effective_till опять без границы'
            )
