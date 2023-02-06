import pytest


@pytest.mark.parametrize('delivery_check', [True, False])
async def test_cancel_and_reissue(tap, dataset, delivery_check):
    with tap.plan(9, 'Снятие всех смен с перевыставлением'):
        cluster = await dataset.cluster(courier_shift_setup={
            'delivery_type_check_enable': delivery_check,
        })
        store = await dataset.store(cluster=cluster)

        courier = await dataset.courier(
            cluster=cluster,
            delivery_type='foot',
            blocks=[
                {'source': 'wms', 'reason': 'ill'},
            ],
        )

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            delivery_type='foot',
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            delivery_type='car',
        )

        tap.ok(
            await dataset.CourierShift.job_courier_cancel_all(
                courier_id=courier.courier_id,
                reason='ill',
            ),
            'Задание выполнено'
        )

        with await shift1.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'cancelled')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'reissued', 'reissued')

                with await dataset.CourierShift.load(
                        event.detail['courier_shift_id']
                ) as reissued:
                    tap.ok(reissued, 'перевыставленная смена есть')
                    tap.eq(reissued.status, 'request', 'предложена')

        with await shift2.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'cancelled')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'reissued', 'reissued')

                with await dataset.CourierShift.load(
                        event.detail['courier_shift_id']
                ) as reissued:
                    tap.ok(reissued, 'перевыставленная смена есть')
                    tap.eq(reissued.status, 'request', 'предложена')


async def test_retry(tap, dataset):
    with tap.plan(2, 'Повторный запуск не плодит перевыставления'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        courier = await dataset.courier(
            cluster=cluster,
            blocks=[
                {'source': 'wms', 'reason': 'ill'},
            ],
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
        )

        with tap.subtest(5, 'Проверяем исполнение') as _tap:
            _tap.ok(
                await dataset.CourierShift.job_courier_cancel_all(
                    courier_id=courier.courier_id,
                    reason='ill',
                ),
                'Задание выполнено'
            )

            with await shift.reload() as shift:
                _tap.eq(shift.status, 'cancelled', 'cancelled')

                with shift.shift_events[-1] as event:
                    _tap.eq(event.type, 'reissued', 'reissued')

                    with await dataset.CourierShift.load(
                            event.detail['courier_shift_id']
                    ) as reissued:
                        _tap.ok(reissued, 'перевыставленная смена есть')
                        _tap.eq(reissued.status, 'request', 'предложена')

        with tap.subtest(3, 'Проверяем повторный запуск задания') as _tap:
            _tap.ok(
                await dataset.CourierShift.job_courier_cancel_all(
                    courier_id=courier.courier_id,
                    reason='ill',
                ),
                'Задание выполнено'
            )

            with await shift.reload() as shift:
                _tap.eq(shift.status, 'cancelled', 'cancelled')
                _tap.eq(
                    len([
                        x for x in shift.shift_events
                        if x.type == 'reissued'
                    ]),
                    1,
                    'Только одно перевыставление'
                )


@pytest.mark.parametrize('status', ['processing', 'complete', 'cancelled'])
async def test_skip_not_waiting(tap, dataset, status):
    with tap.plan(2, 'Снятие только смен в ожидании'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)

        courier = await dataset.courier(
            cluster=cluster,
            blocks=[
                {'source': 'wms', 'reason': 'ill'},
            ],
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
        )
        old_lsn = shift.lsn

        with tap.subtest(3, 'Проверяем исполнение') as _tap:
            _tap.ok(
                await dataset.CourierShift.job_courier_cancel_all(
                    courier_id=courier.courier_id,
                    reason='ill',
                ),
                'Задание выполнено'
            )

            with await shift.reload() as shift:
                _tap.eq(shift.status, status, 'статус не менялся')
                _tap.eq(shift.lsn, old_lsn, 'смену в принципе не трогали')

        with tap.subtest(3, 'Проверяем повторный запуск задания') as _tap:
            _tap.ok(
                await dataset.CourierShift.job_courier_cancel_all(
                    courier_id=courier.courier_id,
                    reason='ill',
                ),
                'Задание выполнено'
            )

            with await shift.reload() as shift:
                _tap.eq(shift.status, status, 'статус не менялся')
                _tap.eq(shift.lsn, old_lsn, 'смену в принципе не трогали')


async def test_without_cluster(tap, dataset):
    with tap.plan(1, 'Курьер без кластера и у него вызвалась отмена смен'):
        courier = await dataset.courier(
            cluster_id=None,           # без кластера
            delivery_type='foot',
            blocks=[
                {'source': 'wms', 'reason': 'ill'},
            ],
        )
        tap.ok(
            await dataset.CourierShift.job_courier_cancel_all(
                courier_id=courier.courier_id,
                reason='ill',
            ),
            'Задание выполнено'
        )
