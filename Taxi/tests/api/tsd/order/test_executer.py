import pytest


@pytest.mark.parametrize('role', ['barcode_executer', 'executer'])
async def test_executer_link_unlink(tap, dataset, api, role):
    with tap.plan(9, 'Нет изменений'):
        user = await dataset.user(role=role)
        tap.eq(user.role, 'executer', 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')

        order = await dataset.order(
            status='processing',
            users=[user.user_id],
            store_id=user.store_id,
        )

        link_user = await dataset.user(store_id=user.store_id)
        tap.eq(link_user.store_id, user.store_id, 'пользователь создан')

        tap.eq(order.store_id, user.store_id, 'заказ на складе создан')
        tap.eq(order.status, 'processing', 'статус')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_executer',
                        json={
                            'order_id': order.order_id,
                            'link': [link_user.user_id],
                            'unlink': [user.user_id],
                        })
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(set(order.users),
               set([link_user.user_id]),
               'изменились пользователи')


@pytest.mark.parametrize('role', ['barcode_executer', 'executer'])
async def test_executer_no_change(tap, dataset, api, role):
    with tap.plan(8, 'Нет изменений'):
        user = await dataset.user(role=role)
        tap.eq(user.role, 'executer', 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')

        order = await dataset.order(
            status='processing',
            users=[user.user_id],
            store_id=user.store_id,
        )

        tap.eq(order.store_id, user.store_id, 'заказ на складе создан')
        tap.eq(order.status, 'processing', 'статус')

        t = await api(user=user)
        revision = order.revision

        await t.post_ok('api_tsd_order_executer',
                        json={'order_id': order.order_id, 'link': order.users})
        t.status_is(200, diag=True)
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.revision, revision, 'ордер не менялся')


@pytest.mark.parametrize('role', ['barcode_executer', 'executer'])
async def test_executer_unlink_all(tap, dataset, api, role):
    with tap.plan(10, 'Нет изменений'):
        user = await dataset.user(role=role)
        tap.eq(user.role, 'executer', 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')

        order = await dataset.order(
            status='processing',
            users=[user.user_id],
            store_id=user.store_id,
        )

        tap.eq(order.store_id, user.store_id, 'заказ на складе создан')
        tap.eq(order.status, 'processing', 'статус')

        t = await api(user=user)
        revision = order.revision

        await t.post_ok('api_tsd_order_executer',
                        json={
                            'order_id': order.order_id,
                            'unlink': order.users
                        })
        t.status_is(410, diag=True)
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.revision, revision, 'ордер не менялся')
        t.json_is('code', 'ER_EXECUTER_REQUIRED')
        t.json_is('message', 'One executer required at least')


@pytest.mark.parametrize('role', ['barcode_executer', 'executer'])
async def test_executer_unknown_users(tap, dataset, api, role, uuid):
    with tap.plan(11, 'Нет изменений'):
        user = await dataset.user(role=role)
        tap.eq(user.role, 'executer', 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')

        order = await dataset.order(
            status='processing',
            users=[user.user_id],
            store_id=user.store_id,
        )

        tap.eq(order.store_id, user.store_id, 'заказ на складе создан')
        tap.eq(order.status, 'processing', 'статус')

        t = await api(user=user)
        revision = order.revision

        user_id = uuid()
        await t.post_ok('api_tsd_order_executer',
                        json={
                            'order_id': order.order_id,
                            'link': [user_id]
                        })
        t.status_is(404, diag=True)
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.revision, revision, 'ордер не менялся')
        t.json_is('code', 'ER_UNKNOWN_USER')
        t.json_is('message', 'User(s) not found')
        t.json_is('details.users', [user_id], 'details')


async def test_wrong_order_type(tap, dataset, api):
    with tap.plan(11, 'Пользовательне может работать над заказом'):
        admin = await dataset.user(role='admin')
        user = await dataset.user(role='executer', store_id=admin.store_id)

        tap.eq(user.role, 'executer', 'пользователь создан')
        tap.eq(user.store_id, admin.store_id,'склад есть')

        order = await dataset.order(
            status='processing',
            type='inventory_check_more',
            store_id=user.store_id,
            users=[admin.user_id]
        )

        tap.eq(order.store_id, user.store_id, 'заказ на складе создан')
        tap.eq(order.status, 'processing', 'статус')

        t = await api(user=admin)
        revision = order.revision

        await t.post_ok('api_tsd_order_executer',
                        json={
                            'order_id': order.order_id,
                            'link': [user.user_id]
                        })
        t.status_is(404, diag=True)
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.revision, revision, 'ордер не менялся')
        t.json_is('code', 'ER_WRONG_USER_FOR_ORDER')
        t.json_is('message', 'User(s) cannot work with order')
        t.json_is('details.users', [user.user_id], 'details')
