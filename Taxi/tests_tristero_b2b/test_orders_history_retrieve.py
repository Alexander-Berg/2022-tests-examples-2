from testsuite.utils import ordered_object

ORDER_IDS = [
    '123e4567-e89b-12d3-a456-426614174000',
    '123e4567-e89b-12d3-a456-426614174001',
]
ORDER_DEPOT_IDS = {
    '123e4567-e89b-12d3-a456-426614174000': '0123456789abcdef000000000000001',
    '123e4567-e89b-12d3-a456-426614174001': '0123456789abcdef000000000000002',
}
ORDERS_HISTORY = {
    '123e4567-e89b-12d3-a456-426614174000': [
        'created',
        'reserved',
        'expecting_delivery',
        'received_partialy',
        'received',
        'delivered_partially',
        'delivered',
        'cancelled',
    ],
    '123e4567-e89b-12d3-a456-426614174001': ['created', 'cancelled'],
}
ORDER_ITEMS = {
    '123e4567-e89b-12d3-a456-426614174000': [
        '98765432-e89b-12d3-a456-426614174000',
        '98765432-e89b-12d3-a456-426614174001',
    ],
    '123e4567-e89b-12d3-a456-426614174001': [],
}
ITEMS_BARCODES = {
    '98765432-e89b-12d3-a456-426614174000': '123456789',
    '98765432-e89b-12d3-a456-426614174001': '0987654321',
}
ITEMS_HISTORY = {
    '98765432-e89b-12d3-a456-426614174000': [
        'reserved',
        'created',
        'in_depot',
        'ordered',
        'order_cancelled',
        'ready_for_delivery',
        'courier_assigned',
        'delivering',
        'delivered',
        'returned_to_vendor',
        'auto_ordered',
    ],
    '98765432-e89b-12d3-a456-426614174001': ['reserved'],
}
TIMESTAMP = '2020-10-09T12:00:00+00:00'


async def test_orders_history_retrieve(taxi_tristero_b2b, mockserver):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/orders/history',
    )
    def _mock_parcels(request):
        response = {'orders': []}
        for order_id in request.json['order_ids']:
            order = {'events': [], 'items': []}
            order['order_id'] = order_id
            order['depot_id'] = ORDER_DEPOT_IDS[order_id]
            for order_history in ORDERS_HISTORY[order_id]:
                order['events'].append(
                    {'state': order_history, 'timestamp': TIMESTAMP},
                )
            for item_id in ORDER_ITEMS[order_id]:
                item = {'events': []}
                item['item_id'] = item_id
                item['barcode'] = ITEMS_BARCODES[item_id]
                for item_history in ITEMS_HISTORY[item_id]:
                    item['events'].append(
                        {
                            'state': item_history,
                            'timestamp': TIMESTAMP,
                            'state_meta': {},
                        },
                    )
                order['items'].append(item)
            response['orders'].append(order)
        return response

    request = {'order_ids': ORDER_IDS}
    response = await taxi_tristero_b2b.post(
        '/tristero/v1/orders/history/retrieve', json=request,
    )
    assert response.status_code == 200
    assert _mock_parcels.times_called == 1
    orders_history = response.json()['orders']
    assert len(orders_history) == len(ORDERS_HISTORY)
    for order in orders_history:
        order_id = order['order_id']
        assert order_id in ORDER_IDS
        assert order['depot_id'] == ORDER_DEPOT_IDS[order_id]
        order_states = list(ORDERS_HISTORY[order_id])
        # created is internal state and should not be in response
        order_states.remove('created')
        assert len(order['events']) == len(order_states)
        ordered_object.assert_eq(
            [event['state'] for event in order['events']], order_states, [''],
        )
        assert len(order['items']) == len(ORDER_ITEMS[order_id])
        for item in order['items']:
            assert 'barcode' in item
            for item_id in ORDER_ITEMS[order_id]:
                if item['barcode'] == ITEMS_BARCODES[item_id]:
                    assert len(item['events']) == len(ITEMS_HISTORY[item_id])
                    ordered_object.assert_eq(
                        [event['state'] for event in item['events']],
                        ITEMS_HISTORY[item_id],
                        [''],
                    )
