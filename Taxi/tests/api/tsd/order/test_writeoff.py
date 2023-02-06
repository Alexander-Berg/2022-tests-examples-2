import pytest


@pytest.mark.parametrize('role', ['executer'])
async def test_writeoff(tap, dataset, api, role, uuid):
    with tap.plan(15, 'Создание ордера списания'):
        store = await dataset.store()

        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад у него есть')

        products = [await dataset.product() for _ in range(3)]
        tap.ok(products, 'продукты сгенерированы')

        shelves = [await dataset.shelf(store_id=user.store_id, type='trash')
                   for _ in range(3)]
        tap.ok(shelves, 'полки сгенерированы')

        stocks = [
            await dataset.stock(shelf=s, product=p, count=521)
            for s in shelves
            for p in products
        ]

        tap.eq(len(stocks), 9, 'Сгенерированы остатки')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_writeoff',
                        json={
                            'order_id': external_id,
                            'check': {
                                'shelves': [s.shelf_id for s in shelves],
                            }
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'writeoff')
        t.json_is('order.shelves', [s.shelf_id for s in shelves])
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)
        t.json_is('order.source', 'tsd')


@pytest.mark.parametrize('role', ['executer'])
async def test_writeoff_all(tap, dataset, api, role, uuid):
    with tap.plan(14, 'Создание ордера списания'):
        store = await dataset.store()

        user = await dataset.user(role=role, store=store)
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад у него есть')

        products = [await dataset.product() for _ in range(3)]
        tap.ok(products, 'продукты сгенерированы')

        shelves = [await dataset.shelf(store_id=user.store_id, type='trash')
                   for _ in range(3)]
        tap.ok(shelves, 'полки сгенерированы')

        stocks = [
            await dataset.stock(shelf=s, product=p, count=521)
            for s in shelves
            for p in products
        ]

        tap.eq(len(stocks), 9, 'Сгенерированы остатки')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_writeoff',
                        json={
                            'order_id': external_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.type', 'writeoff')
        t.json_is('order.shelves', [])
        t.json_is('order.user_id', user.user_id)
        t.json_is('order.store_id', store.store_id)
        t.json_is('order.company_id', store.company_id)


@pytest.mark.parametrize('role', ['barcode_executer'])
async def test_writeoff_deny(tap, dataset, api, role, uuid):
    with tap.plan(9, 'Создание ордера списания'):
        user = await dataset.user(role=role)
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад у него есть')

        products = [await dataset.product() for _ in range(3)]
        tap.ok(products, 'продукты сгенерированы')

        shelves = [await dataset.shelf(store_id=user.store_id, type='trash')
                   for _ in range(3)]
        tap.ok(shelves, 'полки сгенерированы')

        stocks = [
            await dataset.stock(shelf=s, product=p, count=521)
            for s in shelves
            for p in products
        ]

        tap.eq(len(stocks), 9, 'Сгенерированы остатки')

        t = await api(user=user)
        external_id = uuid()

        await t.post_ok('api_tsd_order_writeoff',
                        json={
                            'order_id': external_id,
                        })
        t.status_is(403, diag=True, desc='Запрещено создание writeoff')
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


async def test_wrong_store_estatus(tap, dataset, api, uuid):
    with tap.plan(3, 'Склад в неправильном статусе'):
        store = await dataset.full_store(estatus='inventory')
        user = await dataset.user(role='executer', store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_writeoff',
            json={
                'order_id': uuid(),
            })
        t.status_is(423, diag=True)
        t.json_is('code', 'ER_STORE_MODE')
