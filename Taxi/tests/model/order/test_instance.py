from stall.model.order import Order


def test_instance(tap, uuid):
    with tap.plan(1):
        order = Order({
            'company_id': uuid(),
            'store_id': uuid(),
            'status': 'request',
            'courier_id': uuid(),
        })
        tap.ok(order, 'Инстанцирован')


def test_dispatch_type(tap, uuid):
    with tap.plan(3, 'дефолтные значения флага диспатчинга'):
        with Order({
                'company_id': uuid(),
                'store_id': uuid(),
                'courier_id': uuid(),
                'status': 'request',
                'type': 'order',
        }) as order:
            tap.eq(order.dispatch_type, 'external', 'external для заказов')

        with Order({
                'company_id': uuid(),
                'store_id': uuid(),
                'courier_id': uuid(),
                'status': 'request',
                'type': 'acceptance',
        }) as order:
            tap.eq(order.dispatch_type, None, 'None для остальных ордеров')

        with Order({
                'company_id': uuid(),
                'store_id': uuid(),
                'courier_id': uuid(),
                'status': 'request',
                'type': 'order',
                'dispatch_type': 'grocery',
        }) as order:
            tap.eq(order.dispatch_type, 'grocery', 'Настраивается')
