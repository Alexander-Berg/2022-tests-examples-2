import pytest


async def test_change_flow_type_success(
        taxi_eats_picker_orders, create_order, get_order,
):
    order_id = create_order(eats_id='42', last_version=1, state='new')

    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-only?eats_id=42',
    )

    assert response.status == 202
    assert get_order(order_id)['flow_type'] == 'picking_only'

    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-packing?eats_id=42',
    )

    assert response.status == 200
    assert get_order(order_id)['flow_type'] == 'picking_packing'

    courier_id = '123-picker'
    courier_name = 'Best Picker'
    courier_phone_id = 'phone_1'
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=42',
        json={
            'id': courier_id,
            'name': courier_name,
            'phone_id': courier_phone_id,
        },
    )

    assert response.status == 200
    order = get_order(order_id)
    assert order['flow_type'] == 'picking_handing'
    assert order['courier_id'] == courier_id
    assert order['courier_name'] == courier_name
    assert order['courier_phone_id'] == courier_phone_id
    assert order['courier_phone'] is None

    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-only?eats_id=42',
    )

    assert response.status == 200
    assert get_order(order_id)['flow_type'] == 'picking_only'


@pytest.mark.parametrize(
    'state', ['complete', 'cancelled', 'packing', 'handing'],
)
@pytest.mark.parametrize(
    'flow_type', ['picking-only', 'picking-packing', 'picking-handing'],
)
async def test_flow_type_change_forbidden(
        taxi_eats_picker_orders, create_order, get_order, state, flow_type,
):
    order_id = create_order(eats_id='42', last_version=1, state=state)

    initial_flow = get_order(order_id)['flow_type']
    json = None
    if flow_type == 'picking-handing':
        json = {
            'id': 'courier_id',
            'name': 'courier_name',
            'phone_id': 'courier_phone',
        }
    response = await taxi_eats_picker_orders.put(
        f'/api/v1/order/flow-type/{flow_type}?eats_id=42', json=json,
    )
    assert response.status == 409
    assert get_order(order_id)['flow_type'] == initial_flow


async def test_flow_type_change_courier_cannot_be_picker(
        taxi_eats_picker_orders, create_order, get_order,
):
    picker_id = '1'
    order_id = create_order(eats_id='42', picker_id=picker_id, last_version=1)

    initial_flow = get_order(order_id)['flow_type']
    flow_type = 'picking-handing'
    response = await taxi_eats_picker_orders.put(
        f'/api/v1/order/flow-type/{flow_type}?eats_id=42',
        json={
            'id': picker_id,
            'name': 'courier_name',
            'phone_id': 'courier_phone',
        },
    )
    assert response.status == 409
    assert get_order(order_id)['flow_type'] == initial_flow


async def test_change_handing_courier(taxi_eats_picker_orders, create_order):
    create_order(eats_id='42', flow_type='picking_only', picker_id='1')
    json = {'id': '2', 'name': 'Courier Courierovich', 'phone_id': '57'}
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=42', json=json,
    )
    assert response.status == 200

    # The same courier for the second time
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=42', json=json,
    )
    assert response.status == 202

    # Change courier
    json = {'id': '3', 'name': 'Courier Courierovich Sr.', 'phone_id': '24'}
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=42', json=json,
    )
    assert response.status == 200


async def test_picking_handing_forwarded_phone_number(
        taxi_eats_picker_orders, create_order, mockserver,
):
    create_order(eats_id='42', last_version=1, state='new')
    courier_id = '123-picker'
    courier_name = 'Best Picker'
    courier_phone_id = 'phone_1'
    forwarded_courier_phone = '+7-123-456-78-90'

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _forwardings_handler(request):
        return

    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=42',
        json={
            'id': courier_id,
            'name': courier_name,
            'phone_id': courier_phone_id,
            'forwarded_phone_number': forwarded_courier_phone,
        },
    )
    assert response.status == 200

    response = await taxi_eats_picker_orders.get(f'/api/v1/order?eats_id=42')
    assert response.status == 200
    assert _forwardings_handler.times_called == 0

    order = response.json()['payload']
    assert order['flow_type'] == 'picking_handing'
    assert order['courier_id'] == courier_id
    assert order['courier_name'] == courier_name
    assert order['courier_phone_id'] == courier_phone_id
    assert order['forwarded_courier_phone'] == forwarded_courier_phone


@pytest.mark.parametrize('flow_type', ['picking_packing', 'picking_handing'])
async def test_picking_hanging_phone_id(
        taxi_eats_picker_orders, create_order, get_order, flow_type,
):
    json = {'id': 'courier1', 'name': 'co-co-courier'}
    courier_phone_id = '228'
    json_with_phone_id = {
        'id': 'courier2',
        'name': 'fluffy-courier',
        'phone_id': courier_phone_id,
    }

    order_id = create_order(
        eats_id='210413-000001',
        flow_type=flow_type,
        courier_phone_id=courier_phone_id,
    )
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=210413-000001',
        json=json,
    )
    assert response.status == 200
    assert get_order(order_id)['flow_type'] == 'picking_handing'
    assert get_order(order_id)['courier_phone_id'] is None

    order_id = create_order(eats_id='210413-000002', flow_type=flow_type)
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order/flow-type/picking-handing?eats_id=210413-000002',
        json=json_with_phone_id,
    )
    assert response.status == 200
    assert get_order(order_id)['flow_type'] == 'picking_handing'
    assert get_order(order_id)['courier_phone_id'] == courier_phone_id
