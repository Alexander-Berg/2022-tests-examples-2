from stall.model.order import Order


# pylint: disable=too-many-locals,too-many-statements
async def test_create(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(76):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        stock_product = await dataset.stock(
            product=product,
            store=store,
            count=27
        )
        tap.eq(stock_product.store_id, store.store_id, 'остаток товар')
        tap.eq(stock_product.product_id, product.product_id, 'product_id')
        tap.eq(stock_product.left, 27, 'количество')
        stock_item = await dataset.stock(
            item=item,
            store=store,
            count=1
        )
        tap.eq(stock_item.store_id, store.store_id, 'остаток экземпляр')
        tap.eq(stock_item.product_id, item.item_id, 'product_id')
        tap.eq(stock_item.left, 1, 'количество')

        order = await dataset.order(
            type='order',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 25,
                },
                {
                    'item_id': item.item_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.ok(await item.reload(), 'экземпляр перегружен')
        tap.eq(item.status, 'inactive', 'экземпляр неактивен')

        product2 = await dataset.product()
        tap.ok(product2, 'товар 2 создан')

        t = await api(user=user)

        external_id = uuid()

        tap.note('Пытаемся вернуть продукт, которого не было')

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'part_refund',
                            'parent_order_id': order.order_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 21
                                },
                                {
                                    'product_id': product2.product_id,
                                    'count': 7,
                                },
                                {
                                    'item_id': item.item_id,
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#1: {product2.product_id}'
        )
        t.json_is(
            'details.errors.0.product_id',
            product2.product_id
        )

        tap.note('Пытаемся вернуть больше, чем было в заказе')

        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'part_refund',
                            'parent_order_id': order.order_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 212
                                },
                                {
                                    'item_id': item.item_id,
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {product.product_id}'
        )
        t.json_is(
            'details.errors.0.product_id',
            product.product_id
        )

        tap.note('Попытка вернуть сразу две посылки')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'item_id': item.item_id,
                        'count': 2,
                    }
                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        tap.note('Успешно рефандим часть')
        await t.post_ok('api_disp_orders_create',
                        json={
                            'external_id': external_id,
                            'type': 'part_refund',
                            'parent_order_id': order.order_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 15
                                },
                                {
                                    'item_id': item.item_id,
                                }
                            ],
                            'approved': True,
                            'ack': user.user_id,
                        })
        t.status_is(200, diag=True)
        t.json_has('order.order_id')

        second_external = uuid()

        tap.note('При живом рефанде создаем второй с лишней посылкой')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': second_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'item_id': item.item_id,
                    },
                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {item.item_id}'
        )
        t.json_is(
            'details.errors.0.item_id',
            item.item_id
        )

        tap.note('При живом рефанде пытаемся рефандить больше')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': second_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 11
                    },

                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {product.product_id}'
        )
        t.json_is(
            'details.errors.0.product_id',
            product.product_id
        )

        tap.note('Создаем второй рефанд')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': second_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 9
                    },

                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('order.order_id')

        third_external = uuid()
        tap.note('Пока не можем создать еще рефанд')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': third_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 8
                    },

                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {product.product_id}'
        )
        t.json_is(
            'details.errors.0.product_id',
            product.product_id
        )

        second_part_refund = await dataset.Order.load(
            [store.store_id, second_external],
            by='external'
        )
        tap.ok(second_part_refund, 'Рефанд на месте')
        second_part_refund.target = 'canceled'
        tap.ok(await second_part_refund.save(), 'сохранили ордер')

        await wait_order_status(
            second_part_refund,
            ('canceled', 'done'),
            user_done=user
        )

        tap.note('После отмены старого рефанда - можем новый')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': third_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 8
                    },

                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(200, diag=True)

        order_part_refund = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )

        parent = await Order.load(order_part_refund.parent)
        tap.in_ok(order_part_refund.order_id,
                  parent.vars('child_orders'),
                  'ребенок есть в ордере')

        tap.eq(order_part_refund.store_id, store.store_id, 'ордер создан')
        tap.eq(order_part_refund.type, 'part_refund', 'частичный возврат')
        tap.eq(len(order_part_refund.required), 2, 'длина required части')
        tap.in_ok(order.attr.get('doc_number'),
                  order_part_refund.attr.get('doc_number'), 'doc_number')

        with order_part_refund.required[0] as r:
            tap.eq(r.product_id, product.product_id, 'товар')
            tap.eq(r.stock_id, stock_product.stock_id, 'stock_id')
            tap.eq(r.count, 15, 'количество')
            tap.eq(r.shelf_id, stock_product.shelf_id, 'shelf_id')

        with order_part_refund.required[1] as r:
            tap.eq(r.item_id, item.item_id, 'экземпляр')
            tap.eq(r.stock_id, stock_item.stock_id, 'stock_id')
            tap.eq(r.count, 1, 'количество')
            tap.eq(r.shelf_id, stock_item.shelf_id, 'shelf_id')

        await wait_order_status(order_part_refund, ('request', 'waiting'))
        tap.ok(await order_part_refund.ack(user), 'ack')
        await wait_order_status(order_part_refund,
                                ('complete', 'done'), user_done=user)

        tap.ok(await stock_product.reload(), 'перегружен сток')
        tap.eq(stock_product.count, 27 - 25 + 15, 'количество на стоке')

        tap.ok(await stock_item.reload(), 'перегружен сток')
        tap.eq(stock_item.count, 1, 'количество на стоке с экземпляром')

        tap.ok(await item.reload(), 'экземпляр перегружен')
        tap.eq(item.status, 'active', 'экземпляр снова активен')


async def test_another_stocks(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(34, 'Создание рефанда при смене топологии'):
        store = await dataset.full_store()
        user = await dataset.user(store=store)
        item = await dataset.item(store=store)
        product = await dataset.product()
        stock_product_1 = await dataset.stock(
            product=product,
            store=store,
            count=13
        )
        stock_product_2 = await dataset.stock(
            product=product,
            store=store,
            count=12
        )
        stock_item = await dataset.stock(
            item=item,
            store=store,
            count=1
        )
        order = await dataset.order(
            type='order',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 25,
                },
                {
                    'item_id': item.item_id,
                }
            ]
        )
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        shelf_1 = await dataset.Shelf.load(stock_product_1.shelf_id)
        shelf_1.status = 'removed'
        tap.ok(await shelf_1.save(), 'Выключили одну продуктовую полку')
        shelf_item = await dataset.Shelf.load(stock_item.shelf_id)
        shelf_item.status = 'removed'
        tap.ok(await shelf_item.save(), 'Выключили посылочную полку')

        t = await api(user=user)
        external_id = uuid()

        tap.note('Успешно рефандим часть')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 15
                    },
                    {
                        'item_id': item.item_id,
                    }
                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('order.order_id')
        first_refund = await dataset.Order.load(
            [store.store_id, external_id], by='external')
        await wait_order_status(first_refund, ('request', 'waiting'))

        second_external = uuid()
        tap.note('При живом рефанде создаем второй с лишним продуктом')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': second_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 11
                    },
                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {product.product_id}'
        )
        t.json_is(
            'details.errors.0.product_id',
            product.product_id,
        )
        tap.ok(await first_refund.ack(user=user), 'Взяли рефанд в работу')
        await wait_order_status(
            first_refund,
            ('complete', 'done'),
            user_done=user
        )
        tap.ok(await stock_item.reload(), 'Перезабрали остаток посылка')
        tap.eq(stock_item.count, 0, 'Вернули в другое место')
        tap.ok(await stock_product_1.reload(), 'Перезабрали остаток 1')
        tap.eq(stock_product_1.count, 0, 'Вернули не в обратный остаток')
        tap.ok(await stock_product_2.reload(), 'Перезабрали остаток 2')
        tap.eq(stock_product_2.count, 15, 'Вернули все сюда')
        tap.eq(len(first_refund.required), 2, 'Две записи')
        product_required = next(
            req for req in first_refund.required if req.product_id
        )
        tap.eq(product_required.result_count, 15, 'Вернули 15 разом')
        tap.eq(
            product_required.stock_id,
            stock_product_2.stock_id,
            'Вернули в один остаток'
        )
        item_required = next(
            req for req in first_refund.required if req.item_id
        )
        tap.ok(
            item_required.stock_id != stock_item.stock_id,
            'Посылка на другом остатке'
        )
        tap.note('Все еще не можем вернуть лишнее')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': second_external,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 11
                    },
                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {product.product_id}'
        )
        t.json_is(
            'details.errors.0.product_id',
            product.product_id,
        )

        tap.note('Посылку тоже не вернем')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'part_refund',
                'parent_order_id': order.order_id,
                'required': [
                    {
                        'item_id': item.item_id,
                        'count': 1,
                    }
                ],
                'approved': True,
                'ack': user.user_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is(
            'details.errors.0.message',
            f'Wrong count for required#0: {item.item_id}'
        )
        t.json_is(
            'details.errors.0.item_id',
            item.item_id,
        )
