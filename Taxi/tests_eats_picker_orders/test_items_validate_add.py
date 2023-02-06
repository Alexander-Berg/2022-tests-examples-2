# pylint: disable=too-many-lines
import pytest

from . import utils


@pytest.mark.parametrize(
    'measure_value, measure_quantum', [[1000, 0.75], [0, 1]],
)
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('sold_by_weight', [False, True])
@pytest.mark.parametrize(
    'request_body',
    (
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-1',
                        'vendor_code': '7777',
                        'quantity': 1,
                    },
                ],
            },
            id='add_existing',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-1',
                        'vendor_code': '7777',
                        'quantity': 100,
                    },
                    {
                        'eats_item_id': 'item-3',
                        'vendor_code': '7777',
                        'quantity': 300,
                    },
                ],
            },
            id='add_existing_and_new',
        ),
    ),
)
async def test_items_validate_add_quantity(
        mockserver,
        mock_eatspickeritemcategories,
        generate_integration_item_data,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        sold_by_weight,
        request_body,
        measure_version,
        measure_value: int,
        measure_quantum: float,
):
    price_for_items = {'item-1': 11, 'item-2': 12, 'item-3': 13}
    initial_quantity = {'item-1': 10, 'item-2': 20}
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
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

    initial_value = sum(
        quantity * price_for_items[eats_item_id]
        for eats_item_id, quantity in initial_quantity.items()
    )
    added_value = sum(
        item['quantity'] * price_for_items[item['eats_item_id']]
        for item in request_body['items']
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=sold_by_weight,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=price,
                    measure_quantum=measure_quantum,
                    measure_value=measure_value,
                ),
                'barcode': item_id,
                'sku': item_id,
            }
            for item_id, price in price_for_items.items()
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    order = get_order(order_id)

    params = {'eats_id': eats_id}
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )

    if initial_value + added_value <= payment_limit:
        assert response.status_code == 200
    else:
        assert response.status_code == 422
        assert response.json()['code'] == 'payment_limit_exceeded'
        assert response.json()['details']['limit_overrun'] == '4350.00'

    assert order == get_order(order_id)


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('require_approval', [None, False, True])
@pytest.mark.parametrize(
    'request_body',
    (
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-1',
                        'vendor_code': '7777',
                        'weight': 1000,
                    },
                ],
            },
            id='add_existing_by_weight',
        ),
    ),
)
async def test_items_validate_add_weight(
        mockserver,
        mock_eatspickeritemcategories,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_integration_item_data,
        create_order,
        create_order_item,
        get_order,
        require_approval,
        request_body,
        measure_version,
):
    measure_quantum = 0.75
    measure_value = 1000
    price_for_items = {'item-1': 11, 'item-2': 12, 'item-3': 13}
    initial_quantity = {'item-1': 10, 'item-2': 20}
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        require_approval=require_approval,
    )
    for eats_item_id, quantity in initial_quantity.items():
        create_order_item(
            order_id=order_id,
            eats_item_id=eats_item_id,
            quantity=quantity,
            price=price_for_items[eats_item_id],
            measure_value=measure_value,
            sold_by_weight=True,
        )

    initial_value = sum(
        quantity * price_for_items[eats_item_id]
        for eats_item_id, quantity in initial_quantity.items()
    )
    added_value = sum(
        item['weight'] / measure_value * price_for_items[item['eats_item_id']]
        for item in request_body['items']
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=True,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=price,
                    measure_quantum=measure_quantum,
                    measure_value=measure_value,
                ),
                'barcode': item_id,
                'sku': item_id,
            }
            for item_id, price in price_for_items.items()
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    order = get_order(order_id)

    params = {'eats_id': eats_id}
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )

    if initial_value + added_value <= payment_limit:
        assert response.status_code == 200
    else:
        assert response.status_code == 422
        assert response.json()['code'] == 'payment_limit_exceeded'
        assert response.json()['details']['limit_overrun'] == '1.0'

    assert order == get_order(order_id)


async def test_items_validate_add_400_bad_request(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id},
        json={'items': [{'eats_item_id': 'item-1', 'quantity': 5.5}]},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'empty_addition'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'is_catch_weight, quantity', [[True, 0], [False, 0], [False, 0.9]],
)
async def test_items_validate_add_400_wrong_quantity(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        create_order,
        generate_integration_item_data,
        is_catch_weight,
        quantity,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=is_catch_weight,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'eats_item_id': item_id,
                    'vendor_code': item_id,
                    'quantity': quantity,
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
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
async def test_items_validate_add_400_bad_field_set(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        create_order,
        generate_integration_item_data,
        is_catch_weight,
        quantity_fields: dict,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=is_catch_weight,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
        json={
            'items': [
                dict(
                    {'eats_item_id': item_id, 'vendor_code': item_id},
                    **quantity_fields,
                ),
            ],
        },
    )
    assert response.status_code == 400


async def test_items_validate_add_404_order_not_found(
        taxi_eats_picker_orders, init_measure_units, init_currencies,
):
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers('1122'),
        params={'eats_id': '123'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found_for_picker'


async def test_items_validate_add_412_no_items(
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        return {'matched_items': [], 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
async def test_items_validate_add_412_not_matched_items(
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = generate_integration_item_data(
            origin_id='item-1', measure_quantum=0.75,
        )
        return {
            'matched_items': [{'barcode': None, 'sku': '7777', 'item': item}],
            'not_matched_items': [
                {'barcode': None, 'sku': '7777', 'item': item},
            ],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
async def test_items_validate_add_412_items_mismatch(
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = generate_integration_item_data(
            origin_id='wrong_item_id',
            vendor_code='7778',
            measure_quantum=0.75,
        )
        return {
            'matched_items': [{'barcode': None, 'sku': '7778', 'item': item}],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'item_mismatch'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
async def test_items_validate_add_412_empty_max_overweight(
        mock_eatspickeritemcategories,
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = generate_integration_item_data(
            origin_id='item-1',
            vendor_code='7777',
            is_catch_weight=True,
            measure_max_overweight=None,
            measure_quantum=0.75,
        )
        return {
            'matched_items': [{'barcode': None, 'sku': '7777', 'item': item}],
            'not_matched_items': [],
        }

    mock_eatspickeritemcategories()

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'weight_parameter_is_missing'


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
    # при добавлении товара к 0 версии итоговое количество = 2
    # и лимит не превышается
    # при добавлении к 1 версии итоговое количество = 3
    # и получаем превышение лимита
    price = 400
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    eats_item_id = 'item-1'
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
        eats_item_id=eats_item_id,
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
        eats_item_id=eats_item_id,
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
                    origin_id=eats_item_id,
                    barcodes=[eats_item_id],
                    vendor_code=eats_item_id,
                    price=price,
                    is_catch_weight=sold_by_weight,
                    measure_quantum=1,
                    measure_value=measure_value,
                ),
                'barcode': eats_item_id,
                'sku': eats_item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    params = {'eats_id': eats_id}
    if request_version is not None:
        params['version'] = request_version
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json={
            'items': [
                {
                    'eats_item_id': eats_item_id,
                    'vendor_code': eats_item_id,
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == expected_status
    if expected_status == 422:
        assert response.json()['details']['limit_overrun'] == '200.00'
    assert get_order(order_id)['last_version'] == 1


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, quantity_expected',
    [
        (None, None, 5),
        ('picker_id', None, 5),
        ('picker_id', 'picker', 5),
        ('system', None, 5),
        ('system', 'system', 5),
        ('customer_id', 'customer', 5),
        ('unknown', None, 5),
        ('unknown', 'picker', 5),
    ],
)
async def test_items_validate_add_200_soft_deleted(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        init_measure_units,
        init_currencies,
        mockserver,
        create_order,
        create_order_item,
        generate_integration_item_data,
        get_order_items,
        is_deleted_by,
        deleted_by_type,
        quantity_expected,
        measure_version,
):
    picker_id = 'picker_id'
    eats_id = '123'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='0',
        quantity=5,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id='0',
                    is_catch_weight=True,
                    barcodes=['0'],
                    vendor_code='0',
                    price=10,
                    measure_quantum=0.75,
                ),
                'barcode': '0',
                'sku': '0',
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers('picker_id', measure_version),
        params={'eats_id': eats_id, 'version': 0},
        json={
            'items': [
                {
                    'eats_item_id': '0',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200
    items = get_order_items(order_id=order_id, version=0)
    assert len(items) == 1
    assert items[0]['is_deleted_by'] == is_deleted_by
    assert items[0]['deleted_by_type'] == deleted_by_type
    assert items[0]['quantity'] == quantity_expected


@pytest.mark.parametrize(
    'measure_version, limit_overrun',
    [(None, '200.00'), ('1', '200.00'), ('2', '199.93')],
)
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, status',
    [
        (None, None, 422),
        ('1122', None, 200),
        ('1122', 'picker', 200),
        ('system', None, 200),
        ('system', 'system', 200),
        ('customer_id', 'customer', 200),
        ('unknown', None, 422),
        ('unknown', 'picker', 422),
    ],
)
async def test_items_validate_add_soft_deleted_limit(
        mock_eatspickeritemcategories,
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        is_deleted_by,
        deleted_by_type,
        status,
        measure_version,
        limit_overrun,
):
    payment_limit = 1100
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        require_approval=False,
    )
    for i, (quantity, price, soft_deleted) in enumerate(
            [(1, 100, False), (2, 200, False), (1, 500, True)],
    ):
        create_order_item(
            order_id=order_id,
            eats_item_id='item_' + str(i),
            quantity=quantity,
            price=price,
            is_deleted_by=(is_deleted_by if soft_deleted else None),
            deleted_by_type=(deleted_by_type if soft_deleted else None),
        )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item_id = 'item_n'
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=False,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=300,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    params = {'eats_id': eats_id}
    request_body = {
        'items': [
            {'eats_item_id': 'item_n', 'vendor_code': 'item_n', 'quantity': 1},
        ],
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )

    assert response.status_code == status

    if status == 200:
        assert get_order(order_id)['last_version'] == 0
    elif status == 422:
        assert response.json()['code'] == 'payment_limit_exceeded'
        assert response.json()['details']['limit_overrun'] == limit_overrun


async def test_items_validate_add_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/validate-add',
        headers=bad_header,
        params={'eats_id': '123', 'version': 0},
        json={
            'items': [
                {
                    'eats_item_id': '0',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 401
