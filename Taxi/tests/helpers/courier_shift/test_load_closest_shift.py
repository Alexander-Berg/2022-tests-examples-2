import datetime

from stall.helpers.courier_shift_h import load_closest_shift


async def test_no_shifts(tap, dataset):
    with tap.plan(1, 'у курьера нет смен'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)

        closest_shift = await load_closest_shift(courier)
        tap.is_ok(closest_shift, None, 'there is no closest shift')


async def test_common(tap, dataset, now):
    with tap.plan(1, 'выбираем ближайшую'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() - datetime.timedelta(hours=2),
            closes_at=now() - datetime.timedelta(hours=1),
            status='complete',
        )
        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() + datetime.timedelta(hours=1),
            closes_at=now() + datetime.timedelta(hours=2),
            status='waiting',
        )
        expected_shift = await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() + datetime.timedelta(minutes=5),
            closes_at=now() + datetime.timedelta(hours=1),
            status='waiting',
        )
        await dataset.courier_shift(
            cluster=cluster, store=store,
            started_at=now() + datetime.timedelta(minutes=1),
            closes_at=now() + datetime.timedelta(hours=1),
            status='request',
        )

        closest_shift = await load_closest_shift(courier)
        tap.eq(closest_shift.courier_shift_id,
               expected_shift.courier_shift_id,
               'closest shift is expected_shift')


async def test_shift_processing(tap, dataset, now):
    with tap.plan(1, 'ближайшая в работе'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        expected_shift = await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() - datetime.timedelta(minutes=5),
            closes_at=now() + datetime.timedelta(hours=1),
            status='processing',
        )
        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() + datetime.timedelta(hours=1),
            closes_at=now() + datetime.timedelta(hours=2),
            status='waiting',
        )

        closest_shift = await load_closest_shift(courier)
        tap.eq(closest_shift.courier_shift_id,
               expected_shift.courier_shift_id,
               'closest shift is expected_shift')


async def test_all_complete(tap, dataset, now):
    with tap.plan(1, 'все смены завершены'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(cluster=cluster)
        store = await dataset.store(cluster=cluster)

        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() - datetime.timedelta(hours=2),
            closes_at=now() - datetime.timedelta(hours=1),
            status='complete',
        )
        await dataset.courier_shift(
            cluster=cluster, courier=courier, store=store,
            started_at=now() - datetime.timedelta(hours=1),
            closes_at=now(),
            status='complete',
        )

        closest_shift = await load_closest_shift(courier)
        tap.is_ok(closest_shift, None, 'all shifts are completed')
