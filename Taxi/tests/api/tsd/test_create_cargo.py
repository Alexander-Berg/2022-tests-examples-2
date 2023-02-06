from stall.model.shelf import Shelf


async def test_link_cargo(tap, api, dataset, push_events_cache, job):
    with tap.plan(25, 'Свяжем груз со стеллажом через ручку'):
        rack = await dataset.rack()
        shelf = await dataset.shelf(type='cargo', store_id=rack.store_id)
        admin = await dataset.user(role='admin', store_id=rack.store_id)

        t = await api(user=admin)

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack.rack_id,
                'barcode': shelf.barcode,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cargo.rack_id', rack.rack_id, 'в ответе стеллаж привязан')

        await push_events_cache(rack, job_method='job_change_rack')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        await shelf.reload()
        tap.eq(shelf.rack_id, rack.rack_id, 'стеллаж пророс')

        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id),
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 1, 'Одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'link_cargo', 'Связывание')
        tap.eq(rack_log.shelf_id, shelf.shelf_id, 'Груз пророс')
        tap.eq(rack_log.delta_reserve, 0, 'Изменение резерва нет')
        tap.eq(rack_log.delta_count, 1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 1, 'Количество новое')
        tap.eq(rack.reserve, 0, 'Резерв')

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack.rack_id,
                'barcode': shelf.barcode,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id),
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 1, 'Все еще одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'link_cargo', 'Связывание')
        tap.eq(rack_log.shelf_id, shelf.shelf_id, 'Груз пророс')
        tap.eq(rack_log.delta_reserve, 0, 'Изменение резерва нет')
        tap.eq(rack_log.delta_count, 1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 1, 'Количество новое')
        tap.eq(rack.reserve, 0, 'Резерв')


async def test_create_create_cargo(tap, api, dataset, uuid,
                                   push_events_cache, job):
    with tap.plan(23, 'Создание груза и привязка к стеллажу'):
        rack = await dataset.rack()
        admin = await dataset.user(role='admin', store_id=rack.store_id)
        barcode = uuid()

        t = await api(user=admin)

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack.rack_id,
                'barcode': barcode,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cargo.rack_id', rack.rack_id, 'в ответе стеллаж привязан')

        await push_events_cache(rack, job_method='job_change_rack')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        shelf = await Shelf.load(
            [admin.store_id, barcode],
            by='barcode',
        )
        tap.eq(shelf.rack_id, rack.rack_id, 'стеллаж пророс')

        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id),
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 1, 'Одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'link_cargo', 'Связывание')
        tap.eq(rack_log.delta_reserve, 0, 'Изменение резерва нет')
        tap.eq(rack_log.delta_count, 1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 1, 'Количество новое')
        tap.eq(rack.reserve, 0, 'Резерв')

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack.rack_id,
                'barcode': barcode,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        rack_logs = (await dataset.RackLog.list(
            by='full',
            conditions=[
                ('store_id', rack.store_id),
                ('rack_id', rack.rack_id),
            ],
            sort=['serial']
        )).list
        tap.eq(len(rack_logs), 1, 'Все еще одна запись в логе')
        rack_log = rack_logs[0]
        tap.eq(rack_log.type, 'link_cargo', 'Связывание')
        tap.eq(rack_log.delta_reserve, 0, 'Изменение резерва нет')
        tap.eq(rack_log.delta_count, 1, 'Изменение количества')
        tap.eq(rack_log.reserve, 0, 'Резерв новый')
        tap.eq(rack_log.count, 1, 'Количество новое')
        tap.eq(rack.reserve, 0, 'Резерв')


async def test_full_rack(tap, api, dataset, uuid):
    with tap.plan(4, 'Привязка к заполненному стеллажу'):
        rack = await dataset.rack(capacity=1)
        shelf = await dataset.shelf(type='cargo', store_id=rack.store_id)
        tap.ok(
            await rack.do_link_cargo_no_order(cargo=shelf),
            'связали стеллаж и груз'
        )

        admin = await dataset.user(role='admin', store_id=rack.store_id)
        barcode = uuid()

        t = await api(user=admin)

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack.rack_id,
                'barcode': barcode,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_linked_cargo(tap, api, dataset):
    with tap.plan(3, 'Пытаемся привязать уже привязанный груз'):
        store = await dataset.store()
        rack1 = await dataset.rack(store_id=store.store_id)
        rack2 = await dataset.rack(store_id=store.store_id)
        shelf = await dataset.shelf(
            type='cargo',
            store_id=store.store_id,
            rack_id=rack1.rack_id,
        )

        admin = await dataset.user(role='admin', store_id=store.store_id)

        t = await api(user=admin)

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack2.rack_id,
                'barcode': shelf.barcode,
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_cargo_at_work(tap, api, dataset):
    with tap.plan(4, 'груз уже в работе с другим ордером'):
        store = await dataset.store()
        order = await dataset.order(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        shelf = await dataset.shelf(
            type='cargo',
            store_id=store.store_id,
            order_id=order.order_id,
        )

        admin = await dataset.user(role='admin', store_id=store.store_id)

        t = await api(user=admin)

        await t.post_ok(
            'api_tsd_create_cargo',
            json={
                'rack_id': rack.rack_id,
                'barcode': shelf.barcode,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Cargo in work now')
