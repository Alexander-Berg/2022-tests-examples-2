from datetime import timedelta

from scripts.cron.couriers_drop_beginner import process_dropping_beginner
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_simple(tap, dataset, now, cfg):
    with tap.plan(2, 'Снимаем тег спустя 24 часа'):
        cfg.set('business.courier_shift.beginner_stories_hours', 24)

        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER, tag],
        )
        shift = await dataset.courier_shift(
            status='complete',
            cluster=cluster,
            courier=courier,
            started_at=now() - timedelta(days=1, hours=10),
            closes_at=now() - timedelta(days=1, hours=1),
            tags=[TAG_BEGINNER, tag],
        )

        await process_dropping_beginner(cluster_id=cluster.cluster_id)

        with await courier.reload():
            tap.eq(courier.tags, [tag], 'у курьера новичок убран')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER, tag], 'у смены новичок остался')


async def test_too_early(tap, dataset, now, cfg):
    with tap.plan(2, 'Не снимаем тег, т.к. еще рано'):
        cfg.set('business.courier_shift.beginner_stories_hours', 2)  # 2 часа

        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER, tag],
        )
        shift = await dataset.courier_shift(
            status='complete',
            cluster=cluster,
            courier=courier,
            started_at=now() - timedelta(days=1, hours=10),
            closes_at=now() - timedelta(hours=1),       # закрылась 1 час назад
            tags=[TAG_BEGINNER, tag],
        )

        await process_dropping_beginner(cluster_id=cluster.cluster_id)

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER, tag], 'у курьера новичок есть')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER, tag], 'у смены новичок остался')


async def test_alien_cluster(tap, dataset, now, uuid, cfg):
    with tap.plan(2, 'Чужой кластер не трогаем'):
        cfg.set('business.courier_shift.beginner_stories_hours', 24)

        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER, tag],
        )
        shift = await dataset.courier_shift(
            status='complete',
            cluster=cluster,
            courier=courier,
            started_at=now() - timedelta(days=1, hours=10),
            closes_at=now() - timedelta(days=1, hours=1),
            tags=[TAG_BEGINNER, tag],
        )

        await process_dropping_beginner(cluster_id=uuid())

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER, tag], 'тег остался')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER, tag], 'тег остался')


async def test_disabled_courier(tap, dataset, now, cfg):
    with tap.plan(2, 'Отключенных курьеров не трогаем'):
        cfg.set('business.courier_shift.beginner_stories_hours', 1)

        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            status='disabled',
            tags=[TAG_BEGINNER, tag],
        )
        shift = await dataset.courier_shift(
            status='complete',
            cluster=cluster,
            courier=courier,
            started_at=now() - timedelta(hours=10),
            closes_at=now() - timedelta(hours=2),
            tags=[TAG_BEGINNER, tag],
        )

        await process_dropping_beginner(cluster_id=cluster.cluster_id)

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER, tag], 'тег остался')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER, tag], 'тег остался')


async def test_not_complete(tap, dataset, now, cfg):
    with tap.plan(2, 'Новичков без complete-смен не трогаем'):
        cfg.set('business.courier_shift.beginner_stories_hours', 1)

        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER, tag],
        )
        shift = await dataset.courier_shift(
            status='absent',                    # опоздал, такая не считается
            cluster=cluster,
            courier=courier,
            started_at=now() - timedelta(hours=10),
            closes_at=now() - timedelta(hours=2),
            tags=[TAG_BEGINNER, tag],
        )

        await process_dropping_beginner(cluster_id=cluster.cluster_id)

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER, tag], 'тег остался')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER, tag], 'тег остался')


async def test_old_beginner(tap, dataset, now, cfg):
    with tap.plan(2, 'Новичку выдали тег вручную, т.к. повторное обучение'):
        cfg.set('business.courier_shift.beginner_stories_hours', 1)

        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER, tag],
        )
        shift = await dataset.courier_shift(
            status='complete',
            cluster=cluster,
            courier=courier,
            started_at=now() - timedelta(days=180, hours=10),
            closes_at=now() - timedelta(days=180),
            tags=[TAG_BEGINNER, tag],
        )

        await process_dropping_beginner(cluster_id=cluster.cluster_id)

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER, tag], 'тег остался')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER, tag], 'тег остался')


