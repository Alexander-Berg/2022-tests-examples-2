async def test_third_party_processing(tap, dataset, wait_order_status, uuid):
    # pylint: disable=too-many-locals
    with tap.plan(37, 'Обработка нескольких отчетов'):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'Склад создан')
        user = await dataset.user(role='admin', store=store)
        tap.ok(user, 'Пользователь создан')

        tap.ok(
            await dataset.shelf(store=store, type='lost'),
            'Полка lost'
        )
        tap.ok(
            await dataset.shelf(store=store, type='found'),
            'Полка found'
        )

        shelf_one = await dataset.shelf(store=store)
        tap.ok(shelf_one, 'Одна полка')
        shelf_two = await dataset.shelf(store=store)
        tap.ok(shelf_two, 'Вторая полка')
        shelf_three = await dataset.shelf(store=store)
        tap.ok(shelf_three, 'Третья полка')
        shelf_four = await dataset.shelf(store=store)

        product = await dataset.product()
        tap.ok(product, 'Создали продукт')

        order = await dataset.order(
            type='inventory_check_more',
            store=store,
            required=[
                {'shelf_id': shelf_one.shelf_id},
                {'shelf_id': shelf_two.shelf_id},
                {'shelf_id': shelf_four.shelf_id},
            ],
            status='reserving',
            acks=[user.user_id],
            vars={'third_party_assistance': True},
        )
        tap.ok(order, 'Ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        async def send_report(rows):
            stash_name = f'inventory_report-{order.order_id}'
            tap.ok(
                await dataset.Stash.stash(name=stash_name, rows=rows),
                'Сохранили отчет'
            )
            tap.ok(
                await order.signal(
                    {'type': 'inventory_report_imported'},
                    user=user
                ),
                'Сигнал отправлен'
            )
            await wait_order_status(order, ('processing', 'waiting_signal'))
            await order.reload()

        suggests = await dataset.Suggest.list_by_order(order)

        for suggest in suggests:
            if suggest.shelf_id == shelf_four.shelf_id:
                continue
            tap.ok(
                await suggest.done(product_id=product.product_id, count=20),
                'Cаджест закрыт'
            )
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        for suggest in suggests:
            if suggest.status != 'request':
                continue
            tap.ok(
                await suggest.done(status='error'),
                'Работу с саджестами завершаем'
            )
        await wait_order_status(order, ('processing', 'waiting_signal'))

        fake_external_id = uuid()

        await send_report(
            [
                {
                    'product': fake_external_id,
                    'shelf': shelf_one.title,
                    'count': 10
                },
                {
                    'product': fake_external_id,
                    'shelf': shelf_two.title,
                    'count': 12
                }
            ]
        )
        tap.eq(
            order.vars('report'),
            {
                shelf_one.shelf_id: {
                    product.product_id: {'result_count': 20}
                },
                shelf_two.shelf_id: {
                    product.product_id: {'result_count': 20}
                }
            },
            'Отчет не изменился после кривого продукта'
        )
        tap.eq(
            order.vars('third_party_report_imported', False),
            False,
            'Отчет не был загружен'
        )

        await send_report(
            [
                {
                    'product': product.external_id,
                    'shelf': shelf_one.title,
                    'count': 10
                },
                {
                    'product': product.external_id,
                    'shelf': fake_external_id,
                    'count': 12
                }
            ]
        )

        tap.eq(
            order.vars('report'),
            {
                shelf_one.shelf_id: {
                    product.product_id: {'result_count': 20}
                },
                shelf_two.shelf_id: {
                    product.product_id: {'result_count': 20}
                }
            },
            'Отчет не изменился после кривой полки'
        )
        tap.eq(
            order.vars('third_party_report_imported', False),
            False,
            'Отчет не был загружен'
        )

        await send_report(
            [
                {
                    'product': product.external_id,
                    'shelf': shelf_one.title,
                    'count': 10
                },
                {
                    'product': product.external_id,
                    'shelf': shelf_four.title,
                    'count': 12
                }
            ]
        )

        tap.eq(
            order.vars('report'),
            {
                shelf_one.shelf_id: {
                    product.product_id: {
                        'result_count': 20,
                        'tp_count': 10,
                    }
                },
                shelf_two.shelf_id: {
                    product.product_id: {
                        'result_count': 20,
                    }
                },
                shelf_four.shelf_id: {
                    product.product_id: {
                        'tp_count': 12,
                    }
                },
            },
            'Отчет изменился'
        )
        tap.eq(
            order.vars('third_party_report_imported', False),
            True,
            'Отчет был загружен'
        )
        await send_report(
            [
                {
                    'product': product.external_id,
                    'shelf': shelf_one.title,
                    'count': 101
                },
                {
                    'product': product.external_id,
                    'shelf': shelf_three.title,
                    'count': 13
                }
            ]
        )

        tap.eq(
            order.vars('report'),
            {
                shelf_one.shelf_id: {
                    product.product_id: {
                        'result_count': 20,
                        'tp_count': 101,
                    }
                },
                shelf_two.shelf_id: {
                    product.product_id: {
                        'result_count': 20,
                    }
                }
            },
            'Отчет изменился после перезагрузки'
        )
        tap.eq(
            order.vars('third_party_report_imported', False),
            True,
            'Флаг выставлен по-прежнему'
        )
