from datetime import timedelta
from libstall.util import tzone
from scripts.cron.create_orders import create_orders_periodically as cop


async def test_processing(tap, dataset, uuid):
    with tap.plan(21, 'Обработка конфига успешная'):
        store = await dataset.store()
        tap.ok(store, 'Склад')
        product = await dataset.product()
        tap.ok(product, 'Продукт создали')

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
        parsed_config = await cop.parse_and_validate_config(config)
        tap.eq(len(parsed_config), 1, 'Один склад')
        tap.ok(len(parsed_config[0]['projects']), 1, 'Один проект')

        tap.note('Обработаем конфиг')
        await cop.config_processing(parsed_config)

        orders = await dataset.Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq(len(orders.list), 0, 'Не было остатков, нет и ордера')

        empty_stock = await dataset.stock(
            store=store,
            product=product,
            count=0,
            lot=uuid(),
            shelf_type='store',
        )
        tap.ok(empty_stock, 'Создали пустой остаток')

        stock = await dataset.stock(
            store=store,
            product=product,
            count=33,
            lot=uuid(),
            shelf_type='store',
        )
        tap.ok(stock, 'Создали непустой остаток')

        another_type_stock = await dataset.stock(
            store=store,
            product=product,
            shelf_type='markdown',
        )
        tap.ok(another_type_stock, 'Не из проекта тип полки')

        tap.note('Обработаем конфиг')
        await cop.config_processing(parsed_config)

        orders = await dataset.Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq(len(orders.list), 1, 'Появился ордер')
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
                (empty_stock.shelf_id, empty_stock.product_id),
            },
            {(req.shelf_id, req.product_id) for req in first_order.required},
            'Реквайред правильный',
        )

        tap.note('Обработаем конфиг еще раз')
        await cop.config_processing(parsed_config)

        orders = await dataset.Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq(len(orders.list), 1, 'Один ордер')
        tap.eq(orders.list[0].order_id, first_order.order_id, 'Старый ордер')

        first_order.created = first_order.created - timedelta(days=3)
        tap.ok(await first_order.save(), 'Обновили дату создания ордера')

        new_stock = await dataset.stock(
            store=store,
            product=product,
            count=3,
            lot=uuid(),
            shelf_type='store',
        )
        tap.ok(new_stock, 'Новый остаток появился по пути')

        tap.note('Обработаем конфиг еще разочек')
        await cop.config_processing(parsed_config)

        orders = await dataset.Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq(len(orders.list), 2, 'Два ордера')
        await first_order.reload()
        tap.eq(first_order.target, 'canceled', 'Отменили старый ордер')

        new_order = next(
            order for order in orders
            if order.order_id != first_order.order_id
        )
        tap.eq(
            new_order.vars('project_name', None),
            'best project',
            'Имя проекта в ордере'
        )
        tap.eq(
            {
                (stock.shelf_id, product.product_id),
                (empty_stock.shelf_id, product.product_id),
                (new_stock.shelf_id, product.product_id)
            },
            {(req.shelf_id, req.product_id) for req in new_order.required},
            'Реквайред правильный',
        )


async def test_store_specific(tap, dataset, now):
    with tap.plan(11, 'Складские настройки влияют на ордера'):
        store_mow = await dataset.store(tz='Europe/Moscow')
        tap.ok(store_mow, 'Склад москва')

        store_utc = await dataset.store(tz='UTC')
        tap.ok(store_utc, 'Склад UTC')

        store_inactive = await dataset.store(
            tz='Europe/Moscow',
            status='closed'
        )
        tap.ok(store_inactive, 'Выключенный склад')

        store_inventory = await dataset.store(
            tz='Europe/Moscow',
            status='active',
            estatus='inventory'
        )
        tap.ok(store_inventory, 'Склад с инвой')

        product = await dataset.product()
        tap.ok(product, 'Продукт создали')

        for store in (store_utc, store_mow, store_inactive):
            stock = await dataset.stock(
                store=store,
                product=product,
                count=3,
                shelf_type='store',
            )
            tap.ok(stock, f'Новый остаток на складе {store.tz}')

        current_mow_time = now().astimezone(tz=tzone('Europe/Moscow'))
        current_hour = current_mow_time.hour

        config = {
            'projects': [
                {
                    'project_name': 'best project',
                    'schedule': [
                        {'hour': current_hour},
                        {'hour': (current_hour + 1) % 24}
                    ],
                    'external_store_ids': [
                        store_mow.external_id,
                        store_utc.external_id,
                        store_inactive.external_id,
                        store_inventory.external_id,
                    ],
                    'external_product_ids': [product.external_id],
                    'order_type': 'check_product_on_shelf',
                    'shelf_types': ['store'],
                }
            ]
        }
        parsed_config = await cop.parse_and_validate_config(config)
        tap.ok(parsed_config, 'Конфиг спарсили')

        tap.note('Обработаем конфиг')
        await cop.config_processing(parsed_config)

        orders = await dataset.Order.list(
            by='full',
            conditions=[
                ('store_id', [
                    store.store_id
                    for store in (
                        store_utc,
                        store_mow,
                        store_inactive,
                        store_inventory
                    )
                ]),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq(len(orders.list), 1, 'Один ордер')
        tap.eq(
            orders.list[0].store_id,
            store_mow.store_id,
            'Ордер был создан только на MOW активном складе'
        )
