import pytest


async def test_send_initiate_payment(
        mock_procaas_create,
        mock_cargo_finance_dummy_init,
        procaas_extract_token,
        notify_payment_initiated,
):
    ndd_order_id = '123'
    await notify_payment_initiated(ndd_order_id)

    expected_token = 'payment_initiated/{}'.format(ndd_order_id)

    assert mock_procaas_create.times_called == 1
    assert mock_cargo_finance_dummy_init.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_ndd_c2c/')
    assert request.query == {'item_id': ndd_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'payment_initiated', 'data': {}}


async def test_send_finish_payment(
        mock_procaas_create, procaas_extract_token, notify_payment_finished,
):
    ndd_order_id = '123'
    await notify_payment_finished(ndd_order_id)

    expected_token = 'payment_finished/{}'.format(ndd_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_ndd_c2c/')
    assert request.query == {'item_id': ndd_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'payment_finished', 'data': {}}


async def test_price_recalculated_event(
        mock_procaas_create,
        procaas_extract_token,
        assert_correct_scope_queue,
        notify_price_recalculated,
):
    ndd_order_id = '123'
    data = {'price': '300.0000', 'idempotency_token': '678'}
    expected_token = 'price_recalculated/{}'.format(data['idempotency_token'])

    await notify_price_recalculated(ndd_order_id, data)

    data['price'] = '300'  # because was converted to money

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert_correct_scope_queue(request)
    assert request.query == {'item_id': ndd_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'price_recalculated', 'data': data}


async def test_send_billing_context(
        mock_procaas_create,
        procaas_extract_token,
        send_billing_context,
        get_event,
):
    ndd_order_id = '123'
    context = get_event('billing_context')['payload']['data']
    await send_billing_context(ndd_order_id, context)

    expected_token = 'billing_context/{}'.format(ndd_order_id)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.path.count('/cargo/finance_flow_ndd_c2c/')
    assert request.query == {'item_id': ndd_order_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'billing_context', 'data': context}


@pytest.fixture(name='notify_payment_initiated')
def _notify_payment_initiated(notify_func_factory):
    url = '/internal/cargo-finance/flow/ndd-c2c/events/initiate-payment'  # noqa: E501
    return notify_func_factory(url)


@pytest.fixture(name='notify_price_recalculated')
def _notify_price_recalculated(notify_func_factory):
    url = '/internal/cargo-finance/flow/ndd-c2c/events/price-recalculated'  # noqa: E501
    return notify_func_factory(url)


@pytest.fixture(name='notify_payment_finished')
def _notify_payment_finished(notify_func_factory):
    url = '/internal/cargo-finance/flow/ndd-c2c/events/finish-payment'  # noqa: E501
    return notify_func_factory(url)


@pytest.fixture(name='send_billing_context')
def _send_billing_context(notify_func_factory):
    url = '/internal/cargo-finance/flow/ndd-c2c/events/billing-context'  # noqa: E501
    return notify_func_factory(url)


@pytest.fixture(name='notify_func_factory')
def _notify_func_factory(taxi_cargo_finance):
    def wrapper(url):
        async def func(ndd_order_id, data=None, expected_code=200):
            response = await taxi_cargo_finance.post(
                url, params={'ndd_order_id': ndd_order_id}, json=data,
            )
            assert response.status_code == expected_code
            return response

        return func

    return wrapper
