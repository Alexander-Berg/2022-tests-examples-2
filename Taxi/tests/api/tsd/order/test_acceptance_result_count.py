from datetime import timedelta
from pytz import all_timezones as all_tzs


# pylint: disable=too-many-statements,too-many-locals
async def test_all(tap, dataset, api, uuid, now, wait_order_status):
    with tap:
        store = await dataset.full_store()
        user = await dataset.user(
            store=store,
            role='executer',
        )

        t = await api(user=user)

        stock = await dataset.stock(store=store, count=5)
        tap.eq(stock.count, 5, 'создали остаток')

        acceptance = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            attr={
                'doc_number': '11111-22222',
                'contractor': uuid(),
                'doc_date': now().strftime('%F')
            },
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 7,
                    'valid': now() + timedelta(days=1),
                },
            ],
        )
        tap.ok(acceptance, 'создали приемку с тем же товаром')

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Acceptance is not completed')

        await wait_order_status(
            acceptance, ('complete', 'done'), user_done=user,
        )

        stowages = (
            await dataset.Order.list(
                by='full',
                conditions=('parent', '[1]=', acceptance.order_id),
                sort=(),
            )
        ).list
        tap.eq(len(stowages), 1, 'есть деть')

        stowage = stowages[0]
        tap.eq(stowage.type, 'sale_stowage', 'деть есть раскладка')

        stowage.acks = [user.user_id]
        stowage.approved = now()
        await stowage.save()

        await wait_order_status(stowage, ('processing', 'waiting'))

        stowage_suggests = await dataset.Suggest.list_by_order(stowage)
        tap.eq(len(stowage_suggests), 1, 'есть один саджест на раскладку')
        tap.ok(await stowage_suggests[0].done(), 'закрыли саджест')

        tap.ok(
            await stowage.signal({'type': 'sale_stowage'}),
            'сигнал завершения раскладки отправлен',
        )

        await wait_order_status(stowage, ('processing', 'waiting'))
        await wait_order_status(stowage, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=stock.product_id,
        )
        tap.eq(sum(s.left for s in stocks), 5 + 7, 'всего товара')

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': stowage.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_like('message', 'Wrong order type:')

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', stock.product_id)
        t.json_is('result_count', 7)
        t.json_is('available_to_recount', None)

        order = await dataset.order(
            store=store,
            type='order',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 6,
                },
            ],
        )
        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', stock.product_id)
        t.json_is('result_count', 7)
        t.json_is('available_to_recount', None)

        check = await dataset.order(
            type='check_product_on_shelf',
            parent=[acceptance.order_id],
            products=[stock.product_id],
            shelves=[stock.shelf_id],
            status='processing',
            estatus='begin',
            store_id=store.store_id,
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': stock.product_id,
                },
            ],
        )
        await wait_order_status(check, ('processing', 'waiting'))

        check_suggests = await dataset.Suggest.list_by_order(check)
        tap.eq(len(check_suggests), 1, 'саджесты на проверку')

        with check_suggests[0] as s:
            tap.ok(
                await s.done(count=3, valid=now() + timedelta(days=1)),
                'закрыли саджест на чек в минус',
            )

        await wait_order_status(check, ('complete', 'done'), user_done=user)
        tap.eq(check.fstatus, ('complete', 'done'), 'закрыли проверку')

        tap.ok(check.vars('child'), 'создали детя из-за конфликта')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
        tap.eq(order.fstatus, ('complete', 'done'), 'закрыли клиентский заказ')

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=stock.product_id,
        )
        tap.eq(
            sum(s.left for s in stocks),
            5 + 7 - 6, 'осталось товара после продажи',
        )

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'Acceptance child is not completed')

        child_check = await dataset.Order.load(check.vars('child'))
        child_check.acks = [user.user_id]
        await child_check.save()

        await wait_order_status(child_check, ('processing', 'waiting'))

        child_check_suggests = await dataset.Suggest.list_by_order(child_check)
        tap.eq(len(child_check_suggests), 1, 'саджесты на проверку 2')

        with child_check_suggests[0] as s:
            tap.ok(
                await s.done(count=3, valid=now() + timedelta(days=1)),
                'закрыли саджест на проверку 2',
            )

        await wait_order_status(
            child_check, ('complete', 'done'), user_done=user,
        )

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=stock.product_id,
        )
        tap.eq(
            sum(s.left for s in stocks), 3, 'осталось товара после продажи',
        )

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', stock.product_id)
        t.json_is('result_count', 4)
        t.json_is('available_to_recount', None)


# pylint: disable=too-many-statements,too-many-locals
async def test_product_not_in_acceptance(
        tap, dataset, api, uuid, now, wait_order_status,
):
    with tap:
        store = await dataset.full_store()
        user = await dataset.user(
            store=store,
            role='executer',
        )

        product = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        acceptance = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            attr={
                'doc_number': '11111-22222',
                'contractor': uuid(),
                'doc_date': now().strftime('%F')
            },
            required=[
                {
                    'product_id': product.product_id,
                    'count': 7,
                    'valid': now() + timedelta(days=1),
                },
            ],
        )
        tap.ok(acceptance, 'создали приемку с тем же товаром')

        await wait_order_status(
            acceptance, ('complete', 'done'), user_done=user,
        )

        stowages = (
            await dataset.Order.list(
                by='full',
                conditions=('parent', '[1]=', acceptance.order_id),
                sort=(),
            )
        ).list
        tap.eq(len(stowages), 1, 'есть дети')

        with stowages[0] as stowage:
            tap.eq(stowage.type, 'sale_stowage', 'раскладка')

            stowage.acks = [user.user_id]
            stowage.approved = now()
            await stowage.save()

            await wait_order_status(stowage, ('processing', 'waiting'))

            tap.ok(
                await dataset.suggest(
                    stowage,
                    count=3,
                    product=product2,
                    vars={'mode': 'product', 'stage': 'store'},
                ),
                'имитируем more_product',
            )

            stowage_suggests = await dataset.Suggest.list_by_order(stowage)
            tap.eq(len(stowage_suggests), 2, 'есть саджесты на раскладку')
            tap.ok(await stowage_suggests[0].done(), 'закрыли саджест')

            tap.ok(
                await stowage.signal({'type': 'sale_stowage'}),
                'сигнал завершения раскладки отправлен',
            )

            await wait_order_status(stowage, ('processing', 'waiting'))
            await wait_order_status(
                stowage, ('complete', 'done'), user_done=user,
            )

        stocks = {
            s.product_id: s
            for s in await dataset.Stock.list_by_product(
                product_id=(product.product_id, product2.product_id),
                store_id=store.store_id,
            )
        }
        tap.eq(len(stocks), 2, 'два товара на остатках')
        tap.eq(stocks[product.product_id].left, 7, 'остаток для первого')
        tap.eq(stocks[product2.product_id].left, 3, 'остаток для второго')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', product.product_id)
        t.json_is('result_count', 7)
        t.json_is('available_to_recount', None)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': product2.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', product2.product_id)
        t.json_is('result_count', 3)
        t.json_is('available_to_recount', None)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': product3.product_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')


async def test_time_limit(tap, api, dataset, cfg, now, tzone):
    # взято из load_data
    str_tz = next(i for i in all_tzs if now(tz=tzone(i)).hour not in [23, 0])
    tz = tzone(str_tz)

    before_now = now(tz=tz) - timedelta(minutes=2)
    after_now = now(tz=tz) + timedelta(minutes=2)
    before_now = f'{before_now.hour}:{before_now.minute}'
    after_now = f'{after_now.hour}:{after_now.minute}'
    cfg.set('business.order.acceptance.last_stowage_time_limit', before_now)

    with tap.plan(8, 'заказ с разными time_limit'):
        user = await dataset.user(role='admin', tz=str_tz)

        product = await dataset.product(store_id=user.store_id)

        parent_order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 666,
                 },
            ],
            type='acceptance',
            status='complete',
            estatus='done'
        )
        tap.ok(parent_order, 'создали родителя')

        child_order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='sale_stowage',
            updated=str(now(tz) - timedelta(days=1)),
            parent=[parent_order.order_id],
        )
        tap.ok(child_order, 'создали дочку')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': parent_order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        cfg.set('business.order.acceptance.last_stowage_time_limit', after_now)
        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': parent_order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'stowage свежий')


async def test_allow_another_user(tap, api, dataset):
    with tap.plan(5, 'разрешаем доступ к ордеру от другого юзера'):
        user1 = await dataset.user(role='admin')

        product = await dataset.product(store_id=user1.store_id)

        parent_order = await dataset.order(
            users=[user1.user_id],
            store_id=user1.store_id,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 666,
                },
            ],
            type='acceptance',
            status='complete',
            estatus='done'
        )
        tap.ok(parent_order, 'создали родителя')

        child_order = await dataset.order(
            users=[user1.user_id],
            store_id=user1.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='sale_stowage',
            parent=[parent_order.order_id],
        )
        tap.ok(child_order, 'создали дочку')

        user2 = await dataset.user(
            store_id=user1.store_id,
            role='executer',
        )

        tap.ok(
            user2.user_id not in parent_order.users, 'юзера нет в ордере',
        )

        t = await api(user=user2)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': parent_order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)


async def test_weight_product(tap, dataset, api):
    with tap.plan(4, 'проверка работы приемки для весового товара'):

        store = await dataset.full_store()
        user = await dataset.user(
            store=store,
            role='executer',
        )

        product = await dataset.product(
            store_id=user.store_id,
            type_accounting='weight',
        )
        t = await api(user=user)

        parent_order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[
                {'product_id': product.product_id},
            ],
            type='acceptance',
            status='complete',
            estatus='done'
        )

        await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='weight_stowage',
            parent=[parent_order.order_id],
        )

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': parent_order.order_id,
                'product_id': product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('available_to_recount', None)


# pylint: disable=too-many-statements,too-many-locals
async def test_family(tap, dataset, api, uuid, now, wait_order_status):
    with tap.plan(30, 'пересчитываем дочерний продукт'):
        store = await dataset.full_store()
        user = await dataset.user(
            store=store,
            role='executer',
        )

        t = await api(user=user)

        product = await dataset.product()
        child_product = await dataset.product(parent_id=product.product_id)

        stock = await dataset.stock(
            store=store,
            product=product,
            count=5,
        )
        tap.eq(stock.count, 5, 'создали остаток')

        acceptance = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            attr={
                'doc_number': '11111-22222',
                'contractor': uuid(),
                'doc_date': now().strftime('%F')
            },
            required=[
                {
                    'product_id': product.product_id,
                    'count': 7,
                    'valid': now() + timedelta(days=1),
                },
            ],
        )
        tap.ok(acceptance, 'создали приемку с тем же товаром')

        await wait_order_status(
            acceptance, ('complete', 'done'), user_done=user,
        )

        stowages = (
            await dataset.Order.list(
                by='full',
                conditions=('parent', '[1]=', acceptance.order_id),
                sort=(),
            )
        ).list
        tap.eq(len(stowages), 1, 'есть деть')

        stowage = stowages[0]
        tap.eq(stowage.type, 'sale_stowage', 'деть есть раскладка')

        stowage.acks = [user.user_id]
        stowage.approved = now()
        await stowage.save()

        await wait_order_status(stowage, ('processing', 'waiting'))

        stowage_suggests = await dataset.Suggest.list_by_order(stowage)
        tap.eq(len(stowage_suggests), 1, 'есть один саджест на раскладку')
        tap.ok(await stowage_suggests[0].done(), 'закрыли саджест')

        tap.ok(
            await stowage.signal({'type': 'sale_stowage'}),
            'сигнал завершения раскладки отправлен',
        )

        await wait_order_status(stowage, ('processing', 'waiting'))
        await wait_order_status(stowage, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=product.product_id,
        )
        tap.eq(sum(s.left for s in stocks), 5 + 7, 'всего товара')

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': stock.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', stock.product_id)
        t.json_is('result_count', 7)
        t.json_is('available_to_recount', None)

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': child_product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', child_product.product_id)
        t.json_is('result_count', 7)
        t.json_is('available_to_recount', None)

        check = await dataset.order(
            type='check_product_on_shelf',
            parent=[acceptance.order_id],
            products=[child_product.product_id],
            shelves=[stock.shelf_id],
            status='processing',
            estatus='begin',
            store_id=store.store_id,
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': child_product.product_id,
                },
            ],
        )
        await wait_order_status(check, ('processing', 'waiting'))

        check_suggests = await dataset.Suggest.list_by_order(check)
        tap.eq(len(check_suggests), 1, 'саджесты на проверку')

        with check_suggests[0] as s:
            tap.ok(
                await s.done(count=3, valid=now() + timedelta(days=1)),
                'пересчитали дочерний товар',
            )

        await wait_order_status(check, ('complete', 'done'), user_done=user)
        tap.eq(check.fstatus, ('complete', 'done'), 'закрыли проверку')

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=child_product.product_id,
        )
        tap.eq(sum(s.left for s in stocks), 3, 'всего товара')


# pylint: disable=too-many-statements,too-many-locals
async def test_family_no_stowage(tap, dataset, api, now, wait_order_status):
    with tap.plan(26, 'пересчитываем дочерний продукт без размещения'):
        store = await dataset.full_store()
        contractor = await dataset.assortment_contractor(
            store_id=store.store_id,
        )
        user = await dataset.user(
            store=store,
            role='executer',
        )

        t = await api(user=user)

        product = await dataset.product()
        child_product = await dataset.product(parent_id=product.product_id)
        await dataset.assortment_contractor_product(
            assortment=contractor,
            product=product,
            status='active',
        )

        stock = await dataset.stock(
            store=store,
            product=product,
            count=5,
        )
        tap.eq(stock.count, 5, 'создали остаток')

        acceptance = await dataset.order(
            store=store,
            type='acceptance',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            attr={
                'doc_number': '11111-22222',
                'contractor_id': contractor.contractor_id,
                'doc_date': now().strftime('%F')
            },
            required=[
                {
                    'product_id': product.product_id,
                    'count': 7,
                    'valid': now() + timedelta(days=1),
                },
            ],
        )
        tap.ok(acceptance, 'создали приемку с тем же товаром')

        await wait_order_status(
            acceptance, ('complete', 'done'), user_done=user,
        )

        stowages = (
            await dataset.Order.list(
                by='full',
                conditions=('parent', '[1]=', acceptance.order_id),
                sort=(),
            )
        ).list
        tap.eq(len(stowages), 1, 'есть деть')

        stowage = stowages[0]
        tap.eq(stowage.type, 'sale_stowage', 'деть есть раскладка')

        stowage.acks = [user.user_id]
        stowage.approved = now()
        await stowage.save()

        await wait_order_status(stowage, ('processing', 'waiting'))

        stowage_suggests = await dataset.Suggest.list_by_order(stowage)
        tap.eq(len(stowage_suggests), 1, 'есть один саджест на раскладку')
        tap.ok(await stowage_suggests[0].done(count=0), 'закрыли саджест')

        tap.ok(
            await stowage.signal({'type': 'sale_stowage'}),
            'сигнал завершения раскладки отправлен',
        )

        await wait_order_status(stowage, ('processing', 'waiting'))
        await wait_order_status(stowage, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=product.product_id,
        )
        tap.eq(sum(s.left for s in stocks), 5, 'всего товара')

        await t.post_ok(
            'api_tsd_order_acceptance_result_count',
            json={
                'order_id': acceptance.order_id,
                'product_id': child_product.product_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_id', child_product.product_id)
        t.json_is('result_count', 0)
        t.json_is('available_to_recount', None)

        check = await dataset.order(
            type='check_product_on_shelf',
            parent=[acceptance.order_id],
            products=[child_product.product_id],
            shelves=[stock.shelf_id],
            status='reserving',
            estatus='find_lost_and_found',
            store_id=store.store_id,
            required=[
                {
                    'shelf_id': stock.shelf_id,
                    'product_id': child_product.product_id,
                },
            ],
        )
        await wait_order_status(check, ('request', 'waiting'))

        tap.ok(
            await check.ack(user=user),
            'взяли в работу проверку'
        )

        await wait_order_status(check, ('processing', 'waiting'))

        check_suggests = await dataset.Suggest.list_by_order(check)
        tap.eq(len(check_suggests), 1, 'саджесты на проверку')

        with check_suggests[0] as s:
            tap.ok(
                await s.done(count=3, valid=now() + timedelta(days=1)),
                'пересчитали дочерний товар',
            )

        await wait_order_status(check, ('complete', 'done'), user_done=user)
        tap.eq(check.fstatus, ('complete', 'done'), 'закрыли проверку')

        stocks = await dataset.Stock.list_by_product(
            store_id=store.store_id,
            product_id=child_product.product_id,
        )
        tap.eq(sum(s.left for s in stocks), 3, 'всего товара')
