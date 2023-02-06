async def test_log(tap, dataset):
    with tap.plan(18, 'Проверяем запись лога'):
        store       = await dataset.store()
        provider    = await dataset.provider()

        delivery    = await dataset.delivery(
            store=store,
            provider=provider,
            status='request',
        )

        logs = await dataset.DeliveryLog.list_by_delivery(delivery.delivery_id)
        tap.eq(len(logs), 1, 'Лог получен')

        with logs[0] as log:
            tap.eq(log.delivery_id, delivery.delivery_id,   'delivery_id')
            tap.eq(log.provider_id, provider.provider_id,   'provider_id')
            tap.eq(log.store_id,    store.store_id,         'store_id')
            tap.eq(log.status, 'request', 'request')
            tap.ok(log.created, 'created')
            tap.ok(log.lsn, 'lsn')

        tap.note('Сохранение без смены статуса')
        with delivery:
            tap.ok(await delivery.save(), 'Пересохранили')
            tap.eq(delivery.status, 'request', 'Статус не менялся')
            logs = await dataset.DeliveryLog.list_by_delivery(
                delivery.delivery_id)
            tap.eq(len(logs), 1, 'Лог не менялся')

        tap.note('Сохранение со сменой статуса')
        with delivery:
            tap.ok(await delivery.change_status('processing'), 'processing')
            tap.eq(delivery.status, 'processing', 'Статус менялся')
            logs = await dataset.DeliveryLog.list_by_delivery(
                delivery.delivery_id)
            tap.eq(len(logs), 2, 'Лог добавлен')

            with logs[1] as log:
                tap.eq(log.delivery_id, delivery.delivery_id,   'delivery_id')
                tap.eq(log.provider_id, provider.provider_id,   'provider_id')
                tap.eq(log.store_id,    store.store_id,         'store_id')
                tap.eq(log.status, 'processing', 'processing')
                tap.ok(log.created, 'created')
