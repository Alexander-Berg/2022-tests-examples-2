async def test_no_change_stage(tap, dataset, wait_order_status):
    with tap.plan(9, 'с экспериментом не меняется стадия'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        user = await dataset.user(store=store)
        product1 = await dataset.product()
        product2 = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {'product_id': product1.product_id, 'count': 23},
                {'product_id': product2.product_id, 'count': 23},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'stowage', 'стадия stowage')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'два саджеста')
        tap.ok(await suggests[0].done(count=23), 'закрыли один саджест')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        for _ in range(3):
            await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'stowage', 'все еще stowage')


async def test_happy_flow(tap, dataset, wait_order_status):
    with tap.plan(17, 'хеппи флоу, часть кладем на треш'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(await suggests[0].done(count=13), 'разложили 13')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 10, 'осталось 10')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 10, 'осталось 10')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.ok(await suggests[0].done(count=10), 'списали 10')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks_store = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='store',
        )
        tap.eq(len(stocks_store), 1, 'один сток')
        tap.eq(stocks_store[0].count, 13, 'количество 13')
        stocks_trash = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='trash',
        )
        tap.eq(len(stocks_trash), 1, 'один сток')
        tap.eq(stocks_trash[0].count, 10, 'количество 10')


async def test_all_trash(tap, dataset, wait_order_status):
    with tap.plan(13, 'хеппи флоу, кладем все на треш'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 23, 'тот же count')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 23, 'count тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.ok(await suggests[0].done(count=23), 'кладем все на треш')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks_store = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='store',
        )
        tap.eq(len(stocks_store), 0, 'нету стоков')
        stocks_trash = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='trash',
        )
        tap.eq(len(stocks_trash), 1, 'один сток')
        tap.eq(stocks_trash[0].count, 23, 'все списано')


async def test_part_exp_1(tap, dataset, wait_order_status):
    # pylint: disable=too-many-locals,too-many-statements
    with tap.plan(25, 'выключаем эксп не переведя все саджесты в треш'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        product2 = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {'product_id': product.product_id, 'count': 23},
                {'product_id': product2.product_id, 'count': 25},
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        suggests = [s for s in suggests if s.product_id == product.product_id]
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        suggest_pr2 = [
            s for s in suggests if s.product_id == product2.product_id
        ][0]
        suggest_pr2_old_id = suggest_pr2.suggest_id
        suggests = [s for s in suggests if s.product_id == product.product_id]
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 23, 'count тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')

        store_options = store.options.copy()
        store_options['exp_freegan_party'] = False
        store.options = store_options
        await store.save()
        await store.reload()
        tap.ok(not store.options['exp_freegan_party'], 'выключили эксперимент')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'стадия списания')
        old_suggest_id = suggests[0].suggest_id
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 2, 'два саджеста')
        suggest_pr1 = [
            s for s in suggests if s.product_id == product.product_id
        ][0]
        suggest_pr2 = [
            s for s in suggests if s.product_id == product2.product_id
        ][0]
        tap.eq(suggest_pr1.count, 23, 'count тот же')
        tap.eq(suggest_pr1.shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.ok(
            suggest_pr1.suggest_id == old_suggest_id,
            'саджест треш саджест тот же',
        )

        tap.eq(suggest_pr2.count, 25, 'count тот же')
        tap.eq(suggest_pr2.shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.ok(
            suggest_pr2.suggest_id == suggest_pr2_old_id,
            'саджест по второму продукту тот же',
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks_store = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='store',
        )
        tap.eq(len(stocks_store), 0, 'нет стоков')
        stocks_trash = await dataset.Stock.list_by_shelf(
            shelf_id=trash_shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks_trash), 2, 'два стока')
        stocks_trash = sorted(stocks_trash, key=lambda s: s.count)
        tap.eq(stocks_trash[0].product_id, product.product_id, '1 продукт')
        tap.eq(stocks_trash[0].count, 23, '23 списано')
        tap.eq(stocks_trash[1].product_id, product2.product_id, '2 продукт')
        tap.eq(stocks_trash[1].count, 25, '25 списано')


async def test_part_exp_2(tap, dataset, wait_order_status):
    with tap.plan(20, 'выключаем эксп переведя все саджесты в треш'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 23, 'count тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')

        store_options = store.options.copy()
        store_options['exp_freegan_party'] = False
        store.options = store_options
        await store.save()
        await store.reload()
        tap.ok(not store.options['exp_freegan_party'], 'выключили эксперимент')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'стадия списания')
        old_suggest_id = suggests[0].suggest_id
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджеста')
        tap.eq(suggests[0].count, 23, 'count тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.ok(
            suggests[0].suggest_id == old_suggest_id,
            'саджест треш саджест тот же',
        )

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks_store = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='store',
        )
        tap.eq(len(stocks_store), 0, 'нет стоков')
        stocks_trash = await dataset.Stock.list_by_shelf(
            shelf_id=trash_shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks_trash), 1, 'один сток')
        tap.eq(stocks_trash[0].product_id, product.product_id, '1 продукт')
        tap.eq(stocks_trash[0].count, 23, '23 списано')


async def test_not_all_trash(tap, dataset, wait_order_status):
    with tap.plan(25, 'проверяем что можно положить не все'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        old_suggest_id = suggests[0].suggest_id
        tap.eq(suggests[0].count, 23, 'count тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.ok(suggests[0].vars.get('old_conditions'), 'есть старые кондишны')

        store_options = store.options.copy()
        store_options['exp_freegan_party'] = False
        store.options = store_options
        await store.save()
        await store.reload()
        tap.ok(not store.options['exp_freegan_party'], 'выключили эксперимент')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].suggest_id, old_suggest_id, 'тот же саджест')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')

        tap.ok(await suggests[0].done(count=22), 'списали все кроме 1')
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 0, 'нет саджестов')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'стадия списания')
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 0, 'нет саджестов')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks_store = await dataset.Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type='store',
        )
        tap.eq(len(stocks_store), 0, 'нет стоков')
        stocks_trash = await dataset.Stock.list_by_shelf(
            shelf_id=trash_shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks_trash), 1, 'один сток')
        tap.eq(stocks_trash[0].product_id, product.product_id, '1 продукт')
        tap.eq(stocks_trash[0].count, 22, '22 списано')


async def test_untrashify_suggest(tap, dataset, wait_order_status):
    # pylint: disable=too-many-statements
    with tap.plan(45, 'пробуем гонять саджест по типам туда-сюда'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash'
        )
        store_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='store'
        )
        user = await dataset.user(store=store)
        product = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[{'product_id': product.product_id, 'count': 23}],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].shelf_id, store_shelf.shelf_id, 'на полку store')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF, на треш'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'на полку trash')
        tap.eq(suggests[0].vars('stage'), 'trash', 'стадия саджеста trash')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.note('тут мы передумали и хотим все-таки что-то разложить')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': store_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF, на стор'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].shelf_id, store_shelf.shelf_id, 'на полку store')
        tap.eq(suggests[0].vars('stage'), 'stowage', 'стадия саджеста stowage')
        tap.ok(await suggests[0].done(count=3), 'разложили 3 штучки')
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].count, 20, 'осталось 23-3=20 штучек')
        tap.eq(suggests[0].shelf_id, store_shelf.shelf_id, 'на полку store')

        tap.note('теперь мы "уверены" что все разложили и снова меняем полку')
        tap.ok(
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': trash_shelf.shelf_id,
                },
            ),
            'закрыли саджест в ошибку с LIKE_SHELF, на треш'
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        old_suggest_id = suggests[0].suggest_id
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'на полку trash')

        store_options = store.options.copy()
        store_options['exp_freegan_party'] = False
        store.options = store_options
        await store.save()
        await store.reload()
        tap.ok(not store.options['exp_freegan_party'], 'выключили эксперимент')
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].suggest_id, old_suggest_id, 'айди тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.eq(suggests[0].count, 20, 'осталось по-прежнему 20 штучек')

        tap.ok(await order.signal({'type': 'sale_stowage'}), 'сигнал послан')
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'стадия списания')
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        tap.eq(suggests[0].suggest_id, old_suggest_id, 'айди тот же')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'треш полка')
        tap.eq(suggests[0].count, 20, 'осталось по-прежнему 20 штучек')

        tap.note('тут мы поняли что опять забыли че-то разложить, идем взад')
        with tap.raises(dataset.Suggest.ErSuggestErrorDenided):
            await suggests[0].done(
                status='error',
                reason={
                    'code': 'LIKE_SHELF',
                    'shelf_id': store_shelf.shelf_id,
                },
            )
        tap.note('а нельзя уже, поздно метаться, списывай')

        tap.ok(await suggests[0].done(count=17), 'списали 17')
        await wait_order_status(order, ('complete', 'done'), user_done=user)
        stocks_store = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=store_shelf.shelf_id,
        )
        tap.eq(len(stocks_store), 1, 'один сток')
        tap.eq(stocks_store[0].product_id, product.product_id, '1 продукт')
        tap.eq(stocks_store[0].count, 3, '3 разложено')
        stocks_trash = await dataset.Stock.list_by_shelf(
            shelf_id=trash_shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks_trash), 1, 'один сток')
        tap.eq(stocks_trash[0].product_id, product.product_id, '1 продукт')
        tap.eq(stocks_trash[0].count, 17, '17 списано')


async def test_done_zero_mb_count(tap, dataset, wait_order_status):
    # pylint: disable=too-many-locals
    with tap.plan(29, 'проверяем закрытие саджеста в 0'):
        store = await dataset.full_store(options={'exp_freegan_party': True})
        trash_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='trash',
        )
        store_shelf = await dataset.Shelf.get_one(
            store_id=store.store_id, type='store',
        )
        user = await dataset.user(store=store)
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        order = await dataset.order(
            store=store,
            type='sale_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 23,
                    'maybe_count': True,
                },
                {
                    'product_id': product2.product_id,
                    'count': 23,
                    'maybe_count': True,
                },
                {
                    'product_id': product3.product_id,
                    'count': 23,
                    'maybe_count': True,
                },
                {
                    'product_id': product4.product_id,
                    'count': 23,
                    'maybe_count': True,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, '4 саджеста')
        suggests.sort(key=lambda x: x.product_id)
        tap.eq(suggests[0].shelf_id, store_shelf.shelf_id, 'на полку store')
        tap.ok(await suggests[0].done(count=3, user=user), 'закрыли в 3')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 4, '4 саджеста')
        suggests.sort(key=lambda x: x.product_id)
        tap.eq(suggests[0].shelf_id, store_shelf.shelf_id, 'на полку store')
        tap.eq(suggests[0].count, 20, 'осталось 20')
        tap.ok(await suggests[0].done(count=0, user=user), 'закрыли в 0')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 3, 'осталось 3 саджеста')
        suggests.sort(key=lambda x: x.product_id)
        tap.ok(await suggests[0].done(count=0, user=user), 'закрыли в 0')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 2, 'осталось два саджеста')
        for s in suggests:
            tap.ok(
                await s.done(
                    status='error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': trash_shelf.shelf_id,
                    },
                ),
                'закрыли саджест в ошибку с LIKE_SHELF, на треш'
            )
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 2, 'все еще два саджеста')
        tap.eq(suggests[0].shelf_id, trash_shelf.shelf_id, 'на треш')
        tap.ok(await suggests[0].done(count=0, user=user), 'закрыли в 0')
        tap.eq(suggests[1].shelf_id, trash_shelf.shelf_id, 'на треш')
        tap.ok(await suggests[1].done(count=3, user=user), 'закрыли в 3')
        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 0, 'нет больше саджестов')
        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks_store = await dataset.Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=store_shelf.shelf_id,
        )
        tap.eq(len(stocks_store), 1, 'один сток')
        tap.eq(stocks_store[0].count, 3, 'положили 3 штучки')
        stocks_trash = await dataset.Stock.list_by_shelf(
            shelf_id=trash_shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks_trash), 2, 'два стока')
        tap.eq(sorted([s.count for s in stocks_trash]), [0, 3], '0 и 3')
