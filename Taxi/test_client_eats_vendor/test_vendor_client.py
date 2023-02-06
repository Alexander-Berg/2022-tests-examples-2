from client_eats_vendor.vendor_client.objects import order_response


async def test_get_tokens(library_context, mockserver, load_json):
    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/login')
    def login():  # pylint: disable=W0612
        return mockserver.make_response(json=load_json('token_response.json'))

    tokens = await library_context.client_eats_vendor.get_tokens()
    assert tokens == ['8a5c159de11b43398adf9d79dcf290f0']


async def test_get_active_orders(library_context, mockserver, load_json):
    @mockserver.json_handler('/4.0/restapp-front/api/v1/client/orders/active')
    def active_orders():  # pylint: disable=W0612
        return mockserver.make_response(
            json=load_json('active_orders_response.json'),
        )

    orders = await library_context.client_eats_vendor.get_active_orders(
        token='some_token',
    )
    assert orders.is_success is True
    assert [order.external_id for order in orders.payload] == [
        '211130-490997',
        '211202-366028',
        '211203-414778',
        '211206-441818',
        '211206-437720',
        '211208-245947',
        '211223-266056',
        '220117-070013',
        '220119-332330',
        '220125-073561',
        '220127-192144',
        '220209-331579',
        '220215-316237',
        '220218-152917',
        '220303-130028',
    ]


async def test_accept_order(library_context, mockserver):
    @mockserver.json_handler(
        '/4.0/restapp-front/api/v1/client/orders'
        '/b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e/accept',
    )
    def accept_order():
        return mockserver.make_response()

    await library_context.client_eats_vendor.accept_order(
        token='some_token',
        order=order_response.Order(
            order_id='b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e',
            external_id='211130-490997',
            comment='some_comment',
            status='new',
        ),
    )
    assert accept_order.times_called == 1


async def test_cancel_order(library_context, mockserver):
    @mockserver.json_handler(
        '/4.0/restapp-front/api/v1/client/orders/211130-490997/cancel',
    )
    def cancel_order():
        return mockserver.make_response()

    await library_context.client_eats_vendor.cancel_order(
        token='some_token',
        order=order_response.Order(
            order_id='b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e',
            external_id='211130-490997',
            comment='some_comment',
            status='new',
        ),
    )
    assert cancel_order.times_called == 1


async def test_deliver_order(library_context, mockserver):
    @mockserver.json_handler(
        '/4.0/restapp-front/api/v1/client'
        '/orders/b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e/deliver',
    )
    def deliver_order():
        return mockserver.make_response()

    await library_context.client_eats_vendor.deliver_order(
        token='some_token',
        order=order_response.Order(
            order_id='b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e',
            external_id='211130-490997',
            comment='some_comment',
            status='new',
        ),
    )
    assert deliver_order.times_called == 1


async def test_release_order(library_context, mockserver):
    @mockserver.json_handler(
        '/4.0/restapp-front/api/v1/client'
        '/orders/b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e/release',
    )
    def release_order():
        return mockserver.make_response()

    await library_context.client_eats_vendor.release_order(
        token='some_token',
        order=order_response.Order(
            order_id='b9c0a1a4-675a-4aaa-80b6-2c984bb5d29e',
            external_id='211130-490997',
            comment='some_comment',
            status='new',
        ),
    )
    assert release_order.times_called == 1
