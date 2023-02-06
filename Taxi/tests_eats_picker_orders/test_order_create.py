# pylint: disable=too-many-lines
import pytest

from . import utils


async def test_order_create_wrong_input_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json={'foo': 'bar'},
    )
    assert response.status == 400


async def test_create_order_with_invalid_currency_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        mock_eatspickeritemcategories,
):
    item_data = generate_order_item_data(measure_v1=False)
    order_data = generate_order_data(
        items=[item_data],
        payment_currency_code='FOO',
        payment_currency_sign='BAR',
    )

    mock_eatspickeritemcategories(order_data['place_id'])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400

    payload = response.json()
    assert payload['errors'][0]['code'] == 400
    assert payload['errors'][0]['description'] == 'Incorrect currency code'


async def test_create_order_without_items_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
):
    order_data = generate_order_data()
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


async def test_create_order_with_existing_eats_id_202(
        create_order,
        taxi_eats_picker_orders,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
):
    eats_id = '123'
    create_order(eats_id=eats_id)
    order_data = generate_order_data(
        eats_id=eats_id, items=[generate_order_item_data(measure_v1=False)],
    )
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    assert response.status == 202
    assert response.json()['result'] == 'OK'
    assert response.json()['order_id'] == str(order['id'])


@pytest.mark.parametrize(
    'barcode_weight_encoding', [None, 'ean13-tail-gram-4', 'manual'],
)
@pytest.mark.parametrize('show_vendor_code', [None, True, False])
@utils.send_order_events_config()
async def test_create_order_with_weight_item_200(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        get_last_order_status,
        get_order_items,
        barcode_weight_encoding,
        show_vendor_code,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True,
        images=images,
        barcode_weight_encoding=barcode_weight_encoding,
        show_vendor_code=show_vendor_code,
        measure_quantum=0.8,
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])

    payload = response.json()
    assert payload['result'] == 'OK'
    assert payload['order_id'] == str(order['id'])
    assert order['require_approval'] == order_data['require_approval']

    expected_order = load_json('expected_order.json')
    utils.compare_db_with_expected_data(order, expected_order)

    status = get_last_order_status(order_id=order['id'])
    expected_order_status = load_json('expected_order_status.json')
    utils.compare_db_with_expected_data(status, expected_order_status)

    order_items = get_order_items(order_id=order['id'])
    assert len(order_items) == 1

    expected_order_item = load_json('expected_order_item_measure_v2.json')
    if show_vendor_code is not None:
        expected_order_item['show_vendor_code'] = show_vendor_code
    else:
        expected_order_item['show_vendor_code'] = expected_order_item[
            'sold_by_weight'
        ]

    expected_order_item['barcode_weight_algorithm'] = barcode_weight_encoding
    utils.compare_db_with_expected_data(order_items[0], expected_order_item)


@pytest.mark.parametrize(
    'is_catch_weight, quantity', [[True, 0], [False, 0], [False, 0.9]],
)
async def test_create_order_wrong_item_quantity_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        is_catch_weight,
        quantity,
        mock_eatspickeritemcategories,
):
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight, quantity=quantity,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@utils.send_order_events_config()
async def test_create_order_with_not_weight_item_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        get_last_order_status,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        barcode_weight_encoding=None,
        measure_max_overweight=None,
        is_catch_weight=False,
        images=images,
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])

    last_order_status = get_last_order_status(order['id'])
    assert last_order_status['state'] == 'new'
    assert last_order_status['author_id'] is None

    payload = response.json()
    assert payload['result'] == 'OK'
    assert payload['order_id'] == str(order['id'])


@utils.send_order_events_config()
async def test_create_order_with_flow_type_200(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True, images=images, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['flow_type'] = 'picking_handing'
    order_data['finish_picking_at'] = '1976-01-19T15:00:27.01+03:00'
    order_data['brand_id'] = 'Stop and shop'

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    expected_order['brand_id'] = 'Stop and shop'
    order['finish_picking_at'] = str(order['finish_picking_at'])
    expected_order['finish_picking_at'] = '1976-01-19 15:00:27.010000+03:00'
    expected_order['flow_type'] = 'picking_handing'
    utils.compare_db_with_expected_data(order, expected_order)


@utils.send_order_events_config()
async def test_create_order_with_eta(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    eta = 1000
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True, images=images, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['estimated_picking_time'] = eta

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    expected_order['estimated_picking_time'] = eta
    utils.compare_db_with_expected_data(order, expected_order)


@pytest.mark.parametrize(
    ['field_name'],
    [['id_'], ['vendor_code'], ['name'], ['category_id'], ['category_name']],
)
async def test_order_create_with_empty_required_fields(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        field_name,
):
    item_data = generate_order_item_data(
        is_catch_weight=False, **{field_name: ''},
    )
    order_data = generate_order_data(items=[item_data])
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@utils.send_order_events_config()
async def test_create_order_with_customer_phone_id(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    customer_phone_id = '123'
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True, images=images, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['customer_phone_id'] = customer_phone_id

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    expected_order['customer_phone_id'] = customer_phone_id
    utils.compare_db_with_expected_data(order, expected_order)


@pytest.mark.parametrize('is_catch_weight', [False, True])
@pytest.mark.parametrize(
    'barcode_weight_encoding', [None, 'ean13-tail-gram-4', 'manual'],
)
@pytest.mark.parametrize('show_vendor_code', [None, True, False])
@utils.send_order_events_config()
async def test_create_order_measure_v2_200(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        get_last_order_status,
        get_order_items,
        is_catch_weight,
        barcode_weight_encoding,
        show_vendor_code,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    measure_value = 500
    quantum = 0.8
    quantum_price = 20
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight,
        images=images,
        barcode_weight_encoding=barcode_weight_encoding,
        show_vendor_code=show_vendor_code,
        measure_value=measure_value,
        measure_quantum=quantum,
        quantum_price=quantum_price,
        price=None,
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])

    payload = response.json()
    assert payload['result'] == 'OK'
    assert payload['order_id'] == str(order['id'])
    assert order['require_approval'] == order_data['require_approval']

    expected_order = load_json('expected_order.json')
    utils.compare_db_with_expected_data(order, expected_order)

    status = get_last_order_status(order_id=order['id'])
    expected_order_status = load_json('expected_order_status.json')
    utils.compare_db_with_expected_data(status, expected_order_status)

    order_items = get_order_items(order_id=order['id'])
    assert len(order_items) == 1

    expected_order_item = load_json('expected_order_item_measure_v2.json')
    expected_order_item['sold_by_weight'] = is_catch_weight
    if show_vendor_code is not None:
        expected_order_item['show_vendor_code'] = show_vendor_code
    else:
        expected_order_item['show_vendor_code'] = expected_order_item[
            'sold_by_weight'
        ]

    expected_order_item['barcode_weight_algorithm'] = barcode_weight_encoding
    utils.compare_db_with_expected_data(order_items[0], expected_order_item)


@utils.send_order_events_config()
async def test_create_order_price_string_200(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True,
        images=images,
        measure_v1=False,
        use_string_prices=True,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    utils.compare_db_with_expected_data(order, expected_order)


@utils.marking_types_config()
@pytest.mark.parametrize(
    'marking_type, require_marks',
    [(None, False), ('marked_milk', True), ('another_type', False)],
)
@utils.send_order_events_config()
async def test_create_order_marking_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        get_order_items,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
        mock_nmn_products_info,
        generate_product_info,
        marking_type,
        require_marks,
):
    item_data = generate_order_item_data(
        is_catch_weight=True, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    public_id = '54321'
    mock_eats_products_public_id(
        [{'origin_id': '12345', 'public_id': public_id}],
    )
    mock_nmn_products_info(
        [generate_product_info(public_id, 'product_name', [], marking_type)],
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    order_items = get_order_items(order['id'])
    assert order_items[0]['require_marks'] == require_marks


@pytest.mark.parametrize('is_catch_weight', [False, True])
@utils.send_order_events_config()
async def test_create_order_duplicated_measure_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        get_order_items,
        load_json,
        is_catch_weight,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    measure_value = 500
    quantum = 0.8
    quantum_price = 20
    price = 25
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight,
        images=images,
        measure_value=measure_value,
        measure_quantum=quantum,
        quantum_price=quantum_price,
        price=price,
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    order_items = get_order_items(order_id=order['id'])
    assert len(order_items) == 1

    expected_order_item = load_json('expected_order_item_measure_v2.json')
    expected_order_item['sold_by_weight'] = is_catch_weight

    utils.compare_db_with_expected_data(order_items[0], expected_order_item)


@pytest.mark.parametrize('is_catch_weight', [False, True])
async def test_create_order_missing_measure_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        is_catch_weight,
        mock_eatspickeritemcategories,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight, images=images, measure_v1=True,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@pytest.mark.parametrize('is_catch_weight', [False, True])
async def test_create_order_missing_price_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        is_catch_weight,
        mock_eatspickeritemcategories,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight, images=images, price=None,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'measure_v1, measure_quantum, quantum_price',
    [[False, 1, 100], [True, None, None]],
)
async def test_create_order_missing_max_overweight_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        measure_v1,
        measure_quantum,
        quantum_price,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True,
        images=images,
        measure_max_overweight=None,
        measure_quantum=measure_quantum,
        quantum_price=quantum_price,
        measure_v1=measure_v1,
        price=100,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@pytest.mark.parametrize('is_catch_weight', [False, True])
@pytest.mark.parametrize(
    'measure_quantum, quantum_price, price, is_mismatch',
    [
        (0.8, 20, 30, True),
        (0.799, 210.94, 264, True),
        (0.799, 210.936, 264, False),
        (0.9, 90, 100, False),
    ],
)
@utils.send_order_events_config()
async def test_create_order_price_mismatch(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        is_catch_weight,
        mock_eatspickeritemcategories,
        measure_quantum,
        quantum_price,
        price,
        is_mismatch,
        mock_processing,
        mock_eats_products_public_id,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight,
        images=images,
        measure_v1=False,
        measure_quantum=measure_quantum,
        quantum_price=quantum_price,
        price=price,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    if is_mismatch:
        assert response.status == 400
        assert response.json()['errors'][0]['description'] == 'Prices mismatch'
    else:
        assert response.status == 200
        assert mock_processing.times_called == 1


@pytest.mark.parametrize('is_catch_weight', [False, True])
@pytest.mark.parametrize(
    'measure_update',
    [{'value': 1000}, {'unit': 'GRM'}, {'max_overweight': 100}],
)
async def test_create_order_measures_mismatch_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        is_catch_weight,
        measure_update,
        mock_eatspickeritemcategories,
):
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=is_catch_weight,
        images=images,
        measure_value=500,
        measure_quantum=0.8,
        quantum_price=19,
    )
    item_data['measure'].update(measure_update)
    order_data = generate_order_data(items=[item_data])
    order_data['require_approval'] = True

    mock_eatspickeritemcategories(order_data['place_id'])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@pytest.mark.parametrize('measure_value, quantum', [[500, 0], [0, 0.75]])
async def test_create_order_incorrect_quantum_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        mock_eatspickeritemcategories,
        measure_value,
        quantum,
        mock_eats_products_public_id,
):
    quantum_price = 20
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        images=images,
        measure_value=measure_value,
        measure_quantum=quantum,
        quantum_price=quantum_price,
        price=None,
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


async def test_create_order_missing_measure_v2_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        mock_eatspickeritemcategories,
):
    item_data = generate_order_item_data(measure_v1=True)
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 400


@utils.send_order_events_config()
async def test_create_order_with_customer_id(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
):
    customer_id = '123'
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True, images=images, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    order_data['customer_id'] = customer_id
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    expected_order['customer_id'] = customer_id
    utils.compare_db_with_expected_data(order, expected_order)


@pytest.mark.parametrize(
    'slot_start, slot_end, estimated_delivery_time, expected_response_code',
    [
        (
            '2021-01-01T12:00:00+03:00',
            '2021-01-01T14:00:00+03:00',
            '2021-01-01T15:00:00+03:00',
            200,
        ),
        (None, None, '2021-01-01T15:00:00+03:00', 200),
        (None, '2021-01-01T14:00:00+03:00', '2021-01-01T15:00:00+03:00', 400),
        ('2021-01-01T14:00:00+03:00', None, '2021-01-01T15:00:00+03:00', 400),
        ('2021-01-01T14:00:00+03:00', '2021-01-01T15:00:00+03:00', None, 400),
    ],
)
async def test_create_order_with_slots(
        load_json,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        slot_start,
        slot_end,
        estimated_delivery_time,
        expected_response_code,
        mock_eats_products_public_id,
):
    region_id = 'region_id'
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        is_catch_weight=True, images=images, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])
    order_data['slot_start'] = slot_start
    order_data['slot_end'] = slot_end
    order_data['estimated_delivery_time'] = estimated_delivery_time
    order_data['region_id'] = region_id

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == expected_response_code
    if expected_response_code == 200:
        order = get_order_by_eats_id(eats_id=order_data['eats_id'])
        expected_order = load_json('expected_order.json')
        expected_order['slot_start'] = slot_start
        expected_order['slot_end'] = slot_end
        expected_order['estimated_delivery_time'] = estimated_delivery_time
        expected_order['region_id'] = region_id

        utils.compare_db_with_expected_data(order, expected_order)


@pytest.mark.parametrize(
    """eats_products_status, eats_products_response,
       eats_nomenclature_status, eats_nomenclature_products_info""",
    [
        pytest.param(
            500,
            [],
            200,
            [
                {
                    'name': 'name_1',
                    'id': 12345,
                    'images': ['https://localhost/img1.jpg'],
                },
            ],
            id='eats_products_500',
        ),
        pytest.param(
            200,
            [{'origin_id': '12345', 'public_id': '1'}],
            200,
            [],
            id='eats_nomenclature_empty_response',
        ),
        pytest.param(
            200,
            [{'origin_id': '12345', 'public_id': '1'}],
            404,
            [],
            id='eats_nomenclature_404',
        ),
        pytest.param(
            200,
            [{'origin_id': '12345', 'public_id': '1'}],
            500,
            [],
            id='eats_nomenclature_500',
        ),
    ],
)
@utils.send_order_events_config()
async def test_products_and_nomenclature_errors(
        load_json,
        taxi_config,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
        mock_nmn_products_info,
        generate_product_info,
        get_order_items,
        eats_products_status,
        eats_products_response,
        eats_nomenclature_status,
        eats_nomenclature_products_info,
):
    # This test checks that names and images are not replaced in
    # case of eats-products/eats-nomenclature errors
    # (or empty response from eats-products/eats-nomenclature).

    taxi_config.set_values(
        {
            'EATS_PICKER_ORDERS_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'replace_names_and_inages': True,
            },
        },
    )

    name = 'Name'
    images = [{'url': 'https://localhost/img.jpg'}]
    item_data = generate_order_item_data(
        images=images, name=name, measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id(
        status=eats_products_status, product_ids=eats_products_response,
    )
    eats_nomenclature_response = [
        generate_product_info(
            product_info['id'], product_info['name'], product_info['images'],
        )
        for product_info in eats_nomenclature_products_info
    ]
    mock_nmn_products_info(
        status=eats_nomenclature_status,
        products_info=eats_nomenclature_response,
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    utils.compare_db_with_expected_data(order, expected_order)

    order_items = get_order_items(order_id=order['id'])
    assert len(order_items) == 1
    assert order_items[0]['name'] == name
    assert order_items[0]['images'] == [image['url'] for image in images]


@pytest.mark.parametrize('config_replace_names_and_images', [True, False])
@pytest.mark.parametrize(
    """request_product_info,
       eats_nomenclature_product_info,
       expected_product_info""",
    [
        pytest.param(
            {'name': 'Request name', 'images': ['https://localhost/img.jpg']},
            {
                'name': 'Nomenclature name',
                'images': [
                    'https://localhost/nomenclature_img1.jpg',
                    'https://localhost/nomenclature_img2.jpg',
                ],
            },
            {
                'name': 'Nomenclature name',
                'images': [
                    'https://localhost/nomenclature_img2.jpg',
                    'https://localhost/nomenclature_img1.jpg',
                ],
            },
            id='replace name and images',
        ),
        pytest.param(
            {'name': 'Request name', 'images': ['https://localhost/img.jpg']},
            {'name': 'Nomenclature name', 'images': []},
            {
                'name': 'Nomenclature name',
                'images': ['https://localhost/img.jpg'],
            },
            id='replace only name',
        ),
    ],
)
@utils.send_order_events_config()
async def test_replace_names_and_images(
        load_json,
        taxi_config,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_order_data,
        generate_order_item_data,
        get_order_by_eats_id,
        mock_eatspickeritemcategories,
        mock_processing,
        mock_eats_products_public_id,
        mock_nmn_products_info,
        generate_product_info,
        get_order_items,
        request_product_info,
        eats_nomenclature_product_info,
        expected_product_info,
        config_replace_names_and_images,
):
    # This test checks that name is replaced and images are replaced
    # if they are not empty and config_replace_names_and_images is true.

    taxi_config.set_values(
        {
            'EATS_PICKER_ORDERS_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'replace_names_and_images': config_replace_names_and_images,
            },
        },
    )

    origin_id = '12345'
    public_id = '1'
    item_data = generate_order_item_data(
        id_=origin_id,
        images=[{'url': url} for url in request_product_info['images']],
        name=request_product_info['name'],
        measure_v1=False,
    )
    order_data = generate_order_data(items=[item_data])

    mock_eatspickeritemcategories(order_data['place_id'])

    mock_eats_products_public_id(
        status=200,
        product_ids=[{'origin_id': origin_id, 'public_id': public_id}],
    )
    product_info = generate_product_info(
        public_id,
        eats_nomenclature_product_info['name'],
        eats_nomenclature_product_info['images'],
    )
    mock_nmn_products_info(status=200, products_info=[product_info])

    response = await taxi_eats_picker_orders.post(
        '/api/v1/order', json=order_data,
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id=order_data['eats_id'])
    expected_order = load_json('expected_order.json')
    utils.compare_db_with_expected_data(order, expected_order)

    order_items = get_order_items(order_id=order['id'])
    assert len(order_items) == 1
    if config_replace_names_and_images:
        assert order_items[0]['name'] == expected_product_info['name']
        assert order_items[0]['images'] == expected_product_info['images']
    else:
        assert order_items[0]['name'] == request_product_info['name']
        assert order_items[0]['images'] == request_product_info['images']
