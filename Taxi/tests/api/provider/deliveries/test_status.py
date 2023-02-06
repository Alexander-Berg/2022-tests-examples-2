from datetime import timedelta


async def test_status(tap, dataset, api):
    with tap.plan(5, 'Смена статуса'):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(store=store, provider=provider)
        tap.eq(delivery.status, 'request', 'Поставка создана')

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_provider_deliveries_status',
            json={
                'delivery_id': delivery.delivery_id,
                'status': 'canceled',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('delivery.status', 'canceled')


async def test_status_done(tap, dataset, api):
    with tap.plan(4, 'Смена статуса уже закрытой поставки запрещена'):
        store       = await dataset.store()
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(
            store=store,
            provider=provider,
            status='complete',
        )

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_provider_deliveries_status',
            json={
                'delivery_id': delivery.delivery_id,
                'status': 'canceled',
            }
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')
        t.json_is('message', 'Already done')


async def test_status_slot(tap, dataset, api, job, now):
    with tap.plan(7, 'Удаление слота при отмене'):
        store       = await dataset.store()
        gate        = await dataset.gate(store=store)
        provider    = await dataset.provider(stores=[store.store_id])
        delivery    = await dataset.delivery(
            store=store,
            provider=provider,
            status='request',
        )

        _time1 = now() + timedelta(days=1)
        slot1 = await dataset.gate_slot(
            gate=gate,
            delivery=delivery,
            begin=_time1,
            end=_time1 + timedelta(hours=1),
        )

        _time2 = now() + timedelta(days=1, hours=9)
        slot2 = await dataset.gate_slot(
            gate=gate,
            delivery=delivery,
            begin=_time2,
            end=_time2 + timedelta(hours=1),
        )

        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_provider_deliveries_status',
            json={
                'delivery_id': delivery.delivery_id,
                'status': 'canceled',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('delivery.status', 'canceled')

        tap.ok(await job.call(await job.take()), 'Сброс выполнен')
        tap.ok(not await dataset.GateSlot.load(slot1.gate_slot_id), 'Слота нет')
        tap.ok(not await dataset.GateSlot.load(slot2.gate_slot_id), 'Слота нет')
