import datetime

from stall import cfg


# pylint: disable=too-many-locals,too-many-statements
async def test_create(tap, dataset, api, uuid, wait_order_status):
    with tap.plan(82, 'разные кейсы для возврата отгрузки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='support_it')
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

        shipment = await dataset.order(
            type='shipment',
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
        tap.eq(shipment.store_id, store.store_id, 'заказ создан')
        await wait_order_status(shipment, ('complete', 'done'), user_done=user)

        tap.ok(await item.reload(), 'экземпляр перегружен')
        tap.eq(item.status, 'inactive', 'экземпляр неактивен')

        product2 = await dataset.product()
        tap.ok(product2, 'товар 2 создан')

        t = await api(user=user)

        external_id = uuid()

        tap.note('Пытаемся вернуть продукт, которого не было')

        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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
            },
        )
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
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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

        tap.note('Попытка вернуть сразу две посылки')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'part_refund',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': external_id,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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
            },
        )
        t.status_is(200, diag=True)
        t.json_has('order.order_id')

        second_external = uuid()

        tap.note('При живом рефанде создаем второй с лишней посылкой')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': second_external,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
                'required': [
                    {
                        'product_id': product.product_id,
                        'count': 11,
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
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': '300',
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

        second_shipment_rollback = await dataset.Order.load(
            [store.store_id, second_external],
            by='external'
        )
        tap.ok(second_shipment_rollback, 'Рефанд на месте')
        second_shipment_rollback.target = 'canceled'
        tap.ok(await second_shipment_rollback.save(), 'сохранили ордер')

        await wait_order_status(
            second_shipment_rollback,
            ('canceled', 'done'),
            user_done=user
        )

        tap.note('После отмены старого рефанда - можем новый')
        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': third_external,
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
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

        first_shipment_rollback = await dataset.Order.load(
            [store.store_id, external_id],
            by='external'
        )

        tap.eq(
            first_shipment_rollback.store_id, store.store_id, 'ордер создан',
        )
        tap.eq(
            first_shipment_rollback.type,
            'shipment_rollback',
            'частичный возврат',
        )
        tap.eq(
            len(first_shipment_rollback.required),
            2,
            'длина required части',
        )
        tap.in_ok(
            shipment.attr.get('doc_number'),
            first_shipment_rollback.attr.get('doc_number'),
            'doc_number',
        )
        tap.eq(
            first_shipment_rollback.attr['reason'],
            'потому что потому',
            'причина отмены',
        )

        with first_shipment_rollback.required[0] as r:
            tap.eq(r.product_id, product.product_id, 'товар')
            tap.eq(r.stock_id, stock_product.stock_id, 'stock_id')
            tap.eq(r.count, 15, 'количество')
            tap.eq(r.shelf_id, stock_product.shelf_id, 'shelf_id')

        with first_shipment_rollback.required[1] as r:
            tap.eq(r.item_id, item.item_id, 'экземпляр')
            tap.eq(r.stock_id, stock_item.stock_id, 'stock_id')
            tap.eq(r.count, 1, 'количество')
            tap.eq(r.shelf_id, stock_item.shelf_id, 'shelf_id')

        await wait_order_status(
            first_shipment_rollback, ('request', 'waiting'),
        )

        tap.ok(await first_shipment_rollback.ack(user), 'ack')

        await wait_order_status(
            first_shipment_rollback,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await first_shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'trash'}},
            ),
            'сигнал для перехода на этап раскладки в мусорку'
        )

        await wait_order_status(
            first_shipment_rollback,
            ('processing', 'close_sig'),
            user_done=user,
        )

        await wait_order_status(
            first_shipment_rollback,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await first_shipment_rollback.signal(
                {'type': 'next_stage', 'data': {'stage': 'all_done'}},
            ),
            'сигнал для перехода на этап раскладки в мусорку'
        )

        await wait_order_status(
            first_shipment_rollback,
            ('processing', 'close_sig'),
            user_done=user,
        )

        await wait_order_status(
            first_shipment_rollback,
            ('complete', 'done'),
            user_done=user,
        )

        tap.ok(await stock_product.reload(), 'перегружен сток')
        tap.eq(stock_product.count, 27 - 25 + 15, 'количество на стоке')

        tap.ok(await stock_item.reload(), 'перегружен сток')
        tap.eq(stock_item.count, 1, 'количество на стоке с экземпляром')

        tap.ok(await item.reload(), 'экземпляр перегружен')
        tap.eq(item.status, 'active', 'экземпляр снова активен')


async def test_too_old(tap, dataset, api, uuid, now):
    with tap.plan(7, 'не разрешаем откатывать старые отгрузки'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='support_it')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        shipment = await dataset.order(
            type='shipment',
            acks=[user.user_id],
            approved=True,
            store=store,
            required=[
                {
                    'product_id': uuid(),
                    'count': 25,
                },
            ]
        )

        orig_created = shipment.created

        created = now()
        created -= datetime.timedelta(
            seconds=(cfg('business.order.shipment.rollback_interval') + 3600)
        )

        shipment.created = created
        await shipment.save()

        tap.ok(shipment.created < orig_created, 'отправляем ордер в прошлое')

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_create',
            json={
                'external_id': uuid(),
                'type': 'shipment_rollback',
                'parent_order_id': shipment.order_id,
                'reason': 'потому что потому',
                'required': [
                    {
                        'product_id': uuid(),
                        'count': 21
                    },
                ],
                'approved': True,
                'ack': user.user_id,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Parent order is too old to rollback')
