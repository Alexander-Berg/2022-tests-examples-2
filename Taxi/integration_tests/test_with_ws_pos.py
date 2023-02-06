from test_eats_integration_offline_orders import utils


base_database = utils.BaseDatabase(  # pylint:disable=invalid-name
    restaurants='restaurants.sql',
    tables='tables.sql',
    pos_ws_tokens='pos_ws_tokens.sql',
    orders='orders.sql',
    restaurants_options='restaurants_options.sql',
)


@base_database()
async def test_ws_pos_get_check(
        web_app_client, pos_ws_connection, table_uuid, load_json,
):
    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    assert data == load_json('api_response_data.json')


@base_database()
async def test_ws_pos_pay(
        web_app_client,
        web_context,
        pos_ws_connection,
        payture_mocks,
        billing_mocks,
        table_uuid,
        order_uuid,
        load_json,
):
    response = await web_app_client.get(
        f'/v1/pay?uuid={table_uuid}&order_uuid={order_uuid}',
    )
    assert response.status == 200
    data = await response.json()
    assert data['redirect_link'] == (
        f'{web_context.payture_client.pay_url}'
        f'?SessionId=a333582e-ec0b-43ba-a7b9-717c753b38d1'
    )

    transaction = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM payment_transactions LIMIT 1;',
    )
    assert transaction

    response = await web_app_client.post(
        f'/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=(
            f'Notification=MerchantPay&OrderId={transaction["uuid"]}&'
            f'Success=True'
        ),
    )

    assert response.status == 200


@base_database()
async def test_ws_pos_partial_pay(
        web_app_client,
        web_context,
        pos_ws_connection,
        payture_mocks,
        billing_mocks,
        table_uuid,
        order_uuid,
        load_json,
        stq,
):
    # pay first order part
    response = await web_app_client.post(
        '/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 1},
                {'item_id': 'product_id__2', 'quantity': 1},
            ],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data['redirect_link'] == (
        f'{web_context.payture_client.pay_url}'
        f'?SessionId=a333582e-ec0b-43ba-a7b9-717c753b38d1'
    )

    first_transaction = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM payment_transactions LIMIT 1;',
    )
    assert first_transaction

    response = await web_app_client.post(
        f'/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=(
            f'Notification=MerchantPay&OrderId={first_transaction["uuid"]}&'
            f'Success=True'
        ),
    )
    assert response.status == 200

    # order not paid fully, dont call the pos
    assert not stq.ei_offline_orders_pos_pay_order.has_calls

    # pay last order part
    response = await web_app_client.post(
        '/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [{'item_id': 'product_id__1', 'quantity': 1}],
        },
    )
    assert response.status == 200

    last_transaction = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM payment_transactions ORDER BY created_at DESC LIMIT 1;',
    )
    assert last_transaction

    response = await web_app_client.post(
        f'/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=(
            f'Notification=MerchantPay&OrderId={last_transaction["uuid"]}&'
            f'Success=True'
        ),
    )

    assert response.status == 200

    # order paid fully, call the pos
    assert stq.ei_offline_orders_pos_pay_order.has_calls
