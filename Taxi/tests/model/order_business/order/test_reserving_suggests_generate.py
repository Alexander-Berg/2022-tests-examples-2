# pylint: disable=too-many-locals
from collections import defaultdict
from datetime import timedelta
import pytest
from libstall.util import now

from stall.model.suggest import Suggest


async def test_suggests_generate(tap, wait_order_status, dataset):
    with tap.plan(22, 'Генерация саджестов'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, order=1)
        shelf2 = await dataset.shelf(store=store, order=2)

        date1 = (now() + timedelta(days=10)).date()
        date2 = (now() + timedelta(days=20)).date()

        stock1 = await dataset.stock(
            product=product1,
            shelf=shelf1,
            count=5,
            valid=date1,
        )
        await dataset.stock(
            product=product1,
            shelf=shelf1,
            count=6,
            valid=date2,
        )
        await dataset.stock(product=product2, shelf=shelf1, count=20)
        await dataset.stock(product=product3, shelf=shelf2, count=30)

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 7
                },
                {
                    'product_id': product3.product_id,
                    'count': 3
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('reserving', 'suggests_generate'))

        suggest1 = await dataset.suggest(
            order,
            shelf_id=stock1.shelf_id,
            product_id=stock1.product_id,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Какие-то саджесты уже есть')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'suggests_samples_generate',
               'suggests_samples_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'Список саджестов')
        suggests = dict(((x.shelf_id, x.product_id), x) for x in suggests)

        with suggests[shelf1.shelf_id, product1.product_id] as suggest:
            tap.eq(suggest.count, 7, 'count')
            tap.eq(suggest.valid, date1, 'valid')
            tap.eq(suggest.conditions.all, False, 'conditions.all')
            tap.eq(suggest.conditions.editable, False, 'conditions.editable')

        with suggests[shelf1.shelf_id, product2.product_id] as suggest:
            tap.eq(suggest.count, 2, 'count')
            tap.eq(suggest.valid, None, 'valid')
            tap.eq(suggest.conditions.all, False, 'conditions.all')
            tap.eq(suggest.conditions.editable, False, 'conditions.editable')

        with suggests[shelf2.shelf_id, product3.product_id] as suggest:
            tap.eq(suggest.count, 3, 'count')
            tap.eq(suggest.valid, None, 'valid')
            tap.eq(suggest.conditions.all, False, 'conditions.all')
            tap.eq(suggest.conditions.editable, False, 'conditions.editable')


async def test_mark_products(tap, wait_order_status, dataset):
    with tap.plan(22, 'Марочные саджесты'):
        store = await dataset.store(options={'exp_albert_hofmann': True})
        mark_product = await dataset.product(
            vars={'imported': {'true_mark': True}}
        )
        regular_product = await dataset.product()
        item = await dataset.item(store=store)

        shelf1 = await dataset.shelf(store=store, order=1)
        shelf2 = await dataset.shelf(store=store, order=2)
        parcel_shelf = await dataset.shelf(
            store=store, type='parcel', order=3)

        date1 = (now() + timedelta(days=10)).date()
        date2 = (now() + timedelta(days=20)).date()

        await dataset.stock(
            product=mark_product,
            shelf=shelf1,
            count=5,
            valid=date1,
        )
        await dataset.stock(
            product=mark_product,
            shelf=shelf2,
            count=6,
            valid=date2,
        )
        await dataset.stock(product=regular_product, shelf=shelf2, count=20)
        await dataset.stock(item=item, shelf=parcel_shelf, count=1)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': mark_product.product_id,
                    'count': 7
                },
                {
                    'product_id': regular_product.product_id,
                    'count': 3
                },
                {
                    'item_id': item.item_id,
                    'count': 1
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('reserving', 'suggests_generate'))

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'suggests_samples_generate',
               'suggests_samples_generate')
        tap.eq(order.target, 'complete', 'target: complete')
        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 9, 'Список саджестов')

        suggests_by_product_shelf = defaultdict(list)
        for suggest in suggests:
            suggests_by_product_shelf[
                (suggest.product_id, suggest.shelf_id)].append(suggest)

        mark_suggests = suggests_by_product_shelf[
            mark_product.product_id, shelf1.shelf_id]
        tap.eq(len(mark_suggests), 5, '5 саджестов первой полки')
        tap.ok(
            all(suggest.count == 1 for suggest in mark_suggests),
            'Все саджесты с кол-вом 1',
        )
        tap.ok(
            all(
                suggest.conditions.need_true_mark
                for suggest in mark_suggests
            ),
            'Все саджесты с правильным кондишеном'
        )

        mark_suggests = suggests_by_product_shelf[
            mark_product.product_id, shelf2.shelf_id]
        tap.eq(len(mark_suggests), 2, '2 саджеста второй полки')
        tap.ok(
            all(suggest.count == 1 for suggest in mark_suggests),
            'Все саджесты с кол-вом 1',
        )
        tap.ok(
            all(
                suggest.conditions.need_true_mark
                for suggest in mark_suggests
            ),
            'Все саджесты с правильным кондишеном'
        )

        regular_product_suggests = suggests_by_product_shelf[
            regular_product.product_id, shelf2.shelf_id]

        tap.eq(
            len(regular_product_suggests),
            1,
            '1 саджест второго продукта'
        )
        single_suggest = regular_product_suggests[0]
        tap.eq(single_suggest.count, 3, 'Количество верное')
        tap.eq(
            single_suggest.conditions.need_true_mark,
            False,
            'Марка в обычном продукте не появилась',
        )
        item_suggests = suggests_by_product_shelf[
            item.item_id, parcel_shelf.shelf_id]

        tap.eq(len(item_suggests), 1, '1 саджест посылки')
        single_suggest = item_suggests[0]
        tap.eq(single_suggest.count, 1, 'Количество верное')
        tap.eq(
            single_suggest.conditions.need_true_mark,
            False,
            'Марка в посылке не появилась',
        )
        tap.eq(
            order.vars('true_mark_processing', False),
            True,
            'Прикопали меточку обработки марок'
        )
        tap.eq(
            order.vars('true_mark_in_order', False),
            True,
            'Также прикопали метку, что был марочный саджест'
        )


@pytest.mark.parametrize(
    'experiment, interval, expected_suggests, expected_condition',
    [
        (True, 12, 7, True),
        (False, 12, 1, False),
        (False, -12, 7, True),
    ]
)
async def test_mark_config(
        # pylint: disable=too-many-arguments
        tap, dataset, wait_order_status, cfg,
        experiment, interval, expected_suggests, expected_condition
):
    with tap.plan(6, 'Конфиг включения обработки марок'):
        cfg_value = (now() + timedelta(days=interval)).strftime(
            '%Y-%m-%d %H:%M')
        cfg.set('business.store.true_mark_start', cfg_value)
        store = await dataset.store(
            options={'exp_albert_hofmann': experiment})
        mark_product = await dataset.product(
            vars={'imported': {'true_mark': True}}
        )
        await dataset.stock(
            store=store,
            product=mark_product,
            count=7,
        )
        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': mark_product.product_id,
                    'count': 7
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('reserving', 'suggests_generate'))
        await order.business.order_changed()
        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), expected_suggests, 'Список саджестов')
        tap.ok(
            all(
                suggest.conditions.need_true_mark is expected_condition
                for suggest in suggests
            ),
            'Все саджесты с правильным кондишеном'
        )
        tap.eq(
            order.vars('true_mark_processing', False),
            expected_condition,
            'Прикопали меточку обработки марок'
        )
        tap.eq(
            order.vars('true_mark_in_order', False),
            expected_condition,
            'Метка наличия саджеста с маркой'
        )
