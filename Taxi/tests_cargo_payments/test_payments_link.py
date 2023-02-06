import pytest


@pytest.mark.parametrize(
    'item_type,expected_tag', [('product', 1), ('service', 4)],
)
async def test_payment_link_tag(
        run_operations_executor,
        state_performer_found,
        taxi_cargo_payments,
        mock_link_create,
        get_active_operations,
        item_type,
        expected_tag,
):
    state = await state_performer_found(items_count=1, item_type=item_type)

    response = await taxi_cargo_payments.post(
        'v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
        },
    )

    # ??? sync with taximeter api
    response = await taxi_cargo_payments.post(
        'v1/admin/payment/build_link', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 200
    state = await run_operations_executor()

    assert len(mock_link_create.requests) == 1
    assert (
        mock_link_create.requests[0]['BasicTran']['AuxDataInput']['AuxData'][
            'Purchases'
        ][0]
        == {
            'Title': 'title_1',
            'Price': '10',
            'Quantity': 2,
            'TaxCode': ['VAT2000'],
            '1214': 4,
            '1212': expected_tag,
            '1222': 64,
            '1226': '9705114405',
            '1225': 'yandex_virtual_client',
        }
    )

    operations = get_active_operations()
    assert (
        operations[0]['current_link']['url']
        == f'https://2can.ru:443/pay/59228661320002404'
    )


async def test_link_admin(
        run_operations_executor,
        state_payment_confirmed,
        taxi_cargo_payments,
        driver_headers,
        mock_link_create,
):
    state = await state_payment_confirmed(payment_method='link')

    await run_operations_executor()

    # Проверяем, что в админке видна новая операция и ссылка
    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )

    json = response.json()
    assert len(json['active_operations']) == 1
    assert json['active_operations'][0]['meta']['payment_method'] == 'link'
    assert (
        json['active_operations'][0]['meta']['link']
        == 'https://2can.ru:443/pay/59228661320002404'
    )


async def test_link_sms(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        mock_link_create,
        get_active_operations,
        mock_ucommunications,
        mock_clck,
):
    await state_payment_confirmed(payment_method='link')

    await run_operations_executor()
    operations = get_active_operations()
    assert not operations[0]['notified']

    await process_operation(operations[0]['operation_id'])
    operations = get_active_operations()
    assert operations[0]['notified']


async def test_link_taximeter(
        run_operations_executor,
        state_payment_confirmed,
        taxi_cargo_payments,
        driver_headers,
        mock_link_create,
):
    state = await state_payment_confirmed(payment_method='link')

    await run_operations_executor()

    #  Проверяем, что в таксометре видна ссылка
    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )
    assert response.status_code == 200

    assert (
        response.json()['payment']['payment_link']
        == f'https://2can.ru:443/pay/59228661320002404'
    )


async def test_link_payment(
        run_operations_executor,
        process_operation,
        state_performer_found,
        taxi_cargo_payments,
        driver_headers,
        mock_link_create,
        load_json_var,
        get_active_operations,
):
    state = await state_performer_found()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
            'payment_method': 'link',
        },
        headers=driver_headers,
    )
    assert response.status_code == 200

    await run_operations_executor()

    operations = get_active_operations()
    assert (
        operations[0]['current_link']['url']
        == 'https://2can.ru:443/pay/59228661320002404'
    )

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    await run_operations_executor()
    operations = get_active_operations()
    await process_operation(operations[0]['operation_id'])

    assert not get_active_operations()


async def test_link_credentials(
        run_operations_executor,
        state_payment_confirmed,
        taxi_cargo_payments,
        driver_headers,
        mock_link_create,
        state_context,
):
    """
        Check using different fiscalization account for
        different agent clients.
    """
    state_context.use_eats_client()
    mock_link_create.expected_token = b'default@eats:234234234'

    await state_payment_confirmed(payment_method='link')

    await run_operations_executor()

    assert mock_link_create.handler.times_called == 1


async def test_generate_link_happy_path(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        mock_link_create,
        get_active_operations,
        mock_ucommunications,
        mock_clck,
        load_json_var,
        taxi_cargo_payments,
        mocked_time,
        exp_cargo_payments_link_generation,
        state_context,
):
    """
      Test link generation for payment redirect page. After handler is called
      need_link on current active operation is switched, and process_operation
      stq acquires new link from 2can.
    """
    state = await state_payment_confirmed(payment_method='link')
    await exp_cargo_payments_link_generation(
        virtual_client_id=state_context.virtual_client_id, do_redirect=True,
    )

    # First stq run - current_link create
    await run_operations_executor()
    operations = get_active_operations()
    operation_id = operations[0]['operation_id']

    initial_link = operations[0]['current_link']['url']
    assert initial_link
    assert 'prepared_link' not in operations[0]

    # Second stq run - notify
    await process_operation(operation_id)
    assert mock_clck.handler.times_called == 1
    mocked_time.sleep(2)

    # Third stq run - prepared_link create
    await process_operation(operation_id)
    operations = get_active_operations()

    prepared_link = operations[0]['prepared_link']['url']
    assert operations[0]['current_link']['url'] == initial_link
    assert prepared_link

    response = await taxi_cargo_payments.post(
        '/api/b2b/cargo-payments/v1/payment/generate_link',
        params={'payment_id': state.payment_id},
    )
    assert response.json()['link'] == initial_link

    mocked_time.sleep(25)
    response = await taxi_cargo_payments.post(
        '/api/b2b/cargo-payments/v1/payment/generate_link',
        params={'payment_id': state.payment_id},
    )
    assert response.json()['link'] == prepared_link

    # Links are shifted, so currently there is no prepared one
    operations = get_active_operations()
    operation_id = operations[0]['operation_id']
    assert 'prepared_link' not in operations[0]

    # If stq is late, we should keep returning the curent link
    mocked_time.sleep(25)
    response = await taxi_cargo_payments.post(
        '/api/b2b/cargo-payments/v1/payment/generate_link',
        params={'payment_id': state.payment_id},
    )
    assert response.json()['link'] == prepared_link

    # After link shift, another link should be prepared
    await process_operation(operation_id)

    operations = get_active_operations()
    operation_id = operations[0]['operation_id']

    assert operations[0]['current_link']['url'] == prepared_link
    assert operations[0]['prepared_link']['url'] != prepared_link


@pytest.mark.parametrize(
    ('do_redirect', 'link'),
    [(False, 'https://2can.ru:443/pay/59228661320002404'), (True, 'test')],
)
async def test_admin_payment_link(
        run_operations_executor,
        state_payment_confirmed,
        taxi_cargo_payments,
        exp_cargo_payments_link_generation,
        state_context,
        do_redirect,
        link,
):
    state = await state_payment_confirmed(payment_method='link')
    await exp_cargo_payments_link_generation(
        virtual_client_id=state_context.virtual_client_id,
        do_redirect=do_redirect,
        redirect_url=link,
    )

    await run_operations_executor()

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )
    assert response.json()['active_operations'][0]['meta']['link'].startswith(
        link,
    )


async def test_payment_cut_info(taxi_cargo_payments, state_payment_confirmed):

    state = await state_payment_confirmed(payment_method='link')
    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/v1/payment/cut-info',
        params={'payment_id': state.payment_id},
    )
    assert sorted(response.json().keys()) == ['final_sum', 'items']


async def test_link_available_for_expired_operation(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        mock_link_create,
        get_active_operations,
        taxi_cargo_payments,
        mocked_time,
        exp_cargo_payments_link_generation,
        state_context,
):
    """
      Payment operation currently expires earlier than payment link,
      but link must be still available for customer.
    """
    state = await state_payment_confirmed(payment_method='link')
    await exp_cargo_payments_link_generation(
        virtual_client_id=state_context.virtual_client_id, do_redirect=True,
    )

    # First stq run - current_link create
    await run_operations_executor()
    operations = get_active_operations()

    operation_id = operations[0]['operation_id']
    initial_link = operations[0]['current_link']['url']
    assert initial_link

    mocked_time.sleep(5000)
    # Second stq run - drop active operation
    await process_operation(operation_id)
    assert not get_active_operations()

    response = await taxi_cargo_payments.post(
        '/api/b2b/cargo-payments/v1/payment/generate_link',
        params={'payment_id': state.payment_id},
    )
    assert response.json()['link'] == initial_link
