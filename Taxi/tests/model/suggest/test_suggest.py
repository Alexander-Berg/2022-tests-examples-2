from datetime import date

from stall.model.suggest import Suggest


async def test_model(tap, dataset):
    with tap.plan(7):
        order = await dataset.order(status='request')
        tap.ok(order, 'Заказ сгенерирован')
        tap.eq(order.status, 'request', 'Статус')
        tap.eq(order.estatus, 'begin', 'Саб-статус')

        shelf = await dataset.shelf(store_id=order.store_id)
        tap.ok(shelf, 'полка создана')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        suggest = Suggest({
            'order_id': order.order_id,
            'store_id': order.store_id,
            'type': 'box2shelf',
            'shelf_id': shelf.shelf_id,
            'product_id': product.product_id,
            'count': 27
        })

        tap.ok(suggest, 'инстанцирован')

        tap.ok(await suggest.save(), 'сохранено')


async def test_vars(tap, dataset):
    with tap.plan(8, 'работа с vars'):
        order = await dataset.order()
        tap.ok(order, 'ордер сгенерирован')

        suggest = await dataset.suggest(order)

        tap.ok(suggest, 'саджест сгенерирован')

        suggest.vars['test'] = 'key'
        tap.ok(await suggest.save(), 'сохранён')
        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.vars, {'test': 'key'}, 'итого')

        del suggest.vars['test']

        tap.ok(await suggest.save(), 'сохранён')
        tap.ok(await suggest.reload(), 'перегружен')
        tap.eq(suggest.vars, {}, 'итого')


async def test_conditions(tap, dataset):
    with tap.plan(6, 'Условия работы'):
        order = await dataset.order()
        tap.ok(order, 'ордер сгенерирован')

        suggest = await dataset.suggest(order, conditions={
            'type': 'and',
            'valid': '2020-01-01',
            'all': True,
        })

        tap.ok(suggest, 'саджест сгенерирован')

        tap.ok(await suggest.save(), 'сохранён')
        tap.ok(await suggest.reload(), 'перегружен')

        tap.eq(suggest.conditions.valid,    date(2020, 1, 1),   'valid')
        tap.eq(suggest.conditions.all,      True,               'all')


async def test_revision(tap, dataset):
    with tap.plan(11, 'Поиск по revision'):
        order = await dataset.order()
        tap.ok(order, 'ордер сгенерирован')
        suggest_no_rev = await dataset.suggest(order)
        suggest_same_rev = await dataset.suggest(order,
                                                 vars={'revision': 1}
                                                 )

        suggest_not_same_rev = await dataset.suggest(order,
                                                     vars={'revision': 0}
                                                     )

        tap.eq(
            suggest_same_rev.revision,
            suggest_same_rev.vars['revision'],
            'саджест с одинаковой ревизией')

        tap.ne(
            suggest_not_same_rev.revision,
            suggest_not_same_rev.vars['revision'],
            'саджест с различной ревизией'
        )

        # поиск по саджестам у которых одинаковая ревизия
        suggests = await Suggest.list_by_order(
            order,
            is_revision_not_change=True,
        )

        suggests_ids = [s.suggest_id for s in suggests]

        tap.ok(suggest_same_rev.suggest_id in suggests_ids,
               'саджест найден при поиске одинаковых ревизий'
               )
        tap.ok(suggest_not_same_rev.suggest_id not in suggests_ids,
               'саджест не найден при поиске одинаковых ревизий'
               )
        tap.ok(suggest_no_rev.suggest_id not in suggests_ids,
               'саджест не найден при поиске одинаковых ревизий'
               )

        suggests = await Suggest.list_by_order(
            order,
            is_revision_not_change=False,
        )

        suggests_ids = [s.suggest_id for s in suggests]

        tap.ok(suggest_same_rev.suggest_id not in suggests_ids,
               'саджест не найден при поиске разных ревизий'
               )
        tap.ok(suggest_not_same_rev.suggest_id in suggests_ids,
               'саджест найден при поиске разных ревизий'
               )
        tap.ok(suggest_no_rev.suggest_id in suggests_ids,
               'саджест найден при поиске одинаковых ревизий'
               )

        # поиск по всем саджестам
        suggests = await Suggest.list_by_order(
            order,
        )
        suggests_ids = [s.suggest_id for s in suggests]

        tap.ok(suggest_same_rev.suggest_id in suggests_ids,
               'саджест найден при не переданом флаге'
               )
        tap.ok(suggest_not_same_rev.suggest_id in suggests_ids,
               'саджест найден при не переданом флаге'
               )


async def test_suggest_list(tap, dataset):
    with tap.plan(1, 'Не передаем в list is_revision_not_change'):
        order = await dataset.order()
        suggest1 = await dataset.suggest(
            order,
            vars={'revision': 0}
        )
        suggest2 = await dataset.suggest(
            order,
            vars={'revision': 1}
        )
        suggests = await Suggest.list(
            by='full',
            conditions=(
                (
                    'suggest_id',
                    [
                        suggest1.suggest_id,
                        suggest2.suggest_id,
                    ]
                ),
            ),
        )
        tap.eq(len(suggests.list), 2, 'Два саджеста')


async def test_list_by_order(tap, dataset):
    with tap.plan(4, 'Саджесты по ордеру'):
        store = await dataset.store()
        stock = await dataset.stock(store=store, count=3)
        order = await dataset.order(
            type='order',
            status='complete',
            store=store,
            required=[
                {'prodcut_id': stock.product_id, 'count': 1},
            ]
        )
        another_order = await dataset.order(store=store)
        suggest_one = await dataset.suggest(
            order,
            product_id=stock.product_id,
        )
        suggest_two = await dataset.suggest(
            order,
            product_id=stock.product_id,
        )
        suggest_three = await dataset.suggest(order)
        await dataset.suggest(another_order)

        suggests_for_order = await Suggest.list_by_order(order)
        tap.eq(len(suggests_for_order), 3, 'Три саджеста на заказ')
        tap.eq(
            {s.suggest_id for s in suggests_for_order},
            {
                suggest_one.suggest_id,
                suggest_two.suggest_id,
                suggest_three.suggest_id,
            },
            'Правильные саджесты заказа'
        )

        suggests_by_product = await Suggest.list_by_order(
            order,
            product_id=suggest_one.product_id,
        )
        tap.eq(len(suggests_by_product), 2, 'Три саджеста на заказ и продукт')
        tap.eq(
            {s.suggest_id for s in suggests_by_product},
            {
                suggest_one.suggest_id,
                suggest_two.suggest_id,
            },
            'Правильные саджесты заказа и продукта'
        )
