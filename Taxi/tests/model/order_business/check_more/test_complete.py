import pytest

from stall.model.stock import Stock
from stall.model.stock_log import StockLog
from stall.model.suggest import Suggest


# pylint: disable=too-many-locals, too-many-statements
@pytest.mark.parametrize(
    'shelf_type, counts',
    [
        (
            'store',
            {
                'count': 22,        # начальное количество
                'done': 22,         # конечное количество
                'found': 0,         # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Одинаковое количество до ордера и после',
            },
        ),
        (
            'store',
            {
                'count': 21,        # начальное количество
                'done': 37,         # конечное количество
                'found': 16,         # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Увеличение количества на полке',
            },
        ),
        (
            'kitchen_components',
            {
                'count': 21,        # начальное количество
                'done': 37,         # конечное количество
                'found': 16,        # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Увеличение количества на полке кухни',
            },
        ),
        (
            'store',
            {
                'count': 21,        # начальное количество
                'done': 37,         # конечное количество
                'found': 16,        # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Уменьшение количества на полке',
            },
        ),
        (
            'kitchen_components',
            {
                'count': 45,        # начальное количество
                'done': 21,         # конечное количество
                'found': 0,         # на полке found
                'lost': 24,          # на полке lost
                'desc': 'Уменьшение количества на полке кухни',
            },
        ),
        (
            'store',
            {
                'count': [10, 12],  # начальное количество
                'done': 22,         # конечное количество
                'found': 0,         # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Одинаковое количество несколькими стоками',
            },
        ),
        (
            'store',
            {
                'count': [10, 12],  # начальное количество
                'done': 227,        # конечное количество
                'found': 205,       # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Несколько стоков - увеличиваем',
            },
        ),
        (
            'store',
            {
                'count': [14, 16],  # начальное количество
                'done': 22,         # конечное количество
                'found': 0,         # на полке found
                'lost': 8,          # на полке lost
                'desc': 'Несколько стоков - уменьшаем',
            },
        ),
        (
            'store',
            {
                'count': [0],       # начальное количество
                'done': 22,         # конечное количество
                'found': 22,         # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Увеличиваем с нуля',
            },
        ),
        (
            'store',
            {
                'count': [],        # начальное количество
                'done': 22,         # конечное количество
                'found': 22,         # на полке found
                'lost': 0,          # на полке lost
                'desc': 'Увеличиваем с пусто',
            },
        ),
        (
            'store',
            {
                'count': [14, 16],  # начальное количество
                'done': 3,          # конечное количество
                'found': 0,         # на полке found
                'lost': 27,         # на полке lost
                'desc': 'Несколько стоков - уменьшается несколько',
            },
        ),
        (
            'store',
            {
                'count': [14, 16],  # начальное количество
                'done': 0,          # конечное количество
                'found': 0,         # на полке found
                'lost': 30,         # на полке lost
                'desc': 'Несколько стоков - уменьшается до нуля',
            },
        ),
    ]
)
async def test_complete(
        tap, dataset, wait_order_status, counts, uuid, shelf_type):
    with tap.plan(20, counts['desc']):
        product = await dataset.product(quants=11)
        tap.ok(product, 'продукт создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')
        await dataset.stock(store=store, product=product, count=0)
        user = await dataset.user(store=store, role='executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        shelf = await dataset.shelf(store=store, type=shelf_type)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.type, shelf_type, 'Обычная')

        if counts['count']:
            with tap.subtest(None, 'Создаём остатки') as taps:
                count = counts['count']
                if isinstance(count, int):
                    count = [count]
                ids = set()
                for c in count:
                    stock = await dataset.stock(count=c,
                                                shelf=shelf,
                                                product=product,
                                                store_id=store.store_id,
                                                valid='1999-12-20',
                                                lot=uuid())
                    taps.eq(stock.store_id, store.store_id, 'остаток создан')
                    taps.eq(stock.reserve, 0, 'резерва нет')
                    taps.eq(stock.count, c, f'количество в остатке {c}')
                    taps.eq(stock.product_id, product.product_id, 'товар')
                    taps.eq(stock.shelf_id, shelf.shelf_id, 'на полке')
                    ids.add(stock.stock_id)
                taps.eq(len(list(ids)),
                        len(count),
                        f'количество стоков итого {len(count)}')
        else:
            tap.passed('продукт создавать не надо')

        order = await dataset.order(
            store=store,
            status='reserving',
            estatus='begin',
            shelves=[shelf.shelf_id],
            type='check_more',
            acks=[user.user_id],
        )

        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.done(target='complete', user=user),
               'ордер завершён')

        with tap.subtest(None, 'Завершаем саджесты') as taps:
            suggests = await Suggest.list_by_order(order)
            taps.isa_ok(suggests, list, 'Саджесты получены')

            if counts['done']:
                for s in suggests:
                    taps.ok(await s.done(product_id=product.product_id,
                                         valid='2021-01-02',
                                         count=counts['done']),
                            f'завершили саджест {s.type}')

                await wait_order_status(order, ('processing', 'waiting'),
                                        tap=taps)

                suggests = await Suggest.list_by_order(order)
                taps.eq(len(suggests), 2, 'появился новый саджест')
                with suggests[-1] as s:
                    taps.eq(s.status, 'request', 'статус')
                    taps.eq(s.type, 'check_more', 'тип')
                    taps.ok(await s.done(status='error'), 'Закрываем его')
            else:
                for s in suggests:
                    taps.ok(await s.done(status='error'),
                            f'завершили саджест {s.type}.error')

        await wait_order_status(order, ('complete', 'change_stocks'))

        tap.note('Повторно пройдем этап резерва (ничего не должно сломаться)')
        order.estatus = 'reserve_all'
        await order.save(store_job_event=False)

        await wait_order_status(order, ('complete', 'done'))

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=shelf_type
        )
        tap.eq(sum(s.count for s in stocks),
               counts['done'],
               'Итоговое количество')
        tap.eq(sum(s.reserve for s in stocks), 0, 'нет резерва')

        lost_stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=(
                'kitchen_lost'
                if shelf_type == 'kitchen_components' else 'lost'
            ),
        )

        tap.eq(sum(s.count for s in lost_stocks),
               counts['lost'],
               'На полке потерь')
        tap.eq(sum(s.reserve for s in lost_stocks), 0, 'нет резерва')

        found_stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=(
                'kitchen_found'
                if shelf_type == 'kitchen_components' else 'found'
            ),
        )

        tap.eq(sum(s.count for s in found_stocks),
               counts['found'],
               'На полке находок')
        tap.eq(sum(s.reserve for s in found_stocks), 0, 'нет резерва')

        # Проверяем полку находок
        if counts['found'] > 0 and counts['lost'] == 0:
            tap.eq(len(found_stocks), 1, 'Длина')
            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'found')],
                by='look',
            )
            tap.eq(len(logs.list), 1, "Создан лог с типом found")

        elif counts['found'] == 0 and counts['lost'] > 0:
            # Проверяем полку потерь
            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'lost')],
                by='look',
            )
            tap.ne(len(logs.list), 0, "Создан лог с типом lost")
            tap.passed('')
        else:
            tap.passed('')
            tap.passed('')


async def test_same_rack(tap, dataset, wait_order_status):
    with tap.plan(6, 'Пересорт на одном стеллаже'):
        product = await dataset.product(quants=1)
        store = await dataset.store()
        lost_shelf = await dataset.shelf(store=store, type='lost')
        found_shelf = await dataset.shelf(store=store, type='found')
        shelf_one = await dataset.shelf(
            title='У-1', rack='общий', store=store)
        shelf_two = await dataset.shelf(
            title='У-2', rack='общий', store=store)
        user = await dataset.user(store=store, role='executer')
        await dataset.stock(shelf=shelf_one, product=product, count=12)

        order = await dataset.order(
            store=store,
            status='reserving',
            estatus='begin',
            shelves=[shelf_one.shelf_id, shelf_two.shelf_id],
            type='check_more',
            acks=[user.user_id],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        with tap.subtest(None, 'Завершаем саджесты') as taps:
            suggests = await Suggest.list_by_order(order)
            taps.isa_ok(suggests, list, 'Саджесты получены')
            for s in suggests:
                taps.ok(
                    await s.done(
                        product_id=product.product_id,
                        valid='2021-01-02',
                        count=5
                    ),
                    f'завершили саджест {s.type}')

            await wait_order_status(
                order,
                ('processing', 'waiting'),
                tap=taps
            )

            suggests = await Suggest.list_by_order(order)
            for suggest in suggests:
                if suggest.status == 'request':
                    tap.ok(
                        await suggest.done(status='error'),
                        'Закрываем саджест полки в ошибку'
                    )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks = (await dataset.Stock.list(
            by='full',
            conditions=['store_id', store.store_id],
            sort=(),
        )).list
        tap.eq(
            {
                (stock.shelf_id, stock.product_id, stock.count)
                for stock in stocks
            },
            {
                (shelf_one.shelf_id, product.product_id, 5),
                (shelf_two.shelf_id, product.product_id, 5),
                (lost_shelf.shelf_id, product.product_id, 7),
                (found_shelf.shelf_id, product.product_id, 5)
            },
            'Остатки пересортились правильно'
        )
