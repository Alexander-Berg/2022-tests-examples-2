import pytest


async def test_mode(tap, dataset):
    with tap.plan(7, 'верификатор переключения в инвентаризацию'):
        store = await dataset.store()
        tap.eq((store.status, store.estatus),
               ('active', 'processing'),
               'склад создан')

        store.estatus = 'inventory_begin'
        tap.ok(await store.save(), 'склад сохранён')
        tap.ok(await store.inventory_check_change(), 'проверено')
        tap.eq(store.estatus, 'inventory', 'инвентаризация включилась')

        store.estatus = 'inventory_finish'
        tap.ok(await store.save(), 'склад сохранён')
        tap.ok(await store.inventory_check_change(), 'проверено')
        tap.eq(store.estatus, 'processing', 'инвентаризация выключилась')


@pytest.mark.parametrize('status',
                         ['reserving', 'approving', 'request', 'processing'])
async def test_error(tap, dataset, status):
    with tap.plan(9, 'возврат статуса назад если есть ордера'):
        store = await dataset.store()
        tap.eq((store.status, store.estatus),
               ('active', 'processing'),
               'склад создан')

        order = await dataset.order(store=store, type='order', status=status)
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        tap.eq(order.fstatus, (status, 'begin'), 'статус ордера')

        store.estatus = 'inventory_begin'
        tap.ok(await store.save(), 'склад сохранён')
        tap.ok(await store.inventory_check_change(), 'проверено')
        tap.eq(store.estatus, 'processing', 'инвентаризация не включилась')

        store.estatus = 'inventory_finish'
        tap.ok(await store.save(), 'склад сохранён')
        tap.ok(await store.inventory_check_change(), 'проверено')
        tap.eq(store.estatus, 'inventory', 'инвентаризация не выключилась')
