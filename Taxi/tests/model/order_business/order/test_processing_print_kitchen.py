async def test_status(tap, dataset, wait_order_status, now, uuid):
    with tap.plan(14, 'переход в саб-статус генерации саджестов для кухни'):
        store = await dataset.store(
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': True,
                         'logo': 'lavka'},
        )

        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        with products['latte'] as product:
            product.rehash(
                long_title=f'Длинное название продукта {uuid()}',
                barcode=['2090006001215'],
            )
            await product.save()
        with products['cappuccino'] as product:
            product.rehash(
                long_title=f'Длинное название продукта {uuid()}',
                barcode=['2090006001216'],
            )
            await product.save()

        required = [
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 1,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=required,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'print_kitchen'))
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'print_kitchen', 'print_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '0',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'задание на печать для чашки латте 1')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '1',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'задание на печать для чашки латте 2')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '2',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(not task, 'заданий на печать латте больше нет')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['cappuccino'].product_id,
            '0',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'задание на печать для чашки капучино 1')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['cappuccino'].product_id,
            '1',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(not task, 'заданий на печать капучино больше нет')


async def test_store_uuknown_lang(tap, dataset, wait_order_status, now, uuid):
    with tap.plan(2, 'проверяем что заказ не падает при кривом lang лавки'):
        store = await dataset.store(
            lang='en_GB',
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': True,
                         'logo': 'lavka'},
        )
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        with products['latte'] as product:
            product.rehash(
                long_title=f'Длинное название продукта {uuid()}',
                barcode=['2090006001215'],
            )
            await product.save()

        required = [
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=required,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '0',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'если у нас не настроена локаль то все равно все ок')


async def test_duplication(tap, dataset, wait_order_status, now, uuid):
    with tap.plan(12, 'проверяем что печать этикеток не дублируется'
                      ' при изменении заказа'):
        store = await dataset.store(
            print_setup={'kitchen_sticker': 'sticker',
                         'sticker_size': '50x150',
                         'eac': True,
                         'logo': 'lavka'},
        )

        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        with products['latte'] as product:
            product.rehash(
                long_title=f'Длинное название продукта {uuid()}',
                barcode=['2090006001215'],
            )
            await product.save()

        with products['cappuccino'] as product:
            product.rehash(
                long_title=f'Длинное название продукта {uuid()}',
                barcode=['2090006001216'],
            )
            await product.save()

        required_v1 = [
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
            required=required_v1,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'print_kitchen'))
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        required_v2 = [
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 1,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))
        await order.reload()

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '0',
        ))

        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'задание на печать для чашки латте 1')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '1',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'задание на печать для чашки латте 2')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['latte'].product_id,
            '2',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(not task, 'заданий на печать латте больше нет')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['cappuccino'].product_id,
            '0',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(task, 'задание на печать для чашки капучино 1')

        external_id = ':'.join((
            str(order.order_id),
            'processing',
            'print_kitchen',
            'kitchen_sticker',
            products['cappuccino'].product_id,
            '1',
        ))
        task = await dataset.PrinterTask.load(external_id, by='external')
        tap.ok(not task, 'заданий на печать капучино больше нет')
