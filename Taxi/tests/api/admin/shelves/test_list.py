from random import randrange as rnd

async def test_list_empty(api, dataset, tap):
    with tap.plan(7):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_is('shelves', [], 'shelves is empty')


async def test_list_nonempty(api, dataset, tap):
    with tap.plan(17):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        orders = set()
        while len(orders) < 5:
            orders.add(rnd(100))

        shelves = [ await dataset.shelf(store=store, order=x)
                    for x in orders ]
        tap.ok(shelves, 'полки созданы')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('shelves', 'полки в выдаче')

        shelves.sort(key=lambda x: x.order)

        prev = None
        for i, shelf in enumerate(shelves):
            t.json_is(f'shelves.{i}.shelf_id',
                      shelf.shelf_id,
                      f'Полка {i}: {shelf.order}')
            if prev is not None:
                tap.ok(shelf.order > prev, 'порядок полки в выдаче')
            prev = shelf.order


async def test_list_ids(api, dataset, tap):
    with tap.plan(15):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        orders = set()
        while len(orders) < 5:
            orders.add(rnd(100))

        shelves = [ await dataset.shelf(store=store, order=x)
                    for x in orders ]
        tap.ok(shelves, 'полки созданы')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_list',
                        json={'shelf_ids': [ shelves[1].shelf_id ]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('shelves', 'полки в выдаче')

        t.json_hasnt('shelves.1')
        t.json_is('shelves.0.shelf_id', shelves[1].shelf_id)

        await t.post_ok('api_admin_shelves_list',
                        json={'shelf_ids': []},
                        desc='пустой список в запросе')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('shelves', 'полки в выдаче')
        t.json_hasnt('shelves.0')
