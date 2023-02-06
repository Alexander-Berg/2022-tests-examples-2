from datetime import timedelta

import pytest

from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_simple(tap, dataset, now, push_events_cache, job):
    with tap.plan(10, 'Была новичок смена_1, а стала смена_2'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
            tags=[TAG_BEGINNER],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
        )

        await shift_2.save(recheck_beginner=True)

        await push_events_cache(shift_2, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не поменялся #1')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера на месте #1')
            tap.eq(len(shift.shift_events), 0, 'новых событий нет #1')
            tap.eq(shift.tags, [], 'смена теперь НЕ новичок')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не поменялся #2')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера на месте #2')
            tap.eq(len(shift.shift_events), 0, 'новых событий нет #2')
            tap.eq(shift.tags, [TAG_BEGINNER], 'смена теперь Новичок')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'курьер все еще новичок')


async def test_err_no_courier(tap, dataset, now, push_events_cache, job):
    with tap.plan(4, 'Обработка случая - смена без курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        _now = now().replace(microsecond=0)
        shift = await dataset.courier_shift(
            store=store,
            status='request',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
        )

        await shift.save(recheck_beginner=True)

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(shift.status, 'request', 'статус не поменялся')
            tap.eq(shift.courier_id, None, 'курьера не изменился')
            tap.eq(shift.tags, [], 'новых тегов нет')


async def test_versed_courier(tap, dataset, now, push_events_cache, job):
    with tap.plan(3, 'У курьера нет тега Новичок, и он идет мимо'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[tag],
        )

        _now = now().replace(microsecond=0)
        shift = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=5),
        )

        await shift.save(recheck_beginner=True)

        await push_events_cache(shift, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift.reload():
            tap.eq(shift.tags, [], 'новых тегов нет')

        with await courier.reload():
            tap.eq(courier.tags, [tag], 'теги курьера не изменились')


async def test_courier_with_complete(tap, dataset, now, push_events_cache, job):
    with tap.plan(4, 'Тег с курьера снимается не сразу (потом крон-скриптом)'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[tag, TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)
        shift_1 = await dataset.courier_shift(
            store=store,
            status='complete',
            courier=courier,
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=3),
            tags=[TAG_BEGINNER],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            status='waiting',
            courier=courier,
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
            tags=[tag],
        )

        await shift_2.save(recheck_beginner=True)

        await push_events_cache(shift_2, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.tags, [TAG_BEGINNER], 'осталась новичком')

        with await shift_2.reload() as shift:
            tap.eq(shift.tags, [tag], 'тег не пострадал, и новичком не стала')

        with await courier.reload():
            tap.eq(courier.tags, [tag, TAG_BEGINNER], 'курьер все еще новичок')


@pytest.mark.parametrize('target_status', ['waiting', 'processing'])
async def test_multi_shift_statuses(
    tap, dataset, now, push_events_cache, job, target_status,
):
    with tap.plan(7, 'Выбор правильной смены из cancelled/released/leave'):
        cluster = await dataset.cluster()
        tag = (await dataset.courier_shift_tag()).title
        courier = await dataset.courier(
            cluster=cluster,
            tags=[tag, TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)
        _ignored_statuses = ('cancelled', 'released', 'leave', 'absent')
        ignored_shifts = [
            await dataset.courier_shift(
                status=status,
                courier=courier,
                started_at=_now + timedelta(hours=i),
                closes_at=_now + timedelta(hours=i + 3),
                # новичку не везет: отменили, отказался, ушел рано и опоздал
                tags=[TAG_BEGINNER, tag],
            ) for i, status in enumerate(_ignored_statuses, 1)
        ]

        shift_target = await dataset.courier_shift(
            status=target_status,
            courier=courier,
            started_at=_now + timedelta(days=1),
            closes_at=_now + timedelta(days=1, hours=2),
            tags=[tag],
        )

        # не важно, какая смена изменилась, всегда выбирается лучшая
        absent_shift = ignored_shifts[-1]
        await absent_shift.save(recheck_beginner=True)

        await push_events_cache(absent_shift, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        for shift in ignored_shifts:
            with await shift.reload():
                tap.eq(
                    shift.tags,
                    [TAG_BEGINNER, tag],
                    f'{shift.status} - пропал Новичок'
                )

        with await shift_target.reload() as shift:
            tap.eq(shift.tags, [tag, TAG_BEGINNER], 'добавился новичок')

        with await courier.reload():
            tap.eq(courier.tags, [tag, TAG_BEGINNER], 'новичок все еще')


async def test_processing_shift(tap, dataset, now, push_events_cache, job):
    with tap.plan(8, 'Смена-новичок исполняется, ее не вытеснить новой'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=[TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=_now - timedelta(hours=1),
            closes_at=_now + timedelta(hours=5),
            tags=[TAG_BEGINNER],
            shift_events=[
                dataset.CourierShiftEvent({'type': 'started'}),
            ]
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=6),
            closes_at=_now + timedelta(hours=7),
        )

        await shift_2.save(recheck_beginner=True)

        await push_events_cache(shift_2, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'processing', 'статус не поменялся #1')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера на месте #1')
            tap.eq(shift.tags, [TAG_BEGINNER], 'смена - новичок')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не поменялся #2')
            tap.eq(shift.courier_id, courier.courier_id, 'курьера на месте #2')
            tap.eq(shift.tags, [], 'смена все еще не Новичок')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'курьер все еще новичок')
