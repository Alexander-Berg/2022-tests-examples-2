async def test_assets_writeoff(tap, dataset, api, uuid):
    with tap.plan(7, 'Создание ордера на списание запчастей'):
        store = await dataset.store()
        user = await dataset.user(store_id=store.store_id,
                                  role='executer')
        product = await dataset.product()
        task = await dataset.repair_task(store=store)

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_assets_writeoff',
            json={
                'external_id': external_id,
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
                'required': [
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(200, diag=True)

        order = await dataset.Order.load(
            [user.store_id, external_id],
            by='external'
        )
        tap.ok(order, 'ордер создан')
        t.json_is('order.order_id', order.order_id,
                  'Ручка отдала верный ID ордера')

        await t.post_ok(
            'api_tsd_order_assets_writeoff',
            json={
                'external_id': external_id,
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
                'required': [
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)


async def test_no_products(tap, dataset, api, uuid):
    with tap.plan(4, 'Нельзя создать ордер без продуктов'):
        store = await dataset.store()
        user = await dataset.user(store_id=store.store_id,
                                  role='executer')
        task = await dataset.repair_task()

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_assets_writeoff',
            json={
                'external_id': external_id,
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
                'required': []
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details.message', 'No products')


async def test_another_store(tap, dataset, api, uuid):
    with tap.plan(4, 'Нельзя создать ордер по заявке другого склада'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store_id=store.store_id,
                                  role='executer')
        another_store = await dataset.store()
        task = await dataset.repair_task(store=another_store)

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_assets_writeoff',
            json={
                'external_id': external_id,
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
                'required': [
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('details.message', 'Repair task from another store')


async def test_not_in_progress(tap, dataset, api, uuid):
    with tap.plan(4,
                  'Нельзя создать ордер по заявке не в статусе IN_PROGRESS'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store_id=store.store_id,
                                  role='executer')
        task = await dataset.repair_task(store=store, status='NEW')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_assets_writeoff',
            json={
                'external_id': external_id,
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
                'required': [
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('details.message', 'Repair task is not in progress')


async def test_not_repair(tap, dataset, api, uuid):
    with tap.plan(4,
                  'Нельзя создать ордер по заявке типа отличного от REPAIR'):
        product = await dataset.product()
        store = await dataset.store()
        user = await dataset.user(store_id=store.store_id,
                                  role='executer')
        task = await dataset.repair_task(store=store, status='IN_PROGRESS',
                                         vars={'lavkach_type': 'NEW'})

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_tsd_order_assets_writeoff',
            json={
                'external_id': external_id,
                'repair_task_external_id': task.external_id,
                'repair_task_source': task.source,
                'required': [
                    {'product_id': product.product_id, 'count': 27},
                ]
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('details.message', 'Task in Lavkach is not of type REPAIR')
