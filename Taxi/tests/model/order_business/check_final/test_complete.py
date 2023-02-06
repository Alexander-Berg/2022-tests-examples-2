from stall.model.suggest import Suggest


async def test_check_final_success(tap, dataset, wait_order_status, uuid):
    with tap.plan(4, 'тестим полный цикл ордера'):
        product = await dataset.product()
        store = await dataset.full_store()
        shelf = await dataset.shelf(store=store)
        user = await dataset.user(store=store)

        for _ in range(2):
            await dataset.stock(
                shelf=shelf, product=product, count=123, lot=uuid()
            )

        order = await dataset.order(
            type='check_final',
            store=store,
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                }
            ],
            acks=[user.user_id],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )
        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест')

        await wait_order_status(
            order, ('complete', 'done'), user_done=user,
        )

        children = await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )
        tap.eq(len(children.list), 0, 'Дочерних ордеров не появилось')


async def test_check_final_error(tap, dataset, wait_order_status, uuid):
    with tap.plan(12, 'закрываем саджест с ошибкой и генерим новый ордер'):
        ps = [await dataset.product() for _ in range(2)]
        store = await dataset.full_store()
        shelf = await dataset.shelf(store=store)
        user = await dataset.user(store=store)

        for p in ps:
            await dataset.stock(
                shelf=shelf, product=p, count=123, lot=uuid()
            )

        order = await dataset.order(
            type='check_final',
            store=store,
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': p.product_id,
                }
                for p in ps
            ],
            acks=[user.user_id],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )

        suggests = await Suggest.list_by_order(order)

        tap.eq(len(suggests), 2, '2 саджеста')
        await dataset.stock(shelf=shelf, product=ps[1], count=321, lot=uuid())
        for s in suggests:
            if s.product_id == ps[1].product_id:
                continue
            await s.done(count=69, user=user)

        await wait_order_status(
            order, ('complete', 'done'), user_done=user,
        )

        children = await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )
        tap.eq(len(children.list), 1, 'появился дочерний ордер')

        child = children.list[0]
        await wait_order_status(
            child, ('reserving', 'find_lost_and_found'), user_done=user,
        )

        tap.eq(
            child.shelves,
            [shelf.shelf_id],
            'нужные полки',
        )
        tap.eq(
            child.products,
            [ps[1].product_id],
            'нужные продукты',
        )
        tap.eq(child.type, 'check_final', 'директорский чек')
        await wait_order_status(
            child, ('request', 'waiting'), user_done=user,
        )
        tap.ok(await child.ack(user), 'назначили юзера')

        await wait_order_status(
            child, ('complete', 'done'), user_done=user,
        )

        children = await order.list(
            by='full',
            conditions=('parent', '[1]=', child.order_id),
            sort=(),
        )
        tap.eq(len(children.list), 0, 'нет дочерних ордеров')
