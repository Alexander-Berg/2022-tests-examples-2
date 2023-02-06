import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok('api_admin_shelves_load',
                        json={'shelf_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа к не нашим полкам')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(7):
        store = await dataset.store()

        shelf = await dataset.shelf(store=store)
        tap.ok(shelf, 'полка сгенерирована')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_shelves_load',
                        json={'shelf_id': shelf.shelf_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'полка получена')

        t.json_is('shelf.shelf_id', shelf.shelf_id, 'идентификатор полки')
        t.json_is('shelf.title', shelf.title, 'название')
        t.json_is('shelf.rack', shelf.rack, 'стелаж')


async def test_over_permit_out_store(tap, api, dataset):
    with tap.plan(3, 'Чужая лавка недоступна'):
        company = await dataset.company()
        store1 = await dataset.store(company=company)
        store2 = await dataset.store(company=company)
        shelf = await dataset.shelf(store=store1)

        user = await dataset.user(role='admin', store=store2)
        t = await api(user=user)
        await t.post_ok('api_admin_shelves_load',
                        json={'shelf_id': shelf.shelf_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_over_permit_out_company(tap, api, dataset):
    with tap.plan(3, 'Чужая компания недоступна'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)
        shelf = await dataset.shelf(store=store1)

        user = await dataset.user(role='admin', store=store2)
        t = await api(user=user)
        await t.post_ok('api_admin_shelves_load',
                        json={'shelf_id': shelf.shelf_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store)

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_load',
            json={'shelf_id': [shelf1.shelf_id,
                               shelf2.shelf_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('shelf', 'есть в выдаче')
        res = t.res['json']['shelf']
        tap.eq_ok(
            sorted([res[0]['shelf_id'], res[1]['shelf_id']]),
            sorted([shelf1.shelf_id,
                    shelf2.shelf_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['executer', 'barcode_executer',
                                  'expansioner', 'category_manager'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)

        user = await dataset.user(role=role, store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_load',
            json={'shelf_id': [shelf.shelf_id,
                               uuid()]})
        t.status_is(403, diag=True)


async def test_load_multiple_store(tap, api, dataset):
    with tap.plan(5):
        store = await dataset.store()
        shelf1 = await dataset.shelf(store_id=store.store_id)
        user = await dataset.user(store=store, role='store_admin')
        t = await api()
        t.set_user(user)
        await t.post_ok(
            'api_admin_shelves_load',
            json={'shelf_id': [shelf1.shelf_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('shelf', 'есть в выдаче')
        res = t.res['json']['shelf']
        tap.eq_ok(
            res[0]['shelf_id'],
            shelf1.shelf_id,
            'Пришли правильные объекты'
        )
