import asyncio

from libstall.model import coerces
from stall.helpers.courier_shift_h import list_week_shifts
from stall.model.courier_shift import CourierShiftEvent


async def test_common(tap, dataset):
    with tap.plan(14, 'смены за неделю'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        shifts = await asyncio.gather(
            # суббота
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-18T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-18T14:00:00+00:00'),
                status='complete',
            ),
            # суббота - воскресенье
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-18T23:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-19T04:00:00+00:00'),
                status='complete',
            ),
            # воскресенье
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-19T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-19T16:00:00+00:00'),
                status='complete',
            ),
            # воскресеньше - понедельник
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-19T23:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-20T04:00:00+00:00'),
                status='complete',
            ),
            # понедельник
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-20T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-20T16:00:00+00:00'),
                status='complete',
            ),
            # вторник
            dataset.courier_shift(
                cluster=cluster, courier=courier, store=store,
                started_at=coerces.date_time('2022-06-21T12:00:00+00:00'),
                closes_at=coerces.date_time('2022-06-21T16:00:00+00:00'),
                status='complete',
            ),
        )

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-16T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[0:4]],
               'пред чт (пн-вс): сб+сбвс+вс+вспн')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-16T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[0:2]],
               'пред чт (вс-сб): сб+сбвс')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-18T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[0:4]],
               'сб (пн-вс): сб+сбвс+вс+вспн')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-18T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[0:2]],
               'сб (вс-сб): сб+сбвс')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-19T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[0:4]],
               'вс (пн-вс): сб+сбвс+вс+вспн')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-19T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[1:6]],
               'вс (вс-сб): сбвс+вс+вспн+пн+вт')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-20T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[3:6]],
               'пн (пн-вс): вспн+пн+вт')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-20T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[1:6]],
               'пн (вс-сб): сбвс+вс+вспн+пн+вт')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-24T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[3:6]],
               'пт (пн-вс): вспн+пн+вт')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-24T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[1:6]],
               'пт (вс-сб): сбвс+вс+вспн+пн+вт')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-26T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [it.courier_shift_id for it in shifts[3:6]],
               'след вс (пн-вс): вспн+пн+вт')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-26T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [],
               'след вс (вс-сб): пусто')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-27T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [],
               'след пн (пн-вс): пусто')

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-27T12:00:00+00:00'),
            week_from_sunday=True,
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [],
               'след пн (вс-сб): пусто')


async def test_actual_start(tap, dataset):
    with tap.plan(1, 'фактическое начало в вс'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        shift = await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=coerces.date_time('2022-06-20T00:00:00+00:00'),
            closes_at=coerces.date_time('2022-06-20T05:00:00+00:00'),
            shift_events=[
                CourierShiftEvent({
                    'type': 'started',
                    'created': coerces.date_time('2022-06-19T23:55:00+00:00')
                }),
            ],
            status='complete',
        )

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-19T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [shift.courier_shift_id],
               'вс (пн-вс): смена началась в вс')


async def test_actual_stop(tap, dataset):
    with tap.plan(1, 'фактическое завершение в пн'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        shift = await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=coerces.date_time('2022-06-19T20:55:00+00:00'),
            closes_at=coerces.date_time('2022-06-19T23:55:00+00:00'),
            shift_events=[
                CourierShiftEvent({
                    'type': 'started',
                    'created': coerces.date_time('2022-06-19T20:55:00+00:00')
                }),
                CourierShiftEvent({
                    'type': 'stopped',
                    'created': coerces.date_time('2022-06-20T00:00:00+00:00')
                }),
            ],
            status='complete',
        )

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-20T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [shift.courier_shift_id],
               'пн (пн-вс): смена завершилась в пн')


async def test_foreign_shift(tap, dataset):
    with tap.plan(2, 'показываем только свои смены'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        foreign_courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        shift = await dataset.courier_shift(
            cluster=cluster, courier=foreign_courier, store=store,
            started_at=coerces.date_time('2022-06-20T12:00:00+00:00'),
            closes_at=coerces.date_time('2022-06-20T14:00:00+00:00'),
            status='complete',
        )

        week_shifts = await list_week_shifts(
            courier, coerces.date_time('2022-06-20T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [],
               'для указанного курьера смен нет')

        week_shifts = await list_week_shifts(
            foreign_courier, coerces.date_time('2022-06-20T12:00:00+00:00'),
        )
        tap.eq([it.courier_shift_id for it in week_shifts],
               [shift.courier_shift_id],
               'смены есть у другого курьера')
