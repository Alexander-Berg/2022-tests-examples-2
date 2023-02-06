import pytest

from . import utils


@utils.send_order_events_config()
async def test_top_level_categories_order_creation(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        mockserver,
        mock_processing,
        mock_eats_products_public_id,
):

    item_data = generate_order_item_data(
        category_id='low_level_id',
        category_name='low_level_category_name',
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    top_level_category_id = 'top_level_category_id'
    top_level_category_name = 'top_level_category_name'

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eats_picker_item_categories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == order_data['place_id']
        return mockserver.make_response(
            status=200,
            json={
                'items_categories': [
                    {
                        'item_id': item_data['id'],
                        'categories': [
                            {
                                'category_id': top_level_category_id,
                                'category_name': top_level_category_name,
                            },
                        ],
                    },
                ],
            },
        )

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200
    assert _mock_eats_picker_item_categories.times_called == 1

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.get('/api/v1/order?eats_id=12345')
    assert response.status_code == 200
    response_data = response.json()
    payload = response_data['payload']
    categories = payload['categories']
    assert len(categories) == 1
    category = categories[0]
    assert category['name'] == top_level_category_name
    assert category['id'] == top_level_category_id
    picker_items = payload['picker_items']
    assert len(picker_items) == 1
    assert picker_items[0]['category_id'] == top_level_category_id


@utils.send_order_events_config()
async def test_top_level_categories_with_priority(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        mockserver,
        mock_processing,
        mock_eats_products_public_id,
):

    item_data = generate_order_item_data(
        category_id='low_level_id',
        category_name='low_level_category_name',
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    top_level_category_id1 = 'top_level_category_id_1'
    top_level_category_id2 = 'top_level_category_id_2'
    top_level_category_name1 = 'top_level_category_name_1'
    top_level_category_name2 = 'top_level_category_name_2'
    priority1 = 1.1
    priority2 = 1.5

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eatspickeritemcategories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == order_data['place_id']
        return mockserver.make_response(
            status=200,
            json={
                'items_categories': [
                    {
                        'item_id': item_data['id'],
                        'categories': [
                            {
                                'category_id': top_level_category_id1,
                                'category_name': top_level_category_name1,
                                'category_priority': priority1,
                            },
                            {
                                'category_id': top_level_category_id2,
                                'category_name': top_level_category_name2,
                                'category_priority': priority2,
                            },
                        ],
                    },
                ],
            },
        )

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200
    assert _mock_eatspickeritemcategories.times_called == 1

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.get('/api/v1/order?eats_id=12345')
    assert response.status_code == 200
    response_data = response.json()
    payload = response_data['payload']
    categories = payload['categories']
    assert len(categories) == 1
    category = categories[0]
    assert category['name'] == top_level_category_name1
    assert category['id'] == top_level_category_id1
    picker_items = payload['picker_items']
    assert len(picker_items) == 1
    assert picker_items[0]['category_id'] == top_level_category_id1
    assert abs(picker_items[0]['category_priority'] - priority1) < 0.0001
    second_category = picker_items[0]['second_category']
    assert second_category
    assert second_category['name'] == top_level_category_name2
    assert second_category['id'] == top_level_category_id2
    assert abs(second_category['priority'] - priority2) < 0.0001


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
@utils.send_order_events_config()
async def test_top_level_categories_for_added_item(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_integration_item_data,
        create_order,
        create_order_item,
        mockserver,
        handle,
        mock_processing,
        mock_eats_products_public_id,
):
    eats_id = '111'
    place_id = 5
    picker_id = '222'
    order_id = create_order(
        eats_id=eats_id, place_id=place_id, picker_id=picker_id,
    )

    eats_item_id1 = 'item1'
    category_id1 = 'low_level_category_id_1'
    category_name1 = 'low_level_category_name_1'

    create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        category_id=category_id1,
        category_name=category_name1,
    )

    eats_item_id2 = 'item2'
    category_id2 = 'low_level_category_id_2'
    category_name2 = 'low_level_category_name_2'

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=eats_item_id2,
                    is_catch_weight=False,
                    barcodes=[eats_item_id2],
                    vendor_code=eats_item_id2,
                    category_id=category_id2,
                    category_name=category_name2,
                    price=250,
                    measure_quantum=1,
                ),
                'barcode': eats_item_id2,
                'sku': eats_item_id2,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    payment_limit = 1000000

    @mockserver.json_handler('/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            return mockserver.make_response(
                json={'amount': payment_limit}, status=200,
            )

        assert request.json['order_id'] == eats_id
        assert request.json['amount'] == 1000000
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    top_level_category_id1 = 'top_level_category_id_1'
    top_level_category_id2 = 'top_level_category_id_2'
    top_level_category_name1 = 'top_level_category_name_1'
    top_level_category_name2 = 'top_level_category_name_2'

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eatspickeritemcategories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == place_id
        return mockserver.make_response(
            status=200,
            json={
                'items_categories': [
                    {
                        'item_id': eats_item_id1,
                        'categories': [
                            {
                                'category_id': top_level_category_id1,
                                'category_name': top_level_category_name1,
                            },
                        ],
                    },
                    {
                        'item_id': eats_item_id2,
                        'categories': [
                            {
                                'category_id': top_level_category_id2,
                                'category_name': top_level_category_name2,
                            },
                        ],
                    },
                ],
            },
        )

    mock_eats_products_public_id()

    request_body = {
        'items': [
            {
                'eats_item_id': eats_item_id2,
                'vendor_code': '7777',
                'quantity': 2,
            },
        ],
    }

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    headers = utils.da_headers(picker_id)
    response = await taxi_eats_picker_orders.post(
        handle, headers=headers, params=params, json=request_body,
    )

    assert response.status_code == 200

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    categories = payload['categories']
    assert len(categories) == 2
    category1 = categories[0]
    category2 = categories[1]

    assert top_level_category_id2 in (category1['id'], category2['id'])

    picker_items = payload['picker_items']
    assert len(picker_items) == 2
    picker_item1 = picker_items[0]
    picker_item2 = picker_items[1]
    assert top_level_category_id2 in (
        picker_item1['category_id'],
        picker_item2['category_id'],
    )


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_top_level_categories_for_replacements(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_integration_item_data,
        create_order,
        create_order_item,
        mockserver,
        handle,
        mock_processing,
        mock_eats_products_public_id,
):
    eats_id = '111'
    place_id = 5
    picker_id = '222'
    order_id = create_order(
        eats_id=eats_id, place_id=place_id, picker_id=picker_id,
    )

    eats_item_id1 = 'item1'
    category_id1 = 'low_level_category_id_1'
    category_name1 = 'low_level_category_name_1'

    create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        category_id=category_id1,
        category_name=category_name1,
    )

    eats_item_id2 = 'item2'
    category_id2 = 'low_level_category_id_2'
    category_name2 = 'low_level_category_name_2'

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=eats_item_id2,
                    is_catch_weight=False,
                    barcodes=[eats_item_id2],
                    vendor_code=eats_item_id2,
                    category_id=category_id2,
                    category_name=category_name2,
                    measure_quantum=0.75,
                ),
                'barcode': eats_item_id2,
                'sku': eats_item_id2,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    payment_limit = 1000000

    @mockserver.json_handler('/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            return mockserver.make_response(
                json={'amount': payment_limit}, status=200,
            )

        assert request.json['order_id'] == eats_id
        assert request.json['amount'] == 1000000
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    top_level_category_id1 = 'top_level_category_id_1'
    top_level_category_id2 = 'top_level_category_id_2'
    top_level_category_name1 = 'top_level_category_name_1'
    top_level_category_name2 = 'top_level_category_name_2'

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eatspickeritemcategories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == place_id
        return mockserver.make_response(
            status=200,
            json={
                'items_categories': [
                    {
                        'item_id': eats_item_id1,
                        'categories': [
                            {
                                'category_id': top_level_category_id1,
                                'category_name': top_level_category_name1,
                            },
                        ],
                    },
                    {
                        'item_id': eats_item_id2,
                        'categories': [
                            {
                                'category_id': top_level_category_id2,
                                'category_name': top_level_category_name2,
                            },
                        ],
                    },
                ],
            },
        )

    mock_eats_products_public_id()

    request_body = {
        'items': [
            {
                'old_item_id': eats_item_id1,
                'eats_item_id': eats_item_id2,
                'quantity': 5.5,
                'barcode': '12345',
            },
        ],
    }

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    headers = utils.da_headers(picker_id)
    response = await taxi_eats_picker_orders.put(
        handle, headers=headers, params=params, json=request_body,
    )

    assert response.status_code == 200

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    categories = payload['categories']
    assert len(categories) == 1
    category = categories[0]

    assert category['id'] == top_level_category_id2

    picker_items = payload['picker_items']
    assert len(picker_items) == 1
    assert picker_items[0]['category_id'] == top_level_category_id2
