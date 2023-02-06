# pylint: disable=too-many-locals
import pytest


async def test_success(tap, dataset, api, make_csv_str, cfg, job):
    with tap.plan(10, 'Успешный сквозной тест импорта'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        shelf_one = await dataset.shelf(type='store', store=store)
        shelf_two = await dataset.shelf(type='store', store=store)
        product = await dataset.product()

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(len(stocks.list), 0, 'Остатков нет')

        t = await api(user=user)
        rows = [
            {
                'shelf': shelf_one.title,
                'product': product.external_id,
                'count': 33,
            },
            {
                'shelf': shelf_two.title,
                'product': product.external_id,
                'count': 12,
            }
        ]

        csv_str = make_csv_str(
            ['product', 'shelf', 'count'],
            rows,
        )
        await t.post_ok(
            'api_admin_stocks_import_data',
            json={'csv': csv_str},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'^\S+$')

        stash_name = f'stocks_import_data-{store.store_id}'

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

        stocks = await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )
        tap.eq(
            {
                (stock.product_id, stock.shelf_id, stock.count)
                for stock in stocks
            },
            {
                (product.product_id, shelf_one.shelf_id, 33),
                (product.product_id, shelf_two.shelf_id, 12)
            },
            'Остатки появились на нужных полках'
        )


@pytest.mark.parametrize('csv_body, expected_code, message', [
    (
        'shelf',
        'ER_BAD_REQUEST',
        'No rows in CSV'
    ),
    (
        '',
        'BAD_REQUEST',
        ''
    ),
    (
        '\n\n',
        'ER_BAD_REQUEST',
        'No rows in CSV'
    ),
    (
        'shelf;product'
        '\nabc;abc'
        '\n',
        'ER_FILE_PARSE',
        'The file format is not as expected'
    ),
    (
        'product;shelf;count\nabc;abc;abc',
        'ER_FILE_PARSE',
        'The file format is not as expected'
    ),
    (
        'product;shelf;count'
        '\nabc;abc;3'
        '\nabc;abc;4',
        'ER_BAD_REQUEST',
        'Duplicate on row #2'
    )
])
async def test_wrong_data(
        tap, dataset, api, cfg, csv_body, expected_code, message):
    with tap.plan(5, 'Неудачный тест ручки импорта (кривой запрос)'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        t = await api(user=user)

        await t.post_ok(
            'api_admin_stocks_import_data',
            json={'csv': csv_body},
        )

        t.status_is(400, diag=True)
        t.json_is('code', expected_code)
        t.json_is('message', message)

        stash_name = f'stocks_import_data-{store.store_id}'
        stash = await dataset.Stash.load(stash_name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')


async def test_wrong_store(tap, dataset, api, cfg, make_csv_str):
    with tap.plan(5, 'Неудачный тест ручки импорта (кривой склад)'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [])
        user = await dataset.user(store=store)
        t = await api(user=user)

        rows = [
            {
                'shelf': 'abc',
                'product': 'bca',
                'count': 33,
            },
            {
                'shelf': 'cde',
                'product': 'feg',
                'count': 12,
            }
        ]

        csv_str = make_csv_str(
            ['product', 'shelf', 'count'],
            rows,
        )

        await t.post_ok(
            'api_admin_stocks_import_data',
            json={'csv': csv_str},
        )

        t.status_is(423, diag=True)
        t.json_is('code', 'ER_LOCKED')
        t.json_is('message', 'Store is not allowed to do this')

        stash_name = f'stocks_import_data-{store.store_id}'
        stash = await dataset.Stash.load(stash_name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')


async def test_wrong_inventory(tap, dataset, api, cfg, make_csv_str):
    with tap.plan(5, 'Неудачный тест ручки импорта (инва уже)'):
        store = await dataset.store(estatus='inventory')
        cfg.set('business.stocks_import.stores_allowed', [store.external_id])
        user = await dataset.user(store=store)
        await dataset.order(
            store_id=store.store_id,
            type='inventory',
            status='processing',
            estatus='waiting'
        )

        t = await api(user=user)

        rows = [
            {
                'shelf': 'abc',
                'product': 'bca',
                'count': 33,
            },
            {
                'shelf': 'cde',
                'product': 'feg',
                'count': 12,
            }
        ]

        csv_str = make_csv_str(
            ['product', 'shelf', 'count'],
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
