# pylint: disable=too-many-lines


def make_expected_cart_diff_request(order, expected):
    order_items = order['order_items']
    picked_items = order['picked_items']
    operations = []
    if 'update' in expected:
        for update in expected['update']:
            order_item_i = update['order_item']
            order_item = order_items[order_item_i]
            operation = {
                'operation_type': 'update',
                'update_values': [],
                'identity': order_item['eats_item_id'],
                'quantity': float(order_item['quantity']),
                'quantum': float(order_item['relative_quantum']),
                'price': {
                    'amount': f'{order_item["price"]:.2f}',
                    'currency': 'RUB',
                },
                'options': [],
            }
            if 'quantity' in update:
                operation['update_values'].append(
                    {'name': 'quantity', 'value': float(update['quantity'])},
                )
            if 'price' in update:
                operation['update_values'].append(
                    {
                        'name': 'price',
                        'value': {
                            'amount': update['price'],
                            'currency': 'RUB',
                        },
                    },
                )
            operations.append(operation)
    if 'remove' in expected:
        for remove in expected['remove']:
            order_item_i = remove['order_item']
            order_item = order_items[order_item_i]
            operation = {
                'operation_type': 'remove',
                'identity': order_item['eats_item_id'],
                'quantity': float(order_item['quantity']),
                'quantum': float(order_item['relative_quantum']),
                'price': {
                    'amount': f'{order_item["price"]:.2f}',
                    'currency': 'RUB',
                },
                'options': [],
            }
            operations.append(operation)
    if 'add' in expected:
        for add in expected['add']:
            operation = {
                'operation_type': 'add',
                'options': [],
                'price': {'currency': 'RUB'},
                'vat': None,
            }
            if 'picked_item' in add:
                picked_item_i = add['picked_item']
                picked_item = picked_items[picked_item_i]
                order_item = order_items[picked_item['order_item']]
                operation['identity'] = order_item['eats_item_id']
                operation['name'] = 'Foo bar'
                operation['price']['amount'] = (
                    add['price']
                    if 'price' in add
                    else f'{order_item["price"]:.2f}'
                )
                if 'count' in picked_item:
                    quantity = float(picked_item['count'])
                    weight = float(picked_item['count'])
                else:
                    quantity = (
                        picked_item['weight'] / order_item['measure_value']
                    )
                    weight = float(picked_item['weight'])
                operation['quantity'] = quantity
                operation['quantum'] = float(order_item['relative_quantum'])
                operation['weight'] = weight
            else:
                operation['identity'] = 'cost_for_place_change_item'
                operation[
                    'name'
                ] = 'Дополнительная сумма по заказу из магазина'
                operation['price']['amount'] = add['price']
                operation['quantity'] = float(add['quantity'])
                operation['quantum'] = float(add['quantity'])
                operation['weight'] = 0.0
            operations.append(operation)
    operations = sorted(operations, key=lambda x: x['identity'])
    return {'order_id': 'eats_id_0', 'offer': {'operations': operations}}


def get_test_cases_without_aligner():
    return [
        (
            {
                'last_version': 0,
                'amount': 10.0,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                ],
            },
            {},
        ),
        (
            {
                'last_version': 0,
                'amount': 10.0,
                'order_items': [],
                'picked_items': [],
            },
            {},
        ),
        (
            {
                'last_version': 0,
                'amount': 10.00,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 11.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                ],
            },
            {},
        ),
        (
            {
                'last_version': 0,
                'amount': 10.77,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 2,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 2,
                        'quantum_price': 5.0,
                        'absolute_quantity': 2,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 3, 'cart_version': 0},
                ],
            },
            {'update': [{'order_item': 0, 'quantity': 3.0}]},
        ),
        (
            {
                'last_version': 1,
                'amount': 10.77,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 2,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 2,
                        'quantum_price': 5.0,
                        'absolute_quantity': 2,
                    },
                    {
                        'eats_item_id': '0',
                        'version': 1,
                        'quantity': 2,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 2,
                        'quantum_price': 5.0,
                        'absolute_quantity': 2,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 3, 'cart_version': 0},
                ],
            },
            {'update': [{'order_item': 0, 'quantity': 3.0}]},
        ),
        (
            {
                'last_version': 1,
                'amount': 1502.58,
                'order_items': [
                    {
                        'eats_item_id': '245',
                        'version': 0,
                        'quantity': 2.5,
                        'measure_value': 300,
                        'measure_quantum': 250,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 750,
                    },
                    {
                        'eats_item_id': '542',
                        'version': 0,
                        'quantity': 3,
                        'measure_quantum': 1,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 3,
                    },
                    {
                        'eats_item_id': '1234',
                        'version': 0,
                        'quantity': 1.5,
                        'measure_value': 200,
                        'measure_quantum': 100,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': '4321',
                        'version': 0,
                        'quantity': 1.5,
                        'measure_value': 400,
                        'measure_quantum': 300,
                        'quantum_quantity': 2,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': 'delete-1',
                        'version': 0,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'delete-2',
                        'version': 0,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'replace-1',
                        'version': 0,
                        'quantity': 2,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantum_quantity': 4,
                        'quantum_price': 1.0,
                        'absolute_quantity': 2000,
                    },
                    {
                        'eats_item_id': 'replace-2',
                        'version': 0,
                        'quantity': 2,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantum_quantity': 4,
                        'quantum_price': 1.0,
                        'absolute_quantity': 2000,
                    },
                    {
                        'eats_item_id': '245',
                        'version': 1,
                        'quantity': 2.5,
                        'measure_value': 300,
                        'measure_quantum': 250,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 750,
                    },
                    {
                        'eats_item_id': '542',
                        'version': 1,
                        'quantity': 3,
                        'measure_quantum': 1,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 3,
                    },
                    {
                        'eats_item_id': '1234',
                        'version': 1,
                        'quantity': 1.5,
                        'measure_value': 200,
                        'measure_quantum': 100,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': '4321',
                        'version': 1,
                        'quantity': 1.5,
                        'measure_value': 400,
                        'measure_quantum': 300,
                        'quantum_quantity': 2,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': 'add',
                        'version': 1,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'delete-1',
                        'version': 1,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'replacement',
                        'version': 1,
                        'quantity': 5,
                        'measure_value': 100,
                        'measure_quantum': 50,
                        'quantum_quantity': 10,
                        'quantum_price': 1.0,
                        'absolute_quantity': 500,
                        'replacements': [6, 7],
                    },
                ],
                'picked_items': [
                    {
                        'order_item': 2,
                        'weight': 280,
                        'cart_version': 1,
                    },  # 1234
                    {
                        'order_item': 3,
                        'weight': 600,
                        'cart_version': 1,
                    },  # 4321
                    {
                        'order_item': 4,
                        'count': 3,
                        'cart_version': 1,
                    },  # delete-1
                    {'order_item': 8, 'weight': 750, 'cart_version': 2},  # 245
                    {'order_item': 9, 'count': 3, 'cart_version': 2},  # 542
                    {
                        'order_item': 10,
                        'weight': 320,
                        'cart_version': 2,
                    },  # 1234
                    {
                        'order_item': 11,
                        'weight': 560,
                        'cart_version': 2,
                    },  # 4321
                    {'order_item': 12, 'count': 3, 'cart_version': 2},  # add
                    {
                        'order_item': 14,
                        'weight': 400,
                        'cart_version': 2,
                    },  # replacement
                ],
            },
            {
                'remove': [
                    {'order_item': 4},  # remove-1
                    {'order_item': 5},  # remove-2
                    {'order_item': 6},  # replace-1
                    {'order_item': 7},  # replace-2
                ],
                'add': [
                    {'picked_item': 7, 'price': '10.00'},  # add
                    {'picked_item': 8, 'price': '10.00'},  # replacement
                ],
                'update': [
                    {'order_item': 2, 'quantity': 1.6},  # 1234
                    {'order_item': 3, 'quantity': 1.4},  # 4321
                ],
            },
        ),
        (
            {
                'last_version': 1,
                'amount': 128.0,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 1,
                        'quantum_quantity': 3,
                        'price': 5.0,
                        'quantum_price': 7.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 2,
                        'quantum_quantity': 4,
                        'price': 6.0,
                        'quantum_price': 8.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 1,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 3,
                        'quantum_quantity': 5,
                        'price': 7.0,
                        'quantum_price': 9.0,
                        'absolute_quantity': 1500,
                        'replacements': [0],
                    },
                    {
                        'eats_item_id': '3',
                        'version': 1,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 4,
                        'quantum_quantity': 6,
                        'price': 8.0,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1500,
                        'replacements': [1],
                    },
                    {
                        'eats_item_id': '4',
                        'version': 0,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 4,
                        'quantum_quantity': 7,
                        'price': 9.0,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '5',
                        'version': 0,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 5,
                        'quantum_quantity': 8,
                        'price': 10.0,
                        'quantum_price': 12.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '6',
                        'version': 0,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 1,
                        'quantum_quantity': 2,
                        'price': 10.0,
                        'quantum_price': 5.0,
                        'absolute_quantity': 1000,
                    },
                    {
                        'eats_item_id': '4',
                        'version': 1,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 7,
                        'quantum_quantity': 9,
                        'price': 11.0,
                        'quantum_price': 13.0,
                        'absolute_quantity': 1500,
                        'replacements': [4],
                    },
                    {
                        'eats_item_id': '5',
                        'version': 1,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 8,
                        'quantum_quantity': 10,
                        'price': 12.0,
                        'quantum_price': 14.0,
                        'absolute_quantity': 1500,
                        'replacements': [5],
                    },
                    {
                        'eats_item_id': '6',
                        'version': 1,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 1,
                        'quantum_quantity': 2,
                        'price': 20.0,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1000,
                    },
                ],
                'picked_items': [
                    {'order_item': 2, 'count': 3, 'cart_version': 1},
                    {'order_item': 3, 'weight': 2000, 'cart_version': 1},
                    {'order_item': 4, 'count': 5, 'cart_version': 1},
                    {'order_item': 5, 'weight': 3000, 'cart_version': 1},
                    {'order_item': 6, 'weight': 1000, 'cart_version': 1},
                ],
            },
            {
                'update': [
                    {'order_item': 4, 'quantity': 5.0, 'price': '11.00'},
                    {'order_item': 5, 'quantity': 3.0, 'price': '12.00'},
                    {'order_item': 6, 'price': '20.00'},
                ],
                'add': [
                    {'picked_item': 0, 'price': '7.00'},
                    {'picked_item': 1, 'price': '8.00'},
                ],
                'remove': [{'order_item': 0}, {'order_item': 1}],
            },
        ),
    ]


def get_test_cases_with_aligner():
    return [
        (
            {
                'last_version': 0,
                'amount': 10.0,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                ],
            },
            {},
        ),
        (
            {
                'last_version': 0,
                'amount': 10.0,
                'order_items': [],
                'picked_items': [],
            },
            {'add': [{'quantity': 1.0, 'price': '10.00'}]},
        ),
        (
            {
                'last_version': 0,
                'amount': 10.00,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 11.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                ],
            },
            {'update': [{'order_item': 0, 'price': '10.00'}]},
        ),
        (
            {
                'last_version': 0,
                'amount': 11.00,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                ],
            },
            {
                'update': [{'order_item': 0, 'price': '10.00'}],
                'add': [{'quantity': 1.0, 'price': '1.00'}],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 10.77,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 2,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 2,
                        'quantum_price': 5.0,
                        'absolute_quantity': 2,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 2, 'cart_version': 0},
                ],
            },
            # residuals: 0.77
            # amount is bigger than order_total,
            # so fake_item will be added with residual as amount
            {
                'update': [{'order_item': 0, 'price': '5.00'}],
                'add': [{'quantity': 1.0, 'price': '0.77'}],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 9.98,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 3,
                        'price': 3.33,
                        'measure_quantum': 1,
                        'quantum_quantity': 3,
                        'quantum_price': 3.33,
                        'absolute_quantity': 3,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 3, 'cart_version': 0},
                ],
            },
            # share: 1
            # residual: -0.01
            # items: 3.33 = 9.99 (+1)
            # items: 3.32 = 9.96 (-2)
            {
                'update': [{'order_item': 0, 'price': '3.32'}],
                'add': [{'quantity': 1.0, 'price': '0.02'}],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 20.00,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 1, 'cart_version': 0},
                ],
            },
            {},
        ),
        (
            {
                'last_version': 0,
                'amount': 100.00,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 1, 'cart_version': 0},
                ],
            },
            {
                'update': [
                    {'order_item': 0, 'price': '10.00'},
                    {'order_item': 1, 'price': '10.00'},
                ],
                'add': [{'quantity': 1, 'price': '80.00'}],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 33.33,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 11.11,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.11,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 11.11,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.11,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 0,
                        'quantity': 1,
                        'price': 11.11,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 11.11,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 1, 'cart_version': 0},
                    {'order_item': 2, 'count': 1, 'cart_version': 0},
                ],
            },
            {},
        ),
        (
            {
                'last_version': 0,
                'amount': 100.00,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 1, 'cart_version': 0},
                    {'order_item': 2, 'count': 1, 'cart_version': 0},
                ],
            },
            {
                'add': [{'quantity': 1.0, 'price': '70.00'}],
                'update': [
                    {'order_item': 0, 'price': '10.00'},
                    {'order_item': 1, 'price': '10.00'},
                    {'order_item': 2, 'price': '10.00'},
                ],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 33.33,
                'order_items': [
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 1, 'cart_version': 0},
                ],
            },
            {
                'add': [{'quantity': 1.0, 'price': '13.33'}],
                'update': [
                    {'order_item': 0, 'price': '10.00'},
                    {'order_item': 1, 'price': '10.00'},
                ],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 94.67,
                'order_items': [
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 0,
                        'quantity': 1,
                        'price': 20.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 20.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '3',
                        'version': 0,
                        'quantity': 1,
                        'price': 30.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 30.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 1, 'cart_version': 0},
                    {'order_item': 2, 'count': 1, 'cart_version': 0},
                ],
            },
            {
                'add': [{'quantity': 1.0, 'price': '34.67'}],
                'update': [
                    {'order_item': 0, 'price': '10.00'},
                    {'order_item': 1, 'price': '20.00'},
                    {'order_item': 2, 'price': '30.00'},
                ],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 200,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 10.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 2,
                        'price': 20.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 20.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 0,
                        'quantity': 3,
                        'price': 30.00,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 30.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                    {'order_item': 1, 'count': 2, 'cart_version': 0},
                    {'order_item': 2, 'count': 3, 'cart_version': 0},
                ],
            },
            # residual = 200 - 140 = 60
            # amount is bigger than order_total,
            # so fake_item will be added with residual as amount
            {
                'update': [
                    {'order_item': 0, 'price': '10.00'},
                    {'order_item': 1, 'price': '20.00'},
                    {'order_item': 2, 'price': '30.00'},
                ],
                'add': [{'quantity': 1, 'price': '60.00'}],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 10.0,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 0,
                        'price': 10.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 0,
                        'quantum_price': 10.0,
                        'absolute_quantity': 0,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 1, 'cart_version': 0},
                ],
            },
            {'update': [{'order_item': 0, 'quantity': 1.0}]},
        ),
        (
            {
                'last_version': 0,
                'amount': 10,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 5.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'count': 2, 'cart_version': 0},
                ],
            },
            {'update': [{'order_item': 0, 'quantity': 2.0}]},
        ),
        (
            {
                'last_version': 1,
                'amount': 10,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 5.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 3.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 3.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '0',
                        'version': 1,
                        'quantity': 1,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 5.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 2, 'count': 1, 'cart_version': 1},
                ],
            },
            {
                'remove': [{'order_item': 1}],
                'update': [{'order_item': 2, 'price': '5.00'}],
                'add': [{'quantity': 1, 'price': '5.00'}],
            },
        ),
        (
            {
                'last_version': 1,
                'amount': 10,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 3.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 3.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '0',
                        'version': 1,
                        'quantity': 1,
                        'price': 3.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 3.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 1,
                        'quantity': 1,
                        'price': 5.0,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 5.0,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 1, 'count': 1, 'cart_version': 1},
                    {
                        'order_item': 2,
                        'count': 1,
                        'weight': 1.0,
                        'cart_version': 1,
                    },
                ],
            },
            # residual = 10 - 8 = 2
            # amount is bigger than order_total,
            # so fake_item will be added with residual as amount
            {
                'update': [{'order_item': 1, 'price': '3.00'}],
                'add': [
                    {'picked_item': 1, 'price': '5.00'},
                    {'quantity': 1, 'price': '2.00'},
                ],
            },
        ),
        (
            {
                'last_version': 0,
                'amount': 17.17,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1.5,
                        'measure_value': 200,
                        'price': 5.34,
                        'measure_quantum': 100,
                        'quantum_quantity': 3,
                        'quantum_price': 2.67,
                        'absolute_quantity': 300,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 2.11,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 2.11,
                        'absolute_quantity': 1,
                    },
                ],
                'picked_items': [
                    {'order_item': 0, 'weight': 400, 'cart_version': 1},
                    {'order_item': 1, 'count': 1, 'cart_version': 1},
                ],
            },
            # residual = 17.17 - 5.34 * 2 - 2.11 = 17.17 - 12.79 = 4.38
            # amount is bigger than order_total,
            # so fake_item will be added with residual as amount
            {
                'update': [
                    {'order_item': 0, 'quantity': 2.0, 'price': '5.34'},
                    {'order_item': 1, 'price': '2.11'},
                ],
                'add': [{'quantity': 1, 'price': '4.38'}],
            },
        ),
        (
            {
                'last_version': 1,
                'amount': 10.0,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'quantity': 1,
                        'price': 4,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 4.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'quantity': 1,
                        'price': 4,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 4.0,
                        'absolute_quantity': 1,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 1,
                        'quantity': 1,
                        'price': 7,
                        'measure_quantum': 1,
                        'quantum_quantity': 1,
                        'quantum_price': 7.0,
                        'absolute_quantity': 1,
                        'replacements': [0, 1],
                    },
                ],
                'picked_items': [
                    {'order_item': 2, 'count': 1, 'cart_version': 1},
                ],
            },
            {
                'remove': [{'order_item': 0}, {'order_item': 1}],
                'add': [
                    {'picked_item': 0, 'price': '7.00'},
                    {'quantity': 1, 'price': '3.00'},
                ],
            },
        ),
        (
            {
                'last_version': 1,
                'amount': 1502.58,
                'order_items': [
                    {
                        'eats_item_id': '245',
                        'version': 0,
                        'quantity': 2.5,
                        'measure_value': 300,
                        'measure_quantum': 250,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 750,
                    },
                    {
                        'eats_item_id': '542',
                        'version': 0,
                        'quantity': 3,
                        'measure_quantum': 1,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 3,
                    },
                    {
                        'eats_item_id': '1234',
                        'version': 0,
                        'quantity': 1.5,
                        'measure_value': 200,
                        'measure_quantum': 100,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': '4321',
                        'version': 0,
                        'quantity': 1.5,
                        'measure_value': 400,
                        'measure_quantum': 300,
                        'quantum_quantity': 2,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': 'delete-1',
                        'version': 0,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'delete-2',
                        'version': 0,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'replace-1',
                        'version': 0,
                        'quantity': 2,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantum_quantity': 4,
                        'quantum_price': 1.0,
                        'absolute_quantity': 2000,
                    },
                    {
                        'eats_item_id': 'replace-2',
                        'version': 0,
                        'quantity': 2,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantum_quantity': 4,
                        'quantum_price': 1.0,
                        'absolute_quantity': 2000,
                    },
                    {
                        'eats_item_id': '245',
                        'version': 1,
                        'quantity': 2.5,
                        'measure_value': 300,
                        'measure_quantum': 250,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 750,
                    },
                    {
                        'eats_item_id': '542',
                        'version': 1,
                        'quantity': 3,
                        'measure_quantum': 1,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 3,
                    },
                    {
                        'eats_item_id': '1234',
                        'version': 1,
                        'quantity': 1.5,
                        'measure_value': 200,
                        'measure_quantum': 100,
                        'quantum_quantity': 3,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': '4321',
                        'version': 1,
                        'quantity': 1.5,
                        'measure_value': 400,
                        'measure_quantum': 300,
                        'quantum_quantity': 2,
                        'quantum_price': 1.0,
                        'absolute_quantity': 600,
                    },
                    {
                        'eats_item_id': 'add',
                        'version': 1,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'delete-1',
                        'version': 1,
                        'quantity': 5,
                        'measure_quantum': 1,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 5,
                    },
                    {
                        'eats_item_id': 'replacement',
                        'version': 1,
                        'quantity': 5,
                        'measure_value': 100,
                        'measure_quantum': 100,
                        'quantum_quantity': 5,
                        'quantum_price': 1.0,
                        'absolute_quantity': 500,
                        'replacements': [6, 7],
                    },
                ],
                'picked_items': [
                    {
                        'order_item': 2,
                        'weight': 280,
                        'cart_version': 1,
                    },  # 1234
                    {
                        'order_item': 3,
                        'weight': 600,
                        'cart_version': 1,
                    },  # 4321
                    {
                        'order_item': 4,
                        'count': 3,
                        'cart_version': 1,
                    },  # delete-1
                    {'order_item': 8, 'weight': 750, 'cart_version': 2},  # 245
                    {'order_item': 9, 'count': 3, 'cart_version': 2},  # 542
                    {
                        'order_item': 10,
                        'weight': 320,
                        'cart_version': 2,
                    },  # 1234
                    {
                        'order_item': 11,
                        'weight': 560,
                        'cart_version': 2,
                    },  # 4321
                    {'order_item': 12, 'count': 3, 'cart_version': 2},  # add
                    {
                        'order_item': 14,
                        'weight': 400,
                        'cart_version': 2,
                    },  # replacement
                ],
            },
            # residual = 1502.58 - 10 * (3 + 4 + 2.5 + 3 + 1.6 + 1.4) =
            # = 1502.58 - 155 = 1347.58
            # amount is bigger than order_total,
            # so fake_item will be added with residual as amount
            {
                'remove': [
                    {'order_item': 4},  # remove-1
                    {'order_item': 5},  # remove-2
                    {'order_item': 6},  # replace-1
                    {'order_item': 7},  # replace-2
                ],
                'add': [
                    {'picked_item': 7, 'price': '10.00'},  # add
                    {'picked_item': 8, 'price': '10.00'},  # replacement
                    {'quantity': 1, 'price': '1347.58'},
                ],
                'update': [
                    {'order_item': 0, 'price': '10.00'},  # 245
                    {'order_item': 1, 'price': '10.00'},  # 542
                    {
                        'order_item': 2,
                        'quantity': 1.6,
                        'price': '10.00',
                    },  # 1234
                    {
                        'order_item': 3,
                        'quantity': 1.4,
                        'price': '10.00',
                    },  # 4321
                ],
            },
        ),
        (
            {
                'last_version': 1,
                'amount': 129.0,
                'order_items': [
                    {
                        'eats_item_id': '0',
                        'version': 0,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 1,
                        'quantum_quantity': 3,
                        'price': 5.0,
                        'quantum_price': 7.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '1',
                        'version': 0,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 2,
                        'quantum_quantity': 4,
                        'price': 6.0,
                        'quantum_price': 8.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '2',
                        'version': 1,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 3,
                        'quantum_quantity': 5,
                        'price': 7.0,
                        'quantum_price': 9.0,
                        'absolute_quantity': 1500,
                        'replacements': [0],
                    },
                    {
                        'eats_item_id': '3',
                        'version': 1,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 4,
                        'quantum_quantity': 6,
                        'price': 8.0,
                        'quantum_price': 10.0,
                        'absolute_quantity': 1500,
                        'replacements': [1],
                    },
                    {
                        'eats_item_id': '4',
                        'version': 0,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 4,
                        'quantum_quantity': 7,
                        'price': 9.0,
                        'quantum_price': 11.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '5',
                        'version': 0,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 5,
                        'quantum_quantity': 8,
                        'price': 10.0,
                        'quantum_price': 12.0,
                        'absolute_quantity': 1500,
                    },
                    {
                        'eats_item_id': '4',
                        'version': 1,
                        'sold_by_weight': False,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 7,
                        'quantum_quantity': 9,
                        'price': 11.0,
                        'quantum_price': 13.0,
                        'absolute_quantity': 1500,
                        'replacements': [4],
                    },
                    {
                        'eats_item_id': '5',
                        'version': 1,
                        'sold_by_weight': True,
                        'measure_value': 1000,
                        'measure_quantum': 500,
                        'quantity': 8,
                        'quantum_quantity': 10,
                        'price': 12.0,
                        'quantum_price': 14.0,
                        'absolute_quantity': 1500,
                        'replacements': [5],
                    },
                ],
                'picked_items': [
                    {'order_item': 2, 'count': 3, 'cart_version': 1},
                    {'order_item': 3, 'weight': 2000, 'cart_version': 1},
                    {'order_item': 6, 'count': 5, 'cart_version': 1},
                    {'order_item': 7, 'weight': 3000, 'cart_version': 1},
                ],
            },
            # residual = 129 - 3 * 7 - 2 * 8 - 5 * 11 - 3 * 12 = 1
            # amount is bigger than order_total,
            # so fake_item will be added with residual as amount
            {
                'update': [
                    {'order_item': 4, 'quantity': 5.0, 'price': '11.00'},
                    {'order_item': 5, 'quantity': 3.0, 'price': '12.00'},
                ],
                'add': [
                    {'picked_item': 0, 'price': '7.00'},
                    {'picked_item': 1, 'price': '8.00'},
                    {'quantity': 1, 'price': '1.00'},
                ],
                'remove': [{'order_item': 0}, {'order_item': 1}],
            },
        ),
    ]
