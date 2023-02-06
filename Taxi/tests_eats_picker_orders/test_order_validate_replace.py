# pylint: disable=too-many-lines
import pytest

from . import utils


@pytest.mark.parametrize('sold_by_weight', [False, True])
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'measure_value, measure_quantum', [[500, 0.75], [0, 1]],
)
@pytest.mark.parametrize(
    'request_body',
    (
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-2',
                        'vendor_code': '7777',
                        'quantity': 10,
                    },
                ],
            },
            id='basic_replacement',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-1',
                        'barcode': '1',
                        'quantity': 1,
                    },
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-2',
                        'barcode': '2',
                        'quantity': 2,
                    },
                ],
            },
            id='replace_1_item_to_self_and_new',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-2',
                        'barcode': '2',
                        'quantity': 1,
                    },
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-3',
                        'barcode': '3',
                        'quantity': 2,
                    },
                ],
            },
            id='replace_2_items_to_two_different',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-4',
                        'barcode': '4',
                        'quantity': 1,
                    },
                    {
                        'old_item_id': 'item-2',
                        'eats_item_id': 'item-4',
                        'barcode': '4',
                        'quantity': 2,
                    },
                ],
            },
            id='replace_2_items_to_new',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-3',
                        'barcode': '3',
                        'quantity': 1,
                    },
                    {
                        'old_item_id': 'item-2',
                        'eats_item_id': 'item-3',
                        'barcode': '3',
                        'quantity': 2,
                    },
                ],
            },
            id='replace_1_item_to_2_existing',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-2',
                        'barcode': '2',
                        'quantity': 1,
                    },
                    {
                        'old_item_id': 'item-2',
                        'eats_item_id': 'item-2',
                        'barcode': '2',
                        'quantity': 2,
                    },
                ],
            },
            id='replace_2_items_to_one_of_them',
        ),
        pytest.param(
            {
                # item-1 не участвует в заменах
                'items': [
                    {
                        # item-2 заменяется, но не заменяет другие товары
                        'old_item_id': 'item-2',
                        'eats_item_id': 'item-3',
                        'barcode': '3',
                        'vendor_code': '3',
                        'quantity': 1,
                    },
                    {
                        # item-3 заменяется сам на себя и на item-4,
                        # заменяет item-2 и item-4
                        'old_item_id': 'item-3',
                        'eats_item_id': 'item-3',
                        'barcode': '3',
                        'vendor_code': '3',
                        'quantity': 2,
                    },
                    {
                        'old_item_id': 'item-3',
                        'eats_item_id': 'item-4',
                        'barcode': '4',
                        'vendor_code': '4',
                        'quantity': 4,
                    },
                    {
                        # item-4 заменяет item-3 и заменяется на item-3,
                        # item-5 и item-6, но не сам на себя
                        'old_item_id': 'item-4',
                        'eats_item_id': 'item-3',
                        'barcode': '3',
                        'vendor_code': '3',
                        'quantity': 8,
                    },
                    {
                        # item-5 не заменяется, но заменяет item-4
                        'old_item_id': 'item-4',
                        'eats_item_id': 'item-5',
                        'barcode': '5',
                        'vendor_code': '5',
                        'quantity': 16,
                    },
                    {
                        # item-6 отсутствует в оригинальном составе заказа
                        'old_item_id': 'item-4',
                        'eats_item_id': 'item-6',
                        'barcode': '6',
                        'vendor_code': '6',
                        'quantity': 32,
                    },
                ],
            },
            id='multi_replacements',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': 'item-2',
                        'barcode': '2',
                        'quantity': 1,
                    },
                    {
                        'old_item_id': 'item-2',
                        'eats_item_id': 'item-1',
                        'barcode': '1',
                        'quantity': 2,
                    },
                ],
            },
            id='cross-replacement',
        ),
    ),
)
async def test_order_validate_replace(
        sold_by_weight,
        measure_version,
        measure_value: int,
        measure_quantum: float,
        request_body,
        init_measure_units,
        init_currencies,
        mock_edadeal,
        mock_eatspickeritemcategories,
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        get_order,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    payment_limit = 1000
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
    )

    price_for_items = {f'item-{i}': 10 + i for i in range(1, 7)}
    initial_quantity = {'item-1': 10, 'item-2': 20, 'item-3': 5, 'item-4': 3}
    initial_value = sum(
        quantity * price_for_items[eats_item_id]
        for eats_item_id, quantity in initial_quantity.items()
    )
    added_value = sum(
        item['quantity'] * price_for_items[item['eats_item_id']]
        for item in request_body['items']
    )
    for eats_item_id, quantity in initial_quantity.items():
        create_order_item(
            order_id=order_id,
            eats_item_id=eats_item_id,
            quantity=quantity,
            price=price_for_items[eats_item_id],
            measure_value=measure_value,
            measure_quantum=int(measure_value * measure_quantum),
            quantum_quantity=quantity / measure_quantum,
            absolute_quantity=quantity * measure_value,
            quantum_price=round(
                price_for_items[eats_item_id] * measure_quantum, 2,
            ),
        )

    mock_eatspickeritemcategories()
    mock_edadeal(sold_by_weight, measure_quantum, measure_value)

    order = get_order(order_id)

    params = {'eats_id': eats_id}
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )

    if initial_value + added_value <= payment_limit:
        assert response.status_code == 200
    else:
        assert response.status_code == 422
        assert response.json()['code'] == 'payment_limit_exceeded'
        assert response.json()['details']['limit_overrun'] == '685.00'

    assert order == get_order(order_id)


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
@pytest.mark.parametrize(
    'request_version, author, author_type, expected_status',
    [
        [None, 'someone', None, 422],
        [0, 'someone', None, 204],
        [1, 'someone', None, 422],
        [None, 'customer', 'customer', 422],
        [0, 'customer', 'customer', 204],
        [1, 'customer', 'customer', 422],
        [None, None, 'system', 422],
        [0, None, 'system', 204],
        [1, None, 'system', 422],
        [None, '1122', 'system', 422],
        [0, '1122', 'system', 204],
        [1, '1122', 'system', 422],
        [None, '1122', 'picker', 422],
        [0, '1122', 'picker', 204],
        [1, '1122', 'picker', 422],
        [None, 'another_picker', 'system', 200],
        [0, 'another_picker', 'system', 200],
        [1, 'another_picker', 'system', 409],
        [None, 'another_picker', 'picker', 200],
        [0, 'another_picker', 'picker', 200],
        [1, 'another_picker', 'picker', 409],
    ],
)
async def test_items_validate_add_version_author(
        mockserver,
        mock_eatspickeritemcategories,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        handle,
        measure_version,
        request_version,
        author,
        author_type,
        expected_status,
):
    # при замене товара из 0 версии итоговое количество = 1
    # и лимит не превышается
    # при замене из 1 версии итоговое количество = 3
    # и получаем превышение лимита
    price = 400
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    old_item_id = 'item-1'
    new_item_id = 'item-2'
    sold_by_weight = False
    measure_value = 1000
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        last_version=1,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=old_item_id,
        sold_by_weight=sold_by_weight,
        price=price,
        measure_value=measure_value,
        quantity=1,
        version=0,
        author=None,
        author_type=None,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=old_item_id,
        sold_by_weight=sold_by_weight,
        price=price,
        measure_value=measure_value,
        quantity=2,
        version=1,
        author=author,
        author_type=author_type,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=new_item_id,
        sold_by_weight=sold_by_weight,
        price=price,
        measure_value=measure_value,
        quantity=2,
        version=1,
        author=author,
        author_type=author_type,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=new_item_id,
                    barcodes=[new_item_id],
                    vendor_code=new_item_id,
                    price=price,
                    is_catch_weight=sold_by_weight,
                    measure_quantum=1,
                    measure_value=measure_value,
                ),
                'barcode': new_item_id,
                'sku': new_item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    params = {'eats_id': eats_id}
    if request_version is not None:
        params['version'] = request_version
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json={
            'items': [
                {
                    'old_item_id': old_item_id,
                    'eats_item_id': new_item_id,
                    'vendor_code': new_item_id,
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == expected_status
    if expected_status == 422:
        assert response.json()['details']['limit_overrun'] == '200.00'
    assert get_order(order_id)['last_version'] == 1


async def test_order_validate_replace_412_no_items(
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        return {'matched_items': [], 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


async def test_order_validate_replace_412_not_matched_items(
        load_json,
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = load_json('expected_item_measure_v2.json')
        return {
            'matched_items': [{'barcode': None, 'sku': '7777', 'item': item}],
            'not_matched_items': [
                {'barcode': None, 'sku': '7777', 'item': item},
            ],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


async def test_order_validate_replace_412_items_mismatch(
        load_json,
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = load_json('expected_item_measure_v2.json')
        return {
            'matched_items': [
                {'barcode': None, 'sku': 'different-sku', 'item': item},
            ],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7778',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'item_mismatch'


@pytest.mark.parametrize('measure_value, quantum', [[500, 0], [0, 0.75]])
async def test_order_validate_replace_412_incorrect_measure(
        mock_edadeal,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        measure_value,
        quantum,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    mock_edadeal(False, quantum, measure_value)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.make_headers(picker_id, '2'),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '1',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_item_incorrect_measure'


async def test_order_validate_replace_404_order_item_not_found(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'old_item_id': 'wrong-id',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_item_not_found'


@pytest.mark.parametrize(
    'is_catch_weight, quantity', [[True, 0], [False, 0], [False, 0.9]],
)
async def test_order_validate_replace_400_bad_quantity(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        load_json,
        create_order,
        create_order_item,
        is_catch_weight,
        quantity,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=1.0, price=10,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item_measure_v2.json')
        expected_item['is_catch_weight'] = is_catch_weight
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'old_item_id': item_id,
                    'vendor_code': '7777',
                    'quantity': quantity,
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'is_catch_weight, quantity_fields',
    [
        [True, {}],
        [True, {'quantity': 1, 'weight': 100}],
        [False, {}],
        [False, {'weight': 100}],
        [False, {'quantity': 1, 'weight': 100}],
    ],
)
async def test_order_validate_replace_400_bad_field_set(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        load_json,
        create_order,
        create_order_item,
        is_catch_weight,
        quantity_fields: dict,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=1.0, price=10,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item_measure_v2.json')
        expected_item['is_catch_weight'] = is_catch_weight
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                dict(
                    {'old_item_id': item_id, 'vendor_code': '7777'},
                    **quantity_fields,
                ),
            ],
        },
    )
    assert response.status_code == 400


async def test_order_validate_replace_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/validate-replace',
        headers=bad_header,
        params={'eats_id': '123'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 401
