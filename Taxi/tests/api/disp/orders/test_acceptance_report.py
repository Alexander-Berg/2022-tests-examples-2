# pylint: disable=too-many-lines

async def test_acceptance_report(
    tap, dataset, api, wait_order_status, cfg, job
):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(37, 'Получение акта приемки'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        cfg.set('cursor.limit', 1)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        parent, *weight_products = await dataset.weight_products()
        products.append(weight_products[0])

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        right_report = []

        for number, product in enumerate(products, start=1):
            await dataset.assortment_contractor_product(
                assortment=assortment,
                product=product,
                status='active',
                price=number*69
            )
            right_report.append({
                'product_id': product.product_id,
                'price': "{:.2f}".format(number*69),
                'count': number*2,
                'result_count': number*2,
                'trash': 0,
                'correction': 0,
                'result_delta': 0,
                'delta': 0
            })

        right_report[3]['count'] = None
        right_report[3]['weight'] = 8
        right_report[3]['delta'] = 8
        right_report[3]['result_delta'] = 8
        right_report.append({
            'product_id': parent.product_id,
            'price': None,
            'count': 8,
            'result_count': 0,
            'trash': 0,
            'correction': 0,
            'result_delta': -8,
            'delta': -8
        })

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
                {
                    'product_id': parent.product_id,
                    'count': 8,
                    'weight': 8
                }
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        for stowage_order_id in order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            tap.ok(
                await stowage_order.ack(user=user),
                'взяли в работу stowage'
            )

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            tap.ok(
                await stowage_order.signal({'type': 'sale_stowage'}),
                'сигнал'
            )

            if stowage_order.type == 'weight_stowage':
                suggests = await dataset.Suggest.list_by_order(stowage_order)
                with suggests[0] as s:
                    tap.ok(await s.done(
                        count=8,
                        weight=8,
                        product_id=products[3].product_id
                    ), 'завершён')

        stowage_order = await dataset.Order.load(order.vars['stowage_id'][0])
        await wait_order_status(
            stowage_order,
            ('complete', 'done'),
            user_done=user
        )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_DESCENDANTS_IS_NOT_DONE')

        stowage_order = await dataset.Order.load(order.vars['stowage_id'][1])
        await wait_order_status(
            stowage_order,
            ('complete', 'done'),
            user_done=user
        )

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')

        # Обновили ассортимент поставщика
        await job.call(await job.take())

        # Генерируем акт
        await job.call(await job.take())

        name = f'orders_acceptance_report-{order.order_id}'
        stash = await dataset.Stash.load(name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')

        name_stash_report = f'acceptance_report-{order.order_id}'
        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        report = stash_report.value.get('report')
        tap.ok(report, 'Отчет сгенерирован')

        right_report.sort(key=lambda x: x['product_id'])
        report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report):
            if report[row]['product_id'] == parent.product_id:
                tap.eq_ok(
                    report[row].pop('shelf_ids', []), [],
                    'У весового родителя нет полок')
            else:
                tap.ne(report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                report[row], field_report, f'Проверка отчета. Строка {row} ')

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await job.call(await job.take())

        new_stash_report = await dataset.Stash.load(
            name_stash_report, by='name')

        tap.eq(
            stash_report.lsn,
            new_stash_report.lsn,
            'Отчет не генерировался заново'
        )


async def test_acceptance_agree(
        tap, dataset, api, wait_order_status, cfg, job):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(28, 'Доверительная приемка'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        parent, *weight_products = await dataset.weight_products()
        products.append(weight_products[0])

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        right_report = []

        for number, product in enumerate(products, start=1):
            await dataset.assortment_contractor_product(
                assortment=assortment,
                product=product,
                status='active',
                price=number*69
            )
            right_report.append({
                'product_id': product.product_id,
                'price': "{:.2f}".format(number*69),
                'count': number*2,
                'result_count': number*2,
                'trash': 0,
                'correction': 0,
                'result_delta': 0,
                'delta': 0
            })

        right_report[3]['count'] = None
        right_report[3]['weight'] = 8
        right_report[3]['delta'] = 8
        right_report[3]['result_delta'] = 8
        right_report.append({
            'product_id': parent.product_id,
            'price': None,
            'count': 8,
            'result_count': 0,
            'trash': 0,
            'correction': 0,
            'result_delta': -8,
            'delta': -8
        })

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
                {
                    'product_id': parent.product_id,
                    'count': 8,
                    'weight': 8
                }
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        tap.ok(
            await order.signal({'type': 'acceptance_agree'}),
            'Сигнал на доверительную приемку'
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        for stowage_order_id in order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            tap.ok(
                await stowage_order.ack(user=user),
                'взяли в работу stowage'
            )

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            tap.ok(
                await stowage_order.signal({'type': 'sale_stowage'}),
                'сигнал'
            )

            if stowage_order.type == 'weight_stowage':
                suggests = await dataset.Suggest.list_by_order(stowage_order)
                with suggests[0] as s:
                    tap.ok(await s.done(
                        count=8,
                        weight=8,
                        product_id=products[3].product_id
                    ), 'завершён')

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновили ассортимент поставщика
        await job.call(await job.take())

        # Генерируем акт
        await job.call(await job.take())

        name = f'orders_acceptance_report-{order.order_id}'
        stash = await dataset.Stash.load(name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')

        name_stash_report = f'acceptance_report-{order.order_id}'
        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        report = stash_report.value.get('report')
        tap.ok(report, 'Отчет сгенерирован')

        right_report.sort(key=lambda x: x['product_id'])
        report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report):
            if report[row]['product_id'] == parent.product_id:
                tap.eq_ok(
                    report[row].pop('shelf_ids', []), [],
                    'У весового родителя нет полок')
            else:
                tap.ne(report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                field_report, report[row], f'Проверка отчета. Строка {row} ')


async def test_check(
        tap, dataset, api, wait_order_status, cfg, job):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(30, 'создание дочернего ордера'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        right_report = []

        for number, product in enumerate(products, start=1):
            await dataset.assortment_contractor_product(
                assortment=assortment,
                product=product,
                status='active',
                price=number*69
            )
            right_report.append({
                'product_id': product.product_id,
                'price': "{:.2f}".format(number*69),
                'count': number*2,
                'result_count': number*2,
                'trash': 0,
                'correction': 0,
                'result_delta': 0,
                'delta':        0
            })

        right_report[0]['correction'] = 11
        right_report[0]['result_delta'] = 11

        acceptance_order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        await wait_order_status(
            acceptance_order, ('complete', 'done'), user_done=user)

        for stowage_order_id in acceptance_order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            tap.ok(
                await stowage_order.ack(user=user),
                'взяли в работу stowage'
            )

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            tap.ok(
                await stowage_order.signal({'type': 'sale_stowage'}),
                'сигнал'
            )

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        stock = await dataset.Stock.list_by_product(
            product_id=products[0].product_id,
            shelf_type='store',
            store_id=store.store_id,
        )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': acceptance_order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновили ассортимент поставщика
        await job.call(await job.take())

        # Генерируем акт
        await job.call(await job.take())

        check_order = await dataset.order(
            type='check_product_on_shelf',
            products=[products[0].product_id],
            shelves=[stock[0].shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            parent=[acceptance_order.order_id],
        )

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': acceptance_order.order_id
            }
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_DESCENDANTS_IS_NOT_DONE')

        await wait_order_status(check_order, ('request', 'waiting'))
        await check_order.ack(user)

        await wait_order_status(check_order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(check_order)

        with suggests[0] as s:
            tap.ok(await s.done(count=13, valid='02-03-2022'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')

            tap.eq(s.result_count, 13, 'результирующее число')

        tap.ok(await check_order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(check_order, ('complete', 'done'))

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': acceptance_order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Генерируем акт
        await job.call(await job.take())

        name = f'orders_acceptance_report-{acceptance_order.order_id}'
        stash = await dataset.Stash.load(name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')

        name_stash_report = f'acceptance_report-{acceptance_order.order_id}'
        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        report = stash_report.value.get('report')
        tap.ok(report, 'Отчет сгенерирован')

        right_report.sort(key=lambda x: x['product_id'])
        report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report):
            tap.ne(report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                report[row], field_report, f'Проверка отчета. Строка {row} ')


async def test_non_exist_order(tap, uuid, dataset, api):
    with tap.plan(3, 'Несуществующий ордер'):
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)
        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': uuid()
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_wrong_type_order(tap, dataset, api):
    with tap.plan(3, 'Ордер не acceptance'):
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)
        user = await dataset.user(store=store)

        t = await api(user=user)

        some_order = await dataset.order(
            store=store,
            acks=[user.user_id],
        )

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': some_order.order_id
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_trash(
        tap, dataset, api, wait_order_status, cfg, job):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(40, 'Часть продуктов списали'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(
            company=company,
            options={'exp_chicken_run': True}
        )

        products = [await dataset.product() for _ in range(3)]

        parent, *weight_products = await dataset.weight_products()
        products.append(weight_products[0])

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        right_report = []

        for number, product in enumerate(products, start=1):
            await dataset.assortment_contractor_product(
                assortment=assortment,
                product=product,
                status='active',
                price=number*69
            )
            right_report.append({
                'product_id': product.product_id,
                'price': "{:.2f}".format(number*69),
                'count': number*2,
                'result_count': number*2,
                'trash': 0,
                'correction': 0,
                'result_delta': 0,
                'delta': 0
            })

        right_report[0]['correction'] = 11
        right_report[0]['result_delta'] = 11
        right_report[3]['trash'] = 8
        right_report[3]['count'] = None
        right_report[3]['delta'] = 8
        right_report[3]['result_delta'] = 8
        right_report[3]['weight'] = 8
        right_report.append({
            'product_id': parent.product_id,
            'price': None,
            'count': 8,
            'result_count': 0,
            'trash': 0,
            'correction': 0,
            'result_delta': -8,
            'delta': -8
        })

        order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
                {
                    'product_id': parent.product_id,
                    'count': 8,
                    'weight': 8
                }
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        for stowage_order_id in order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            tap.ok(
                await stowage_order.ack(user=user),
                'взяли в работу stowage'
            )

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            if stowage_order.type == 'weight_stowage':
                suggests = await dataset.Suggest.list_by_order(stowage_order)

                tap.ok(
                    await stowage_order.signal({'type': 'sale_stowage'}),
                    'сигнал sale_stowage'
                )

                await wait_order_status(
                    stowage_order, ('processing', 'waiting')
                )

                tap.eq(stowage_order.vars('stage'), 'trash', 'stage')

                with suggests[0] as s:
                    tap.ok(await s.done(
                        count=8,
                        weight=8,
                        product_id=products[3].product_id
                    ), 'завершён')

            else:
                tap.ok(
                    await stowage_order.signal({'type': 'sale_stowage'}),
                    'сигнал'
                )

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновили ассортимент поставщика
        await job.call(await job.take())

        stock = await dataset.Stock.list_by_product(
            product_id=products[0].product_id,
            shelf_type='store',
            store_id=store.store_id,
        )

        check_order = await dataset.order(
            type='check_product_on_shelf',
            products=[products[0].product_id],
            shelves=[stock[0].shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            parent=[order.order_id],
        )

        await wait_order_status(check_order, ('request', 'waiting'))
        await check_order.ack(user)

        await wait_order_status(check_order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(check_order)

        with suggests[0] as s:
            tap.ok(await s.done(count=13, valid='02-03-2022'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')

            tap.eq(s.result_count, 13, 'результирующее число')

        # Генерируем акт
        await job.call(await job.take())

        name_stash_report = f'acceptance_report-{order.order_id}'
        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        tap.eq(stash_report, None, 'Отчета нет')

        tap.ok(await check_order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(check_order, ('complete', 'done'))

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await job.call(await job.take())

        name = f'orders_acceptance_report-{order.order_id}'
        stash = await dataset.Stash.load(name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')

        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        report = stash_report.value.get('report')
        tap.ok(report, 'Отчет сгенерирован')

        right_report.sort(key=lambda x: x['product_id'])
        report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report):
            if report[row]['product_id'] == parent.product_id:
                tap.eq_ok(
                    report[row].pop('shelf_ids', []), [],
                    'У весового родителя нет полок')
            else:
                tap.ne(report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                report[row], field_report, f'Проверка отчета. Строка {row} ')


async def test_no_price(
        tap, dataset, api, wait_order_status, cfg, job):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(27, 'Отсутствует поставщик'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        parent, *weight_products = await dataset.weight_products()
        products.append(weight_products[0])

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        right_report = []

        for number, product in enumerate(products, start=1):
            right_report.append({
                'product_id': product.product_id,
                'price': None,
                'count': number*2,
                'result_count': number*2,
                'trash': 0,
                'correction': 0,
                'result_delta': 0,
                'delta': 0
            })

        right_report[3]['count'] = None
        right_report[3]['delta'] = 8
        right_report[3]['result_delta'] = 8
        right_report[3]['weight'] = 8
        right_report.append({
            'product_id': parent.product_id,
            'price': None,
            'count': 8,
            'result_count': 0,
            'trash': 0,
            'correction': 0,
            'result_delta': -8,
            'delta': -8
        })

        acceptance_order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
                {
                    'product_id': parent.product_id,
                    'count': 8,
                    'weight': 8
                }
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        await wait_order_status(
            acceptance_order, ('complete', 'done'), user_done=user)

        for stowage_order_id in acceptance_order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            tap.ok(
                await stowage_order.ack(user=user),
                'взяли в работу stowage'
            )

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            tap.ok(
                await stowage_order.signal({'type': 'sale_stowage'}),
                'сигнал'
            )

            if stowage_order.type == 'weight_stowage':
                suggests = await dataset.Suggest.list_by_order(stowage_order)
                with suggests[0] as s:
                    tap.ok(await s.done(
                        count=8,
                        weight=8,
                        product_id=products[3].product_id
                    ), 'завершён')

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': acceptance_order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновили ассортимент поставщика
        await job.call(await job.take())

        # Генерируем акт
        await job.call(await job.take())

        name = f'orders_acceptance_report-{acceptance_order.order_id}'
        stash = await dataset.Stash.load(name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')

        name_stash_report = f'acceptance_report-{acceptance_order.order_id}'
        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        report = stash_report.value.get('report')
        tap.ok(report, 'Отчет сгенерирован')

        right_report.sort(key=lambda x: x['product_id'])
        report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report):
            if report[row]['product_id'] == parent.product_id:
                tap.eq_ok(
                    report[row].pop('shelf_ids', []), [],
                    'У весового родителя нет полок')
            else:
                tap.ne(report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                field_report, report[row], f'Проверка отчета. Строка {row} ')


async def test_new_check(
        tap, dataset, api, wait_order_status, cfg, job):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    with tap.plan(49, 'Создан check после создания акта'):
        cfg.set('business.order.acceptance.stowage_limit', 0)
        company = await dataset.company(instance_erp='ru')
        store = await dataset.full_store(company=company)

        products = [await dataset.product() for _ in range(3)]

        parent, *weight_products = await dataset.weight_products()
        products.append(weight_products[0])

        assortment = await dataset.assortment_contractor(store=store)

        user = await dataset.user(store=store)

        right_report = []

        for number, product in enumerate(products, start=1):
            right_report.append({
                'product_id': product.product_id,
                'price': None,
                'count': number*2,
                'result_count': number*2,
                'trash': 0,
                'correction': 0,
                'result_delta': 0,
                'delta': 0
            })

        right_report[3]['count'] = None
        right_report[3]['delta'] = 8
        right_report[3]['result_delta'] = 8
        right_report[3]['weight'] = 8
        right_report.append({
            'product_id': parent.product_id,
            'price': None,
            'count': 8,
            'result_count': 0,
            'trash': 0,
            'correction': 0,
            'result_delta': -8,
            'delta': -8
        })

        acceptance_order = await dataset.order(
            store=store,
            acks=[user.user_id],
            type='acceptance',
            required=[
                {
                  'product_id': products[0].product_id,
                  'count': 2
                },
                {
                    'product_id': products[1].product_id,
                    'count': 4
                },
                {
                    'product_id': products[2].product_id,
                    'count': 6
                },
                {
                    'product_id': parent.product_id,
                    'count': 8,
                    'weight': 8
                }
            ],
            attr={'contractor_id': assortment.contractor_id},
            status='reserving',
        )

        await wait_order_status(
            acceptance_order, ('complete', 'done'), user_done=user)

        for stowage_order_id in acceptance_order.vars['stowage_id']:
            stowage_order = await dataset.Order.load(stowage_order_id)

            await wait_order_status(stowage_order, ('request', 'waiting'))

            tap.ok(
                await stowage_order.ack(user=user),
                'взяли в работу stowage'
            )

            await wait_order_status(stowage_order, ('processing', 'waiting'))

            tap.ok(
                await stowage_order.signal({'type': 'sale_stowage'}),
                'сигнал'
            )

            if stowage_order.type == 'weight_stowage':
                suggests = await dataset.Suggest.list_by_order(stowage_order)
                with suggests[0] as s:
                    tap.ok(await s.done(
                        count=8,
                        weight=8,
                        product_id=products[3].product_id
                    ), 'завершён')

            await wait_order_status(
                stowage_order,
                ('complete', 'done'),
                user_done=user
            )

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': acceptance_order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Обновили ассортимент поставщика
        await job.call(await job.take())

        # Генерируем акт
        await job.call(await job.take())

        name = f'orders_acceptance_report-{acceptance_order.order_id}'
        stash = await dataset.Stash.load(name, by='name')
        tap.is_ok(stash, None, 'Нет стэша')

        name_stash_report = f'acceptance_report-{acceptance_order.order_id}'
        stash_report = await dataset.Stash.load(name_stash_report, by='name')

        report = stash_report.value.get('report')
        tap.ok(report, 'Отчет сгенерирован')

        right_report2 = right_report.copy()

        right_report.sort(key=lambda x: x['product_id'])
        report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report):
            if report[row]['product_id'] == parent.product_id:
                tap.eq_ok(
                    report[row].pop('shelf_ids', []), [],
                    'У весового родителя нет полок')
            else:
                tap.ne(report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                field_report, report[row], f'Проверка отчета. Строка {row} ')

        stock = await dataset.Stock.list_by_product(
            product_id=products[0].product_id,
            shelf_type='store',
            store_id=store.store_id,
        )

        check_order = await dataset.order(
            type='check_product_on_shelf',
            products=[products[0].product_id],
            shelves=[stock[0].shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            parent=[acceptance_order.order_id],
        )

        await wait_order_status(check_order, ('request', 'waiting'))
        await check_order.ack(user)

        await wait_order_status(check_order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(check_order)

        with suggests[0] as s:
            tap.ok(await s.done(count=13, valid='02-03-2022'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')

            tap.eq(s.result_count, 13, 'результирующее число')

        tap.ok(await check_order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(check_order, ('complete', 'done'))

        right_report2[0]['correction'] = 11
        right_report2[0]['result_delta'] = 11

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_acceptance_report',
            json={
                'order_id': acceptance_order.order_id
            }
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        # Генерируем акт
        await job.call(await job.take())

        new_stash_report = await dataset.Stash.load(
            name_stash_report, by='name')

        tap.ne_ok(
            new_stash_report.lsn,
            stash_report.lsn,
            'Сгенерирован новый отчет'
        )

        new_report = new_stash_report.value.get('report')
        tap.ok(new_report, 'Отчет получен')

        right_report2.sort(key=lambda x: x['product_id'])
        new_report.sort(key=lambda x: x['product_id'])

        for row, field_report in enumerate(right_report2):
            if new_report[row]['product_id'] == parent.product_id:
                tap.eq_ok(
                    new_report[row].pop('shelf_ids', []), [],
                    'У весового родителя нет полок')
            else:
                tap.ne(
                    new_report[row].pop('shelf_ids', []), [], 'Указаны полки')
            tap.eq(
                new_report[row], field_report,
                f'Проверка отчета. Строка {row}'
            )
