from argparse import Namespace
from scripts.cron.create_orders import create_orders_periodically as cop


async def test_main(tap, dataset, uuid):
    with tap.plan(9, 'Полный прогон успешный'):
        store = await dataset.store()
        tap.ok(store, 'Склад')
        product = await dataset.product()
        tap.ok(product, 'Продукт создали')
        stock = await dataset.stock(
            store=store,
            product=product,
            count=33,
            lot=uuid(),
            shelf_type='store',
        )
        tap.ok(stock, 'Создали непустой остаток')

        config = {
            'projects': [
                {
                    'project_name': 'best project',
                    'schedule': [{'hour': '*'}],
                    'external_store_ids': [store.external_id],
                    'external_product_ids': [product.external_id],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['store'],
                }
            ]
        }
        stash = await dataset.stash(
            name=cop.CONFIG_STASH_NAME,
            value=config,
        )
        tap.ok(stash, 'Прикопали конфиг')
        async with stash:
            await cop.main(Namespace(validate=False))

        orders = await dataset.Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq(len(orders.list), 1, 'Ордер появился')
        first_order = orders.list[0]
        tap.eq(first_order.status, 'reserving', 'Статус начальный')
        tap.eq(first_order.target, 'complete', 'target завершения')
        tap.eq(
            first_order.vars('project_name', None),
            'best project',
            'Имя проекта в ордере',
        )
        tap.eq(
            {
                (stock.shelf_id, stock.product_id),
            },
            {(req.shelf_id, req.product_id) for req in first_order.required},
            'Реквайред правильный',
        )
