import pytest


@pytest.mark.parametrize(
    'orders, expected_status',
    [
        [[{'eats_id': '123', 'status': 'picking'}], 400],
        [
            [
                {'eats_id': '123', 'status': 'complete'},
                {'eats_id': '12345', 'status': 'picking'},
            ],
            400,
        ],
        [
            [
                {'eats_id': '123', 'status': 'complete'},
                {'eats_id': '12345', 'status': 'cancelled'},
            ],
            409,
        ],
        [[{'eats_id': '123', 'status': 'complete'}], 200],
        [
            [
                {'eats_id': '123', 'status': 'complete'},
                {'eats_id': '1234', 'status': 'complete'},
            ],
            200,
        ],
        [
            [
                {'eats_id': '123', 'status': 'complete'},
                {'eats_id': '123456', 'status': 'cancelled'},
            ],
            200,
        ],
        [[{'eats_id': '123', 'status': 'complete'}] * 5000, 400],
    ],
)
async def test_post_orders_status_response_status(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        mock_processing,
        orders,
        expected_status,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    create_order(eats_id='123', state='picking')
    create_order(eats_id='1234', state='picking')
    create_order(eats_id='12345', state='complete')

    response = await taxi_eats_picker_orders.post(
        '/admin/v1/orders/status', json={'orders': orders},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'orders',
    [
        [{'eats_id': '123', 'status': 'complete'}],
        [
            {'eats_id': '12345', 'status': 'complete'},
            {'eats_id': '1234', 'status': 'complete'},
        ],
        [
            {'eats_id': '123', 'status': 'cancelled'},
            {'eats_id': '123456', 'status': 'cancelled'},
        ],
        [
            {'eats_id': '1234', 'status': 'cancelled'},
            {'eats_id': '123456', 'status': 'cancelled'},
        ],
    ],
)
async def test_post_orders_status_db_update(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        mock_processing,
        get_order_by_eats_id,
        orders,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    create_order(eats_id='123', state='picking')
    create_order(eats_id='1234', state='picking')
    create_order(eats_id='12345', state='complete')

    response = await taxi_eats_picker_orders.post(
        '/admin/v1/orders/status', json={'orders': orders},
    )
    assert response.status == 200

    result = get_order_by_eats_id(orders[0]['eats_id'])
    assert result['state'] == orders[0]['status']


@pytest.mark.parametrize(
    'orders',
    [
        [{'eats_id': '123', 'status': 'complete', 'comment': 'some text'}],
        [
            {'eats_id': '123', 'status': 'complete', 'comment': 'some text'},
            {
                'eats_id': '1234',
                'status': 'complete',
                'comment': 'some other text',
            },
        ],
    ],
)
async def test_post_orders_status_comments_update(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        mock_processing,
        get_last_order_status,
        orders,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    create_order(eats_id='123', state='picking')
    create_order(eats_id='1234', state='picking')
    create_order(eats_id='12345', state='complete')

    response = await taxi_eats_picker_orders.post(
        '/admin/v1/orders/status', json={'orders': orders},
    )
    assert response.status == 200

    for index, order in enumerate(orders):
        result = get_last_order_status(index + 1)
        assert result['comment'] == order['comment']


@pytest.mark.parametrize(
    'orders, expected_response',
    [
        [
            [{'eats_id': '123', 'status': 'complete'}],
            {'not_found_orders': [], 'same_status_orders': []},
        ],
        [
            [
                {'eats_id': '12345', 'status': 'complete'},
                {'eats_id': '1234', 'status': 'complete'},
            ],
            {'not_found_orders': [], 'same_status_orders': ['12345']},
        ],
        [
            [
                {'eats_id': '123', 'status': 'cancelled'},
                {'eats_id': '123456', 'status': 'cancelled'},
            ],
            {'not_found_orders': ['123456'], 'same_status_orders': []},
        ],
        [
            [
                {'eats_id': '1234', 'status': 'cancelled'},
                {'eats_id': '123456', 'status': 'cancelled'},
                {'eats_id': '12345', 'status': 'complete'},
            ],
            {'not_found_orders': ['123456'], 'same_status_orders': ['12345']},
        ],
    ],
)
async def test_post_orders_status_response(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        mock_processing,
        get_order_by_eats_id,
        orders,
        expected_response,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    create_order(eats_id='123', state='picking')
    create_order(eats_id='1234', state='picking')
    create_order(eats_id='12345', state='complete')

    response = await taxi_eats_picker_orders.post(
        '/admin/v1/orders/status', json={'orders': orders},
    )
    assert response.status == 200

    response_data = response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    'headers, expected_author_id',
    [
        [{'X-Yandex-Uid': '12345'}, '12345'],
        [{'X-Yandex-Login': 'abcde'}, 'abcde'],
        [{'X-Yandex-Uid': '12345', 'X-Yandex-Login': 'abcde'}, '12345:abcde'],
        [{}, None],
    ],
)
async def test_post_orders_status_headers(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        mock_processing,
        get_last_order_status,
        headers,
        expected_author_id,
):
    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        return mockserver.make_response(json={'isSuccess': True}, status=200)

    order_id = create_order(eats_id='123', state='picking')
    create_order(eats_id='1234', state='picking')
    create_order(eats_id='12345', state='complete')

    response = await taxi_eats_picker_orders.post(
        '/admin/v1/orders/status',
        headers=headers,
        json={'orders': [{'eats_id': '123', 'status': 'complete'}]},
    )
    assert response.status == 200
    result = get_last_order_status(order_id)
    assert result['author_type'] == 'admin'
    assert result['author_id'] == expected_author_id
