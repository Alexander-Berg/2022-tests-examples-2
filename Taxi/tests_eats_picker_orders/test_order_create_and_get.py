import pytest

from . import utils


@pytest.mark.parametrize('show_vendor_code', [None, True, False])
@utils.send_order_events_config()
@utils.marking_types_config()
async def test_create_orders_and_get_them(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        show_vendor_code,
        mockserver,
        mock_processing,
        mock_eats_products_public_id,
        mock_nmn_products_info,
        generate_product_info,
):
    item_data = generate_order_item_data(
        show_vendor_code=show_vendor_code,
        measure_v1=False,
        measure_quantum=0.8,
    )
    order_data = generate_order_data(items=[item_data])
    estimated_delivery_duration = 1800
    order_data['estimated_delivery_duration'] = estimated_delivery_duration

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eats_picker_item_categories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == order_data['place_id']
        return mockserver.make_response(
            status=200, json={'items_categories': []},
        )

    public_id = '54321'
    mock_eats_products_public_id(
        [{'origin_id': '12345', 'public_id': public_id}],
    )
    mock_nmn_products_info(
        [generate_product_info(public_id, 'product_name', [], 'marked_milk')],
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200
    assert _mock_eats_picker_item_categories.times_called == 1
    response = await taxi_eats_picker_orders.get('/api/v1/order?eats_id=12345')
    response_data = response.json()
    expected_order = load_json('expected_order.json')
    expected_order['payload']['status_updated_at'] = response_data['payload'][
        'status_updated_at'
    ]

    assert mock_processing.times_called == 1

    if show_vendor_code is not None:
        expected_order['payload']['picker_items'][0][
            'show_vendor_code'
        ] = show_vendor_code
    else:
        expected_order['payload']['picker_items'][0][
            'show_vendor_code'
        ] = expected_order['payload']['picker_items'][0]['is_catch_weight']

    assert (
        response_data['payload']['estimated_delivery_duration']
        == estimated_delivery_duration
    )
    del response_data['payload']['estimated_delivery_duration']
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['payment_limit']
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']

    expected_picked_item = expected_order['payload']['picker_items'][0]

    for measure in ['measure', 'measure_v2']:
        expected_picked_item[measure]['relative_quantum'] = pytest.approx(
            expected_picked_item[measure]['relative_quantum'],
        )

    assert expected_order == response_data
