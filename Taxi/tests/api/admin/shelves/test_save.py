import pytest

from stall.model.shelf import (
    Shelf, SHELF_TYPES_TECH, SHELF_TYPES_KITCHEN_TECH, SHELF_WH_GROUPS
)


async def test_save_exists(tap, dataset, api):
    with tap.plan(20, 'Полка без стоков'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store, title='медвед')
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'на складе')
        tap.eq(shelf.title, 'медвед', 'название полки')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'title': 'привет',
                            'status': 'disabled',
                            'type': 'incoming',
                            'width': 100,
                            'height': 50,
                            'depth': 70,
                            'warehouse_group': SHELF_WH_GROUPS[0],
                            'external_id': shelf.external_id,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('shelf.updated', 'updated')
        t.json_has('shelf.created', 'created')
        t.json_is('shelf.order', shelf.order, 'order')
        t.json_is('shelf.title', 'привет', 'title')
        t.json_is('shelf.status', 'disabled', 'status')
        t.json_is('shelf.type', 'incoming', 'type')
        t.json_is('shelf.barcode', shelf.barcode, 'barcode валидный')
        t.json_is('shelf.width', 100)
        t.json_is('shelf.height', 50)
        t.json_is('shelf.depth', 70)
        t.json_is(
            'shelf.warehouse_group',
            SHELF_WH_GROUPS[0],
            'Верный warehouse_group',
        )


async def test_save_unexists(tap, dataset, api, uuid):
    with tap.plan(13):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        external_id = uuid()

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'external_id': external_id,
                            'title': 'привет'
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('shelf.updated', 'updated')
        t.json_has('shelf.created', 'created')
        t.json_is('shelf.title', 'привет', 'title')
        t.json_is('shelf.external_id', external_id, 'идентификатор')
        t.json_has('shelf.barcode', 'штрихкод назначен')
        t.json_is('shelf.status', 'active', 'статус "активный"')
        t.json_is('shelf.user_id', user.user_id)


async def test_save_barcode(tap, dataset, api):
    with tap.plan(15):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store, title='медвед')
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'на складе')
        tap.eq(shelf.title, 'медвед', 'название полки')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api(user=user)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'title': 'привет',
                            'change_barcode': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('shelf.updated', 'updated')
        t.json_has('shelf.created', 'created')
        t.json_is('shelf.order', shelf.order, 'order')
        t.json_is('shelf.title', 'привет', 'title')
        t.json_isnt('shelf.barcode', None, 'barcode не пустой')
        t.json_isnt('shelf.barcode', shelf.barcode, 'barcode изменен')


@pytest.mark.parametrize('role', ['store_admin'])
async def test_save_prohibited(tap, dataset, api, role):
    with tap.plan(3):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, title='медвед')

        t = await api(role=role)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'title': 'привет',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_save_user_id(tap, dataset, api):
    with tap.plan(4, 'изменение user_id'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, title='медвед')

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'title': 'привет',
                            'user_id': 'hello',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('shelf.user_id', 'hello')


async def test_change_external_id(tap, dataset, api, uuid):
    with tap.plan(6, 'изменение external_id'):
        store = await dataset.store()
        external_id_one = uuid()
        external_id_two = uuid()
        shelf = await dataset.shelf(
            store=store,
            title='медвед',
            external_id=external_id_one,
        )

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'shelf_id': shelf.shelf_id,
                'title': 'привет',
                'external_id': external_id_two,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        tap.ok(await shelf.reload(), 'Перезабрали полку')
        tap.eq(shelf.title, 'медвед', 'Заголовок прежний')
        tap.eq(shelf.external_id, external_id_one, 'external прежний')


async def test_title_duplicate(tap, dataset, api, uuid):
    with tap.plan(12, 'Дубли в имени'):
        store = await dataset.store()
        shelf = await dataset.shelf(
            store=store,
            title='медвед',
        )

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        tap.note('Создание полки')
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'title': 'медвед',
                'external_id': uuid(),
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Title duplicated')

        store_shelves = await shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(store_shelves), 1, 'Все та же полка')

        another_shelf = await dataset.shelf(
            store=store,
            title='превед',
        )
        tap.note('Обновление полки')
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'shelf_id': another_shelf.shelf_id,
                'title': 'медвед',
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Title duplicated')

        store_shelves = await shelf.list_by_store(store_id=store.store_id)
        tap.eq(len(store_shelves), 2, 'Две старые полки')
        tap.ok(await another_shelf.reload(), 'Перезабрали полку')
        tap.eq(another_shelf.title, 'превед', 'Заголовок не изменился')


async def test_save_check_shelves(tap, dataset, api, job, push_events_cache):
    with tap.plan(26, 'проверяем выполнение check_shelves при сохранении'):
        store = await dataset.store(status='active')
        user = await dataset.user(role='admin', store=store)
        kshelf = await dataset.shelf(
            store=store, type='kitchen_components', status='disabled'
        )

        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t not in shelf_types, f'нет полки {t}')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'shelf_id': kshelf.shelf_id,
                'status': 'active',
            },
        )
        t.status_is(200)

        await push_events_cache(kshelf, job_method='job_store_check_errors')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')
        shelves = await Shelf.list_by_store(store_id=store.store_id)
        shelf_types = {s.type for s in shelves}
        for t in SHELF_TYPES_TECH + SHELF_TYPES_KITCHEN_TECH:
            tap.ok(t in shelf_types, f'есть полка {t}')

        kfound = [s for s in shelves if s.type == 'kitchen_found'][0]
        t = await api(user=user)
        await t.post_ok(
            'api_admin_shelves_save',
            json={
                'shelf_id': kfound.shelf_id,
                'status': 'disabled',
            },
        )
        t.status_is(200)
        await kfound.reload()
        tap.eq(kfound.status, 'disabled', 'выключили полку')
        await push_events_cache(kfound, job_method='job_store_check_errors')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')
        await kfound.reload()
        tap.eq(kfound.status, 'active', 'включили полку')


@pytest.mark.parametrize(
    'changes',
    [{'type': 'incoming'}, {'status': 'removed'}, {'tags': ['freezer']}]
)
async def test_has_stocks_conflict(tap, dataset, api, changes):
    with tap.plan(3, 'Не изменяются тип и статус полки со стоками'):
        store = await dataset.store()

        shelf = await dataset.shelf(store=store, title='медвед')
        await dataset.stock(
            store=store, shelf_id=shelf.shelf_id, count=1)

        user = await dataset.user(store=store, role='admin')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'external_id': shelf.external_id,
                            **changes
                        })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_status_empty_stock_ok(tap, dataset, api):
    with tap.plan(4, 'Изменяется статус полки с нулевыми стоками'):
        store = await dataset.store()

        shelf = await dataset.shelf(store=store, title='медвед')
        await dataset.stock(
            store=store, shelf_id=shelf.shelf_id, count=0)

        user = await dataset.user(store=store, role='admin')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'external_id': shelf.external_id,
                            'status': 'removed',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('shelf.status', 'removed', 'status')


@pytest.mark.parametrize(
    'changes',
    [{}, {'status': 'removed'}]
)
async def test_type_dur_stowage(tap, dataset, api, changes):
    with tap.plan(3, 'Не изменяется статус во время раскладки'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, title='медвед')
        user = await dataset.user(store=store, role='admin')

        await dataset.order(store=store, type='stowage')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
            json={
                'shelf_id':    shelf.shelf_id,
                'external_id': shelf.external_id,
                **changes
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_order_on_shelf(tap, dataset, api):
    with tap.plan(
        3, 'Не изменяется тип и статус, если на полку создан документ'
    ):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, title='медвед')
        user = await dataset.user(store=store, role='admin')

        await dataset.order(
            store=store,
            type='check_product_on_shelf',
            shelves=[shelf.shelf_id],
            status='reserving',
            estatus='begin',
        )

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
            json={
                'shelf_id':    shelf.shelf_id,
                'external_id': shelf.external_id,
                'status': 'removed'
            })
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_complete_stowage(tap, dataset, api):
    with tap.plan(4, 'Изменяется тип при завершенной раскладке'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, title='медвед')
        user = await dataset.user(store=store, role='admin')

        await dataset.order(
            store=store,
            type='stowage',
            status='complete',
            estatus='done'
        )

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'external_id': shelf.external_id,
                            'type': 'incoming',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('shelf.type', 'incoming', 'type')


async def test_force_save(tap, dataset, api):
    with tap.plan(4, 'force_save изменяет тип во время раскладки'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, title='медвед')
        user = await dataset.user(store=store, role='admin')

        await dataset.order(store=store, type='stowage')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_shelves_save',
                        json={
                            'shelf_id': shelf.shelf_id,
                            'external_id': shelf.external_id,
                            'type': 'incoming',
                            'force_save': True
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('shelf.type', 'incoming', 'type')
