from tests import dataset as dt

async def test_create_log(tap, dataset: dt):
    courier = await dataset.courier()
    courier_shift = await dataset.courier_shift(courier_id=courier.courier_id)
    order = await dataset.order(
        courier_id=courier.courier_id,
        courier_shift_id=courier_shift.courier_shift_id,
    )

    await dataset.order_log(
        order_id=order.order_id,
        source='set_courier',
        vars={
            'action': 'assign',
            'courier_id': order.courier_id,
            'courier_shift_id': order.courier_shift_id,
            'request': {}
        }
    )

    cursor = await dataset.OrderLog.list(
        by='full',
        conditions=(
            ('source', 'set_courier'),
            ('order_id', order.order_id),
        )
    )
    tap.ok(len(cursor.list), 'Лог set_courier загружен')
    with cursor.list[0] as order_log:
        tap.eq_ok(order_log.order_id, order.order_id, 'order_id')
        tap.eq_ok(order_log.source, 'set_courier', 'source')
        tap.eq_ok(order_log.vars.get('action'), 'assign', 'action')
        tap.eq_ok(order_log.vars.get('courier_id'), order.courier_id,
                  'courier_id')
        tap.eq_ok(order_log.vars.get('courier_shift_id'),
                  order.courier_shift_id, 'courier_shift_id')
