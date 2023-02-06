from datetime import timedelta
from pytz import all_timezones as all_tzs

import pytest


@pytest.mark.parametrize('role, expected_code', [
    ('admin', 200),
    ('executer', 200),
    ('barcode_executer', 403),
])
async def test_roles(tap, api, dataset, role, expected_code, cfg):
    cfg.set('business.order.acceptance.time_doc_availability', 24)
    with tap.plan(5, 'проверка order на доступ по сроку давности'):
        user = await dataset.user(role=role)
        tap.ok(user, 'юзер создан')
        order_child = await dataset.order(
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='stowage',
        )
        tap.ok(order_child, 'дочерний заказ создан')
        order_main = await dataset.order(
            store_id=user.store_id,
            required=[],
            vars={'stowage_id': [order_child.order_id]},
            status='complete',
            estatus='done',
            type='acceptance',
        )
        tap.ok(order_main, 'основной заказ создан')
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': order_main.order_id}
        )
        t.status_is(expected_code, diag=True)


@pytest.mark.parametrize('main_time, ans', [(0, 200), (48, 403)])
async def test_load_data_time(tap, api, dataset, cfg, main_time, now, ans):
    cfg.set('business.order.acceptance.time_doc_availability', 24)
    with tap.plan(5, 'проверка order на доступ по сроку давности'):
        time = timedelta(hours=main_time)
        user = await dataset.user(role='admin')
        tap.ok(user, 'юзер создан')
        order_child = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='stowage',
        )
        tap.ok(order_child, 'дочерний заказ создан')
        order_main = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            updated=now() - time,
            vars={'stowage_id': [order_child.order_id]},
            status='complete',
            estatus='done',
            type='acceptance',
        )
        tap.ok(order_main, 'основной заказ создан')
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': order_main.order_id}
        )
        t.status_is(ans, diag=True)


@pytest.mark.parametrize(
    'order_type, ans',
    [('acceptance', 200), ('stowage', 403)]
)
async def test_load_data_acceptance(tap, api, dataset, cfg, order_type, ans):
    cfg.set('business.order.acceptance.time_doc_availability', 48)
    with tap.plan(8,
                  'проверка order на доступ по тип order'
                  ' - acceptance + дочерние stowage'):
        user = await dataset.user(role='admin')
        tap.ok(user, 'юзер создан')
        list_child_ord = []
        for i in [['complete', 'done'], ['processing', 'waiting'],
                  ['complete', 'done']]:
            order_child = await dataset.order(
                users=[user.user_id],
                store_id=user.store_id,
                required=[],
                status=i[0],
                estatus=i[1],
                type='stowage',
            )
            list_child_ord.append(order_child)
        tap.ok(list_child_ord, 'дочерний заказ 1, 2, 3 создан')
        list_main_ord = []
        for stowage_id in [[list_child_ord[0].order_id],
                           [list_child_ord[1].order_id,
                            list_child_ord[2].order_id]]:
            order_main = await dataset.order(
                users=[user.user_id],
                store_id=user.store_id,
                required=[],
                vars={'stowage_id': stowage_id},
                type=order_type,
                status='complete',
                estatus='done'
            )
            list_main_ord.append(order_main)

        tap.ok(list_main_ord[0], 'родительский 1 заказ создан '
                                 'с 1 дочерним заказом')
        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': list_main_ord[0].order_id}
        )
        t.status_is(ans, diag=True)

        tap.ok(list_main_ord[1], 'родительский 2 заказ создан с'
                                 ' 2 и 3 дочерним заказом')
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': list_main_ord[1].order_id}
        )
        t.status_is(403, diag=True)


async def test_acceptance_stowage_failed(tap, api, dataset, cfg):
    cfg.set('business.order.acceptance.time_doc_availability', 48)
    with tap.plan(5,
                  'проверка приемки со всеми размещениями '
                  'в статусе failed/canceled'):
        user = await dataset.user(role='admin')
        tap.ok(user, 'юзер создан')
        order_main = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='acceptance',
        )
        tap.ok(order_main, 'приемка создана')

        list_child_ord = []
        for i in ['failed', 'failed', 'canceled']:
            order_child = await dataset.order(
                users=[user.user_id],
                store_id=user.store_id,
                required=[],
                parent=[order_main.order_id],
                status=i,
                estatus='done',
                type='sale_stowage',
            )
            list_child_ord.append(order_child)
        tap.ok(list_child_ord, 'дочерний заказ 1, 2, 3 создан')

        order_main.vars['stowage_id'] = [o.order_id for o in list_child_ord]
        await order_main.save()

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': order_main.order_id}
        )
        t.status_is(200, diag=True)


async def test_load_data_no_stowage(tap, api, dataset, cfg):
    cfg.set('business.order.acceptance.time_doc_availability', 48)
    with tap.plan(3, 'заказ без дочерних stowage'):
        user = await dataset.user(role='admin')
        parent_order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            vars={},
            type='acceptance',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': parent_order.order_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нету stowage')


async def test_load_data_diff_times(tap, api, dataset, cfg, now, tzone):
    cfg.set('business.order.acceptance.time_doc_availability', 48)
    # антифлап
    str_tz = next(i for i in all_tzs if now(tz=tzone(i)).hour not in [23, 0])
    tz = tzone(str_tz)


    before_now = now(tz=tz) - timedelta(minutes=2)
    after_now = now(tz=tz) + timedelta(minutes=2)
    before_now = f'{before_now.hour}:{before_now.minute}'
    after_now = f'{after_now.hour}:{after_now.minute}'
    cfg.set('business.order.acceptance.last_stowage_time_limit', before_now)
    with tap.plan(6, 'заказ с разными time_limit'):
        user = await dataset.user(role='admin', tz=str_tz)

        child_order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='stowage',
            updated=str(now(tz) - timedelta(days=1)),
        )

        parent_order = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            vars={'stowage_id': [child_order.order_id]},
            type='acceptance',
            status='complete',
            estatus='done'
        )

        t = await api(user=user)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': parent_order.order_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'stowage протух')

        cfg.set('business.order.acceptance.last_stowage_time_limit', after_now)
        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': parent_order.order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'stowage свежий')


async def test_stowage_without_parent(tap, api, dataset, cfg):
    cfg.set('business.order.sale_stowage.time_doc_availability', 48)
    with tap.plan(5, 'проверка sale_stowage без родителя'):
        user = await dataset.user(role='admin')
        tap.ok(user, 'юзер создан')
        order_child = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='sale_stowage',
        )
        tap.ok(order_child, 'размещение создано')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': order_child.order_id}
        )
        t.status_is(403, diag=True)
        t.json_is('message', 'Stowage has not parent')


async def test_not_done_relatives_ss(tap, api, dataset, cfg):
    cfg.set('business.order.sale_stowage.time_doc_availability', 48)
    with tap.plan(6, 'проверка sale_stowage с незакрытой раскладкой'
                     ' у родительской приемки'):
        user = await dataset.user(role='admin')
        tap.ok(user, 'юзер создан')
        order_main = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='acceptance',
        )
        tap.ok(order_main, 'приемка создана')
        list_child_ord = []
        for i in [['complete', 'done'], ['request', 'begin']]:
            order_child = await dataset.order(
                users=[user.user_id],
                store_id=user.store_id,
                parent=[order_main.order_id],
                required=[],
                status=i[0],
                estatus=i[1],
                type='sale_stowage',
            )
            list_child_ord.append(order_child)
        tap.ok(list_child_ord, 'дочерний заказ 1, 2 создан')

        order_main.vars['stowage_id'] = [o.order_id for o in list_child_ord]
        await order_main.save()

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': list_child_ord[0].order_id}
        )
        t.status_is(403, diag=True)
        t.json_is('message', 'Stowage is not complete')


async def test_sale_stowage_ok(tap, api, dataset, cfg, uuid):
    cfg.set('business.order.sale_stowage.time_doc_availability', 48)
    with tap.plan(13, 'проверка раскладки со всеми'
                      ' закрытыми братскими размещениями'):
        user = await dataset.user(role='admin')
        tap.ok(user, 'юзер создан')

        order_main = await dataset.order(
            users=[user.user_id],
            store_id=user.store_id,
            required=[],
            status='complete',
            estatus='done',
            type='acceptance',
        )
        tap.ok(order_main, 'приемка создана')

        list_child_ord = []
        for i in ['complete', 'complete', 'canceled']:
            order_child = await dataset.order(
                users=[user.user_id],
                store_id=user.store_id,
                parent=[order_main.order_id],
                required=[{'product_id': uuid(), 'count': 0}],
                status=i,
                estatus='done',
                type='sale_stowage',
            )
            list_child_ord.append(order_child)
        tap.ok(list_child_ord, 'дочерний заказ 1, 2, 3 создан')

        order_main.vars['stowage_id'] = [o.order_id for o in list_child_ord]
        await order_main.save()

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': list_child_ord[0].order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('order.type', 'sale_stowage')
        t.json_is('order.required.0.count', 0)

        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': list_child_ord[1].order_id}
        )
        t.status_is(200, diag=True)
        t.json_is('order.type', 'sale_stowage')
        t.json_is('order.required.0.count', 0)

        await t.post_ok(
            'api_tsd_order_load_data',
            json={'order_id': list_child_ord[2].order_id}
        )
        t.status_is(403, diag=True)
