import pytest


@pytest.fixture(name='build_partial_refund_request')
async def _build_partial_refund_request(build_update_request):
    def wrapper(
            *,
            payment_id,
            snapshot_token='token1',
            accepted_counts,
            items_count=None,
    ):
        if items_count is None:
            items_count = len(accepted_counts)
        else:
            assert items_count >= len(accepted_counts)
        request = build_update_request(
            payment_id=payment_id,
            snapshot_token=snapshot_token,
            item_count=2,
            items_count=items_count,
        )
        for i, accepted_count in enumerate(accepted_counts):
            request['items'][i]['count'] = accepted_count
        return request

    return wrapper


async def test_card_payment(
        run_operations_executor,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
):
    # Проверяем, что на ожидание оплаты картой создается
    # соответствующая операция
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )

    json = response.json()
    assert len(json['active_operations']) == 1
    assert json['active_operations'][0]['meta']['payment_method'] == 'card'
    operations = get_active_operations()
    assert operations[0]['payment_method'] == 'card'

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    await run_operations_executor()

    operations = get_active_operations()
    assert not operations


async def test_refund_payment(
        run_operations_executor,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
        process_operation,
):
    # Проверяем, что на возврат оплаты создается
    # соответствующая операция
    state = await state_payment_confirmed()

    operations = get_active_operations()
    assert len(operations) == 1

    response = await taxi_cargo_payments.post(
        'v1/payment/refund', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 404

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    response = await taxi_cargo_payments.post(
        'v1/payment/refund', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 200

    operations = get_active_operations()
    assert len(operations) == 2

    await run_operations_executor()

    operations = get_active_operations()
    assert len(operations) == 1
    assert operations[0]['refund_id'] != ''

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'refund_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    assert response.status_code == 200

    await process_operation(operations[0]['operation_id'])
    operations = get_active_operations()
    assert not operations

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )
    assert len(response.json()['transactions']) == 2


async def test_expired_refund_payment(
        state_payment_authorized, taxi_cargo_payments, mocked_time,
):
    """
    Check that expired return is not created
    """
    state = await state_payment_authorized()

    mocked_time.sleep(3600 * 24 * 60)  # 60 days
    response = await taxi_cargo_payments.post(
        'v1/payment/refund', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 404


async def test_duplicated_refund(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
        mock_transactions_history,
):
    # Проверяем, что подбирается транзакция refund-а из репорта
    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_operations_executor()

    operations = get_active_operations()
    assert not operations

    response = await taxi_cargo_payments.post(
        'v1/payment/refund', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 200

    operations = get_active_operations()
    assert len(operations) == 1

    mock_transactions_history.transaction_id = '123456'
    mock_transactions_history.description = (
        'Operation:%d' % operations[0]['operation_id']
    )

    await process_operation(operations[0]['operation_id'])

    operations = get_active_operations()
    assert len(operations) == 1
    assert operations[0]['refund_id'] == '123456'


async def test_auto_refund_payment(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
        cancel_payment,
):
    # Проверяем, что на возврат оплаты создается
    # соответствующая операция
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_operations_executor()
    operations = get_active_operations()
    assert not operations

    await cancel_payment(payment_id=state.payment_id)

    operations = get_active_operations()
    assert len(operations) == 1

    await process_operation(operations[0]['operation_id'])

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'refund_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    assert response.status_code == 200

    await process_operation(operations[0]['operation_id'])
    operations = get_active_operations()
    assert not operations

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )
    assert len(response.json()['transactions']) == 2


async def test_auto_refund_not_canceled(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
        run_transactions_scanner,
):
    # Проверяем, что на на дублирующиеся транзакции создается возврат
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_operations_executor()
    operations = get_active_operations()
    assert not operations

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event_duplicated.json',
            payment_id=state.payment_id,
            amount='40',
        ),
    )

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )
    assert len(response.json()['transactions']) == 2

    operations = get_active_operations()
    assert not operations

    await run_transactions_scanner()

    operations = get_active_operations()
    assert len(operations) == 1

    assert (
        operations[0]['transaction_id']
        == 'E54906D4-92A1-43A5-8016-D50F0EEEFB35'
    )

    await process_operation(operations[0]['operation_id'])

    refund = load_json_var(
        'refund_event.json', payment_id=state.payment_id, amount='40',
    )
    refund['PaymentID'] = 'E54906D4-92A1-43A5-8016-D50F0EEEFB35'

    response = await taxi_cargo_payments.post('2can/status', json=refund)

    assert response.status_code == 200

    await process_operation(operations[0]['operation_id'])
    operations = get_active_operations()
    assert not operations

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )
    assert len(response.json()['transactions']) == 3


async def test_refund_credentials(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
        state_context,
        mock_reversecnp,
        mock_web_api_agent_create,
        cancel_payment,
):
    """
        Check for agent authorization data for
        different agent's client.
    """
    state_context.use_eats_client()

    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_operations_executor()
    operations = get_active_operations()
    assert not operations

    await cancel_payment(payment_id=state.payment_id)

    operations = get_active_operations()
    assert len(operations) == 1

    mock_reversecnp.expected_token = b'default@eats:234234234'
    await process_operation(operations[0]['operation_id'])
    assert mock_reversecnp.handler.times_called == 1


@pytest.mark.parametrize('accepted_counts', [[1, 0], [1, 2]])
async def test_partial_refund_authorized(
        state_payment_finished,
        taxi_cargo_payments,
        load_json_var,
        build_partial_refund_request,
        run_operations_executor,
        process_operation,
        get_active_operations,
        accepted_counts,
):
    state = await state_payment_finished(item_count=2)

    response = await taxi_cargo_payments.post(
        'v1/payment/update',
        json=build_partial_refund_request(
            payment_id=state.payment_id, accepted_counts=accepted_counts,
        ),
    )
    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )

    for i, accepted_count in enumerate(accepted_counts):
        _check_returned_count(
            items=response.json()['items'],
            article=f'article_{i+1}',
            returned_count=2 - accepted_count,
        )

    await run_operations_executor()
    operations = get_active_operations()
    assert len(operations) == 1
    assert operations[0]['refund_id'] != ''
    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'refund_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200
    await process_operation(operations[0]['operation_id'])
    operations = get_active_operations()
    assert not operations
    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )
    assert len(response.json()['transactions']) == 2


async def test_partial_refund_zero_diff(
        state_performer_found,
        taxi_cargo_payments,
        load_json_var,
        update_items,
        get_active_operations,
        get_payment,
):
    state = await state_performer_found()

    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token1',
        item_count=2,
        items_count=1,
    )

    response = await taxi_cargo_payments.post(
        'v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision + 1,
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='20',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'fiscal_event.json', payment_id=state.payment_id, amount='20',
        ),
    )
    assert response.status_code == 200

    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token2',
        item_count=2,
        items_count=1,
    )

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )

    operations = get_active_operations()
    assert not operations

    assert response.json()['items'] == [
        {
            'article': 'article_1',
            'count': 2,
            'currency': 'RUB',
            'supplier_inn': '9705114405',
            'nds': 'nds_20',
            'price': '10',
            'returned': 0,
            'title': 'title_1',
            'type': 'product',
        },
    ]


async def test_double_refund_zero_diff(
        state_payment_finished,
        taxi_cargo_payments,
        load_json_var,
        update_items,
        run_operations_executor,
        process_operation,
        get_active_operations,
):
    state = await state_payment_finished()

    response = await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token2',
        item_count=1,
    )
    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        'v1/admin/payment/info', params={'payment_id': state.payment_id},
    )

    operations = get_active_operations()
    assert len(operations) == 1

    assert len(response.json()['items']) == 2

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'refund_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200
    await run_operations_executor()
    await process_operation(operations[0]['operation_id'])
    operations = get_active_operations()
    assert not operations

    response = await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token2',
        item_count=1,
    )

    assert response.status_code == 200
    operations = get_active_operations()
    assert not operations


async def test_link_credentials(
        run_operations_executor,
        process_operation,
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        get_active_operations,
        state_context,
        mock_reversecnp,
        mock_web_api_agent_create,
        cancel_payment,
):
    """
        Check for agent authorization data for
        different agent's client.
    """
    state_context.use_eats_client()

    state = await state_payment_confirmed()

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )

    await run_operations_executor()
    operations = get_active_operations()
    assert not operations
    await cancel_payment(payment_id=state.payment_id)

    operations = get_active_operations()
    assert len(operations) == 1

    mock_reversecnp.expected_token = b'default@eats:234234234'
    await process_operation(operations[0]['operation_id'])
    assert mock_reversecnp.handler.times_called == 1


async def test_second_refund(
        state_payment_finished, get_payment, update_items, item_count=2,
):
    # payment created with 3 items
    state = await state_payment_finished(items_count=3)

    # update with 2 items, so need refund for 1 item
    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token1',
        item_count=item_count,
        items_count=2,
    )

    payment = await get_payment(state.payment_id)
    _check_returned_count(
        payment['items'], 'article_3', returned_count=item_count,
    )

    # update with 1 item, so need refund for 1 another item
    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token2',
        items_count=1,
        item_count=item_count,
    )

    payment = await get_payment(state.payment_id)
    _check_returned_count(
        payment['items'], 'article_2', returned_count=item_count,
    )


async def test_second_partial_refund(
        state_payment_finished,
        get_payment,
        update_items,
        get_active_operations,
        delete_operations,
        run_operations_executor,
):
    # payment created with 3 items
    state = await state_payment_finished(item_count=3)

    # update with 2 items, so need refund for 1 item
    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token1',
        item_count=2,
    )

    payment = await get_payment(state.payment_id)
    _check_returned_count(payment['items'], 'article_1', returned_count=1)
    operations = get_active_operations()
    assert len(operations) == 1
    for diff in operations[0]['items']:
        assert diff['count'] == 1
    delete_operations()

    # update with 1 item, so need refund for 1 another item
    await update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token2',
        item_count=1,
    )

    payment = await get_payment(state.payment_id)
    _check_returned_count(payment['items'], 'article_1', returned_count=2)
    operations = get_active_operations()
    assert len(operations) == 1
    for diff in operations[0]['items']:
        assert diff['count'] == 1


def _find_item(items, article):
    for item in items:
        if item['article'] == article:
            return item
    return None


def _check_returned_count(items, article, returned_count):
    item = _find_item(items, article)
    assert item

    assert item['returned'] == returned_count
