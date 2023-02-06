from datetime import timedelta

from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_drop_shifts(tap, dataset, push_events_cache, job):
    with tap.plan(10, 'При изменении типа доставки сбрасываем смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
        )

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            delivery_type='foot',
            status='waiting',
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            delivery_type='car',
            status='waiting',
        )

        courier.delivery_type = 'car'
        tap.ok(await courier.save(), 'Сохранили новый тип доставки')

        await push_events_cache(
            courier,
            job_method='job_courier_cancel_all',
        )
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'cancelled')

            with shift.shift_events[-2] as event:
                tap.eq(event.type, 'cancelled', 'cancelled')
                tap.eq(event.detail['reason'], 'wrong_delivery_type', 'причина')
                tap.eq(event.detail['source'], 'wms', 'источник')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'reissued', 'reissued')

                with await dataset.CourierShift.load(
                        event.detail['courier_shift_id']
                ) as reissued:
                    tap.ok(reissued, 'перевыставленная смена есть')
                    tap.eq(reissued.status, 'request', 'предложена')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'Своего типа не тронули')


async def test_ignore_delivery_type(tap, dataset, push_events_cache, job):
    with tap.plan(6, 'НЕ сбрасываем смены при выкл.проверке "тип доставки"'):
        cluster = await dataset.cluster(courier_shift_setup={
            'delivery_type_check_enable': False,
        })
        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
        )
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            delivery_type='foot',
            status='waiting',
        )
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            delivery_type='car',
            status='waiting',
        )

        courier.delivery_type = 'rover'
        tap.ok(await courier.save(), 'Сохранили новый тип доставки')

        await push_events_cache(
            courier,
            job_method='job_courier_cancel_all',
        )
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'waiting', 'смена не снята')

        with await shift_2.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'waiting', 'смена не снята')


async def test_beginner_drop_shifts(tap, dataset, now, push_events_cache, job):
    with tap.plan(10, 'Новичок теряет свои смены'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            tags=[TAG_BEGINNER],
        )

        _now = now().replace(microsecond=0)
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            delivery_type='foot',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
            tags=[TAG_BEGINNER],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            delivery_type='foot',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
            tags=[],
        )

        courier.delivery_type = 'car'
        tap.ok(await courier.save(), 'Сохранили новый тип доставки')

        # отмена смен
        await push_events_cache(courier, job_method='job_courier_cancel_all')
        tap.ok(await job.call(await job.take()), 'Задание №1 выполнено')

        # пересчет новичков
        await push_events_cache(shift_1, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание №2 выполнено')

        # смены отменились; новой смены-новичка нет, т.к. смен нет в целом
        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'cancelled')
            tap.eq(shift.tags, [TAG_BEGINNER], 'тег остался на смене')

        with await shift_2.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'cancelled')
            tap.eq(shift.tags, [], 'тег не назначался')

        # на курьера назначили смены с нужным типом доставки (или сам взял)
        shift_1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            delivery_type='car',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
            tags=[],
        )
        shift_2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            delivery_type='car',
            started_at=_now + timedelta(hours=3),
            closes_at=_now + timedelta(hours=5),
            tags=[],
        )

        # пересчет новичков
        await shift_2.save(recheck_beginner=True)
        await push_events_cache(shift_2, job_method='job_recheck_beginner')
        tap.ok(await job.call(await job.take()), 'Задание №3 выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.tags, [TAG_BEGINNER], 'тег назначен')

        with await shift_2.reload() as shift:
            tap.eq(shift.tags, [], 'тег не назначен')
