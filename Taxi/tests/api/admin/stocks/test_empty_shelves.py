# pylint: disable=too-many-locals
import pytest


async def test_success(tap, dataset, api, make_csv_str, cfg, job):
    with tap.plan(12, 'Успешный сквозной тест удаления'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(type='store', store=store)
        stock_one = await dataset.stock(
            shelf=shelf,
            count=999,
        )
        stock_two = await dataset.stock(
            count=123,
            store=store
        )

        t = await api(user=user)
        rows = [{'shelf': shelf.title}]

        csv_str = make_csv_str(
            ['shelf'],
            rows,
        )
        await t.post_ok(
            'api_admin_stocks_empty_shelves',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'stocks_empty_shelves-{store.store_id}'

        stash = await dataset.Stash.load(stash_name, by='name')

        tap.ok(stash, 'Стэш сохранили')
        tap.eq_ok(
            stash.value('user_id'),
            user.user_id, 'Правильный пользователь'
        )
        tap.eq_ok(
            stash.value('store_id'),
            store.store_id,
            'Правильный склад в стэше'
        )
        tap.ok(stash.value('rows'), rows)

        task = await job.take()
        await job.call(task)

        tap.ok(await stock_one.reload(), 'Перезабрали остаток')
        tap.eq(stock_one.count, 0, 'Остаток удален')

        tap.ok(await stock_two.reload(), 'Перезабрали второй остаток')
        tap.eq(stock_two.count, 123, 'Остаток на месте')


@pytest.mark.parametrize('csv_body, expected_code', [
    ('shelf', 'ER_BAD_REQUEST'),
    ('', 'BAD_REQUEST'),
    ('\n\n', 'ER_BAD_REQUEST'),
])
async def test_wrong_data(
        tap, dataset, api, cfg, csv_body, expected_code):
    with tap.plan(4, 'Неудачный тест ручки удаления (кривой запрос)'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        await dataset.shelf(
            type='store',
            store=store,
            title='Лучший тайтол'
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_stocks_empty_shelves',
            json={'csv': csv_body},
        )

        t.status_is(400, diag=True)
        t.json_is('code', expected_code)

        stash_name = f'stocks_empty_shelves-{store.store_id}'
        stash = await dataset.Stash.load(stash_name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')


async def test_wrong_store(tap, dataset, api, cfg, make_csv_str):
    with tap.plan(5, 'Неудачный тест ручки удаления (кривой склад)'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [])
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(
            type='store',
            store=store,
            title='Лучший тайтол'
        )

        t = await api(user=user)

        rows = [{'shelf': shelf.title}]

        csv_str = make_csv_str(
            ['shelf'],
            rows,
        )

        await t.post_ok(
            'api_admin_stocks_empty_shelves',
            json={'csv': csv_str},
        )

        t.status_is(423, diag=True)
        t.json_is('code', 'ER_LOCKED')
        t.json_is('message', 'Store is not allowed to do this')

        stash_name = f'stocks_empty_shelves-{store.store_id}'
        stash = await dataset.Stash.load(stash_name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')


async def test_wrong_inventory(tap, dataset, api, cfg, make_csv_str):
    with tap.plan(5, 'Неудачный тест ручки удаления (инва уже)'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf = await dataset.shelf(
            type='store',
            store=store,
            title='Лучший тайтол'
        )

        await dataset.order(
            store_id=store.store_id,
            type='inventory',
            status='processing',
            estatus='waiting'
        )

        t = await api(user=user)

        rows = [{'shelf': shelf.title}]

        csv_str = make_csv_str(
            ['shelf'],
            rows,
        )

        await t.post_ok(
            'api_admin_stocks_empty_shelves',
            json={'csv': csv_str},
        )

        t.status_is(423, diag=True)
        t.json_is('code', 'ER_INVENTORY_EXISTS')
        t.json_is('message', 'order.inventory has already exists')

        stash_name = f'stocks_empty_shelves-{store.store_id}'
        stash = await dataset.Stash.load(stash_name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')
