async def test_failed_suggest(tap, dataset, wait_order_status):
    with tap.plan(28, 'failed при закрытии саджеста в error'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stock1 = await dataset.stock(store=store, count=50)
        tap.eq(stock1.store_id, store.store_id, 'остаток 1 создан')

        stock2 = await dataset.stock(store=store, count=60)
        tap.eq(stock2.store_id, store.store_id, 'остаток 2 создан')
        tap.ne(stock2.product_id, stock1.product_id, 'разные товары')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        order = await dataset.order(
            type='hand_move',
            store=store,
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock1.product_id,
                    'count': 20,
                    'src_shelf_id': stock1.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': stock2.product_id,
                    'count': 20,
                    'src_shelf_id': stock2.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')

        for s in suggests:
            if s.product_id == stock1.product_id:
                tap.ok(await s.done(), 'закрыли саджест')
                continue
            tap.ok(await s.done(status='error'), 'саджест в error')

        await wait_order_status(order, ('processing', 'error_resolve'))
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'switched_target'))
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.target, 'failed', 'target стал failed')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(
            len(suggests),
            2,
            'появился зеркальный саджест, error удалились'
        )

        for status in ('done', 'request'):
            tap.eq(
                len([s for s in suggests if s.status == status]),
                1,
                f'саджестов в статусе {status}'
            )

        for s in [s for s in suggests if s.status == 'request']:
            tap.eq(s.conditions.all, False, 'нельзя менять количество')
            tap.eq(s.conditions.error, False, 'нельзя закрывать с ошибкой')
            parent_id = s.vars('parent')

            parents = [s for s in suggests if s.suggest_id == parent_id]
            tap.eq(len(parents), 1, 'родитель найден')
            with parents[0] as p:
                tap.eq(
                    {p.type, s.type},
                    {'box2shelf', 'shelf2box'},
                    'зеркальный тип'
                )

        await wait_order_status(order, ('failed', 'done'), user_done=user)


        tap.ok(await stock1.reload(), 'перегружен сток 1')
        tap.ok(await stock2.reload(), 'перегружен сток 2')

        tap.eq((stock1.count, stock1.reserve), (50, 0), 'количества стока 1')
        tap.eq((stock2.count, stock2.reserve), (60, 0), 'количества стока 2')


async def test_failed_shelf_id(tap, dataset, wait_order_status):
    with tap.plan(8, 'верификация required'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf = await dataset.shelf(store=store)
        kshelf = await dataset.shelf(store=store, type='kitchen_components')
        kshelf2 = await dataset.shelf(store=store, type='kitchen_components')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        kitchen_shelf = await dataset.shelf(
            store=store, type='kitchen_components')
        tap.ok(kitchen_shelf, 'Полка кухни')

        order = await dataset.order(
            store=store,
            type='hand_move',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 34,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'src_shelf_id': shelf.shelf_id,
                    'count': 20,
                },
                {
                    'product_id': product.product_id,
                    'dst_shelf_id': shelf.shelf_id,
                    'count': 20,
                },
                {
                    'product_id': product.product_id,
                    'count': 34,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'count': 300,
                    'src_shelf_id': kshelf.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'count': 300,
                    'src_shelf_id': kshelf.shelf_id,
                    'dst_shelf_id': kshelf2.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'count': 34,
                    'src_shelf_id': shelf.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },

                {
                    'product_id': product.product_id,
                    'count': 34,
                    'src_shelf_id': kitchen_shelf.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()

        shelf_not_found = [
            p for p in order.problems if p.type.endswith('_shelf_not_found')
        ]
        tap.eq(len(shelf_not_found), 2, 'Две ошибки на ненайденные полки')

        problem_types = {p.type for p in order.problems}

        tap.eq(
            problem_types,
            {
                'no_move_detected',
                'required_duplicate',
                'src_shelf_not_found',
                'dst_shelf_not_found',
                'move_quant_to_noquant',
                'move_quant_to_quant',
                'move_diff_shelf_types',
            },
            'Все типы проблем'
        )


async def test_all_steps_fail(tap, dataset, wait_order_status, uuid):
    # pylint: disable=too-many-statements
    with tap.plan(12, 'ошибка одного из 1-3 саджестов'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        shelves = [await dataset.shelf(store=store) for _ in range(2)]
        shelves[1].type = 'kitchen_components'
        await shelves[1].save()
        ps = [await dataset.product() for _ in range(2)]
        for p in ps:
            await dataset.stock(
                shelf=shelves[0], product=p, count=100, lot=uuid()
            )

        order_params = {
            'type': 'hand_move',
            'store': store,
            'acks': [user.user_id],
            'required': [
                {
                    'product_id': p.product_id,
                    'src_shelf_id': shelves[0].shelf_id,
                    'dst_shelf_id': shelves[1].shelf_id,
                    'count': 10,
                }
                for p in ps
            ]
        }

        # фейлимся на s1
        order = await dataset.order(**order_params)
        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 2, '2 саджеста')
        await suggests[0].done(status='error', user=user)
        await wait_order_status(
            order, ('processing', 'switched_target')
        )
        await wait_order_status(
            order, ('processing', 'waiting')
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.ok(not suggests, 'нету зеркальных саджестов')

        await wait_order_status(
            order, ('failed', 'done'), user_done=user
        )

        # фейлимся на s2
        order = await dataset.order(**order_params)
        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user
        )
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, '2 саджеста')
        await suggests[0].done(status='done', user=user)
        await suggests[1].done(status='error', user=user)
        await wait_order_status(
            order, ('processing', 'switched_target')
        )
        await wait_order_status(
            order, ('processing', 'waiting')
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, '1 саджест')
        await wait_order_status(
            order, ('failed', 'done'), user_done=user
        )


async def test_all_steps_fail_not_full(tap, dataset, wait_order_status, uuid):
    # pylint: disable=too-many-statements
    with tap.plan(7, 'ошибка 1-2 саджеста с другим result_count'):
        store = await dataset.store()
        user = await dataset.user(store=store, role='admin')
        shelves = [await dataset.shelf(store=store) for _ in range(2)]
        shelves[1].type = 'kitchen_components'
        await shelves[1].save()
        ps = [await dataset.product() for _ in range(2)]
        for p in ps:
            await dataset.stock(
                shelf=shelves[0], product=p, count=100, lot=uuid()
            )

        order_params = {
            'type': 'hand_move',
            'store': store,
            'acks': [user.user_id],
            'required': [
                {
                    'product_id': p.product_id,
                    'src_shelf_id': shelves[0].shelf_id,
                    'dst_shelf_id': shelves[1].shelf_id,
                    'count': 10,
                }
                for p in ps
            ]
        }

        # фейлимся на s2
        order = await dataset.order(**order_params)
        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user
        )
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, '2 саджеста')
        await suggests[0].done(status='done', count=5, user=user)
        await suggests[1].done(status='error', user=user)
        await wait_order_status(
            order, ('processing', 'switched_target')
        )
        await wait_order_status(
            order, ('processing', 'waiting')
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, '1 саджест')
        tap.eq(suggests[0].count, 5, 'нужный count')
        await wait_order_status(
            order, ('failed', 'done'), user_done=user
        )


async def test_failed_shelf_type_office(tap, dataset, wait_order_status):
    with tap.plan(9, 'перемещения продукта на office и расходника на store'):
        store = await dataset.store(options={'exp_illidan': True})
        tap.ok(store, 'склад создан')

        product = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'product',
                }
            }
        )
        tap.ok(product, 'товар создан')

        consumable = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'consumable',
                }
            }
        )
        tap.ok(consumable, 'расходник создан')

        shelf_store = await dataset.shelf(store=store)
        shelf_office = await dataset.shelf(store=store, type='office')

        order = await dataset.order(
            store=store,
            type='hand_move',
            required=[
                {
                    'product_id': product.product_id,
                    'count': 1,
                    'src_shelf_id': shelf_store.shelf_id,
                    'dst_shelf_id': shelf_office.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()

        problem_types = {p.type for p in order.problems}

        tap.eq(
            problem_types,
            {
                'non_consumable_product_to_office',
            },
            'Все типы проблем'
        )

        order = await dataset.order(
            store=store,
            type='hand_move',
            required=[
                {
                    'product_id': consumable.product_id,
                    'count': 1,
                    'src_shelf_id': shelf_office.shelf_id,
                    'dst_shelf_id': shelf_store.shelf_id,
                },
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('failed', 'done'))
        await order.reload()

        problem_types = {p.type for p in order.problems}

        tap.eq(
            problem_types,
            {
                'non_consumable_product_to_office',
            },
            'Все типы проблем'
        )

