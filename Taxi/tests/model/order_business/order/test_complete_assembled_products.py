from collections import defaultdict


async def test_assembled_products(tap, dataset, wait_order_status, now, uuid):
    # pylint: disable=too-many-locals
    with tap.plan(18, 'Заполняем assembled products'):
        def generate_mark(product):
            barcode = product.barcode[0]
            return f'01{barcode}21{uuid()[:6]}\x1D93Zjqw'

        store = await dataset.store(options={'exp_albert_hofmann': True})
        user = await dataset.user(store=store)

        barcode_one = '1' + uuid()[:13]
        marked_product_one = await dataset.product(
            vars={'imported': {'true_mark': True}},
            barcode=[barcode_one],
        )

        barcode_two = '1' + uuid()[:13]
        marked_product_two = await dataset.product(
            vars={'imported': {'true_mark': True}},
            barcode=[barcode_two],
        )
        regular_product = await dataset.product()
        item = await dataset.item(store=store)

        marked_products = {
            marked_product_one.product_id: marked_product_one,
            marked_product_two.product_id: marked_product_two,
        }

        await dataset.stock(product=marked_product_one, store=store, count=10)
        await dataset.stock(product=marked_product_two, store=store, count=10)
        await dataset.stock(product=regular_product, store=store, count=10)
        await dataset.stock(item=item, store=store, count=1)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': marked_product_one.product_id,
                    'count': 3
                },
                {
                    'product_id': marked_product_two.product_id,
                    'count': 1
                },
                {
                    'item_id': item.item_id,
                    'count': 1
                },
            ],
            vars={'editable': True},
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 5, 'Четыре саджеста сначала')

        mark_register = defaultdict(list)
        for suggest in suggests:
            if suggest.product_id in marked_products:
                product = marked_products[suggest.product_id]
                mark = generate_mark(product)
                mark_register[product.product_id].append(mark)
                tap.ok(
                    await suggest.done(
                        user=user, count=suggest.count, true_mark=mark),
                    'Закрыли успешно марочный саджест'
                )
            else:
                tap.ok(
                    await suggest.done(user=user, count=suggest.count),
                    'Закрыли успешно обычный саджест'
                )

        tap.ok(await order.reload(), 'Перезабрали документ')
        order.vars['required'] = [
            {
                'product_id': marked_product_one.product_id,
                'count': 2
            },
            {
                'item_id': item.item_id,
                'count': 1
            },
            {
                'product_id': regular_product.product_id,
                'count': 3
            }
        ]
        tap.ok(
            await order.save(store_job_event=False),
            'Прикопали реквайред новый'
        )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(
            order,
            status=['request']
        )
        tap.eq(len(suggests), 3, 'Три саджеста еще')

        for suggest in suggests:
            if suggest.product_id in marked_products:
                mark = mark_register[suggest.product_id].pop()
                tap.ok(
                    await suggest.done(
                        user=user, count=suggest.count, true_mark=mark),
                    'Закрыли успешно обратный марочный саджест'
                )
            else:
                tap.ok(
                    await suggest.done(user=user, count=suggest.count),
                    'Закрыли успешно дополнительный саджест'
                )
        tap.ok(
            await order.done(user=user, target='complete'),
            'Успешно завершили документ',
        )

        await wait_order_status(order, ('complete', 'done'))

        tap.ok(
            'assembled_products' in order.vars,
            'Прикопали товары в документе',
        )

        assembled_in_order = sorted(
            order.vars('assembled_products', []),
            key=lambda i: (i['product_id'], i.get('true_mark'))
        )
        expected_assembled = [
            {
                'count': 3,
                'product_id': regular_product.product_id,
                'product_type': 'product'
            },
            {
                'count': 1,
                'true_mark': mark_register[
                    marked_product_one.product_id].pop(),
                'product_id': marked_product_one.product_id,
                'product_type': 'product'
            },
            {
                'count': 1,
                'true_mark': mark_register[
                    marked_product_one.product_id].pop(),
                'product_id': marked_product_one.product_id,
                'product_type': 'product'
            },
            {
                'count': 1,
                'product_id': item.item_id,
                'product_type': 'item'
            }
        ]
        expected_assembled = sorted(
            expected_assembled,
            key=lambda i: (i['product_id'], i.get('true_mark'))
        )
        tap.eq(
            assembled_in_order,
            expected_assembled,
            'Итоговые продукты правильно заполнили'
        )
