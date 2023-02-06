import pytest

@pytest.mark.parametrize('status', ['active', 'disabled'])
@pytest.mark.parametrize(
    'estatus',
    [
        {
            'from': 'processing',
            'to': 'inventory_begin',
            'mode': 'start',
            'ignore_mode': 'stop',
        },
        {
            'from': 'inventory',
            'to': 'inventory_finish',
            'mode': 'stop',
            'ignore_mode': 'start'
        },
    ]
)
async def test_mode_start(tap, api, dataset, estatus, status):
    with tap.plan(15, 'Переходы в инвентаризацию и из - без ошибок'):
        store = await dataset.store(status=status, estatus=estatus['from'])
        tap.eq(store.status, status, 'склад создан')
        tap.eq(store.estatus, estatus['from'], 'estatus')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)

        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['ignore_mode']},
                        desc='Запрос на уже сделанном')
        t.status_is(200, diag=True)
        tap.ok(await store.reload(), 'перегружен')
        tap.eq(store.estatus, estatus['from'], 'estatus не менялся')

        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['mode']})
        t.status_is(200, diag=True)

        tap.ok(await store.reload(), 'перегружен')
        tap.eq(store.estatus,
               estatus['to'],
               'режим перехода включён')

        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['mode']},
                        desc='Повторный запрос')
        t.status_is(200, diag=True)


        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['ignore_mode']},
                        desc='остановка при старте, старт при остановке')
        t.status_is(410, diag=True)

@pytest.mark.parametrize(
    'estatus',
    [
        {
            'from': 'processing',
            'to': 'inventory_begin',
            'mode': 'start',
            'ignore_mode': 'stop',
        },
        {
            'from': 'inventory',
            'to': 'inventory_finish',
            'mode': 'stop',
            'ignore_mode': 'start'
        },
    ]
)
async def test_mode_er_processing(tap, api, dataset, estatus):
    with tap.plan(12, 'Есть заказы в работе'):
        store = await dataset.store(status='active', estatus=estatus['from'])
        tap.eq(store.status, 'active', 'склад создан')
        tap.eq(store.estatus, estatus['from'], 'estatus')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)


        order = await dataset.order(status='processing', store=store)
        tap.eq(order.status, 'processing', 'заказ создан')
        tap.eq(order.store_id, store.store_id, 'склад')

        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['mode']},
                        desc='Повторный запрос')
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_HAS_PROCESSING')
        t.json_is('details.orders.0', order.order_id)
        t.json_hasnt('details.orders.1')


        tap.ok(await store.reload(), 'перегружен')
        tap.eq(store.estatus, estatus['from'], 'estatus не менялся')


@pytest.mark.parametrize('status', ['reserving', 'approving', 'request'])
@pytest.mark.parametrize(
    'estatus',
    [
        {
            'from': 'processing',
            'to': 'inventory_begin',
            'mode': 'start',
            'ignore_mode': 'stop',
        },
        {
            'from': 'inventory',
            'to': 'inventory_finish',
            'mode': 'stop',
            'ignore_mode': 'start'
        },
    ]
)
async def test_mode_er_orders(tap, api, dataset, estatus, status):
    with tap.plan(12, 'Есть заказы в работе'):
        store = await dataset.store(status='active', estatus=estatus['from'])
        tap.eq(store.status, 'active', 'склад создан')
        tap.eq(store.estatus, estatus['from'], 'estatus')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        t = await api(user=admin)


        order = await dataset.order(status=status, store=store)
        tap.eq(order.status, status, f'заказ {status} создан')
        tap.eq(order.store_id, store.store_id, 'склад')

        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['mode']},
                        desc='Повторный запрос')
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_HAS_ORDERS')
        t.json_is('details.orders.0', order.order_id)
        t.json_hasnt('details.orders.1')


        tap.ok(await store.reload(), 'перегружен')
        tap.eq(store.estatus, estatus['from'], 'estatus не менялся')

@pytest.mark.parametrize(
    'order_type',
    ['acceptance', 'refund', 'writeoff', 'visual_control',
     'writeoff_prepare_day', 'check_valid_short', 'check_valid_regular']
)
@pytest.mark.parametrize(
    'estatus',
    [
        {
            'from': 'processing',
            'to': 'inventory_begin',
            'to_final': 'inventory',
            'mode': 'start',
            'ignore_mode': 'stop',
        },
        {
            'from': 'inventory',
            'to': 'inventory_finish',
            'to_final': 'processing',
            'mode': 'stop',
            'ignore_mode': 'start'
        },
    ]
)
async def test_mode_ok_orders(tap, api, dataset, estatus, order_type):
    with tap.plan(12, 'Есть заказы в работе'):
        store = await dataset.store(status='active', estatus=estatus['from'])
        tap.eq(store.status, 'active', 'склад создан')
        tap.eq(store.estatus, estatus['from'], 'estatus')

        admin = await dataset.user(role='admin', store=store)
        tap.eq(admin.store_id, store.store_id, 'админ создан')

        order = await dataset.order(type=order_type, store=store)
        tap.eq(order.type, order_type, f'заказ {order_type} создан')
        tap.eq(order.store_id, store.store_id, 'склад')

        t = await api(user=admin)
        await t.post_ok('api_admin_stores_inventory_mode',
                        json={'mode': estatus['mode']},
                        desc='Повторный запрос')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.ok(await store.reload(), 'перегружен')
        tap.eq(store.estatus, estatus['to'], 'estatus изменился')

        tap.note('Переключим режим инвентаризации до конца')
        await store.inventory_check_change()
        tap.ok(await store.reload(), 'перегружен')
        tap.eq(store.estatus, estatus['to_final'], 'estatus изменился')
