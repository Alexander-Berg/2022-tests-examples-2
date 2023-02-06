import pytest

from tests_cargo_fiscal import const


async def generate_response(
        taxi_cargo_fiscal,
        service,
        additional_context,
        topic_id,
        transaction_id,
        is_refund=False,
):
    data = {
        **{
            'transaction_id': transaction_id,
            'is_refund': is_refund,
            'payment_method': 'card',
            'price_details': {
                'without_vat': '12.5',
                'vat': '.5',
                'total': '13.0',
            },
        },
        **additional_context,
    }
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts'
        f'/{service}/orders/generate-transaction?topic_id={topic_id}'
        f'&transaction_id={transaction_id}',
        json=data,
    )
    return response


@pytest.mark.parametrize(
    'service, country, expected_code, additional_context',
    (
        pytest.param(
            'delivery', 'RUS', 200, {}, id='rus_transaction_context_ok',
        ),
        pytest.param(
            'delivery', 'KAZ', 200, {}, id='kaz_transaction_context_ok',
        ),
        pytest.param(
            'delivery',
            'ISR',
            200,
            {
                'isr_data': {
                    'developer_email': 'v@c.ru',
                    'park_clid': '12345',
                    'customer_name': 'name',
                    'payment_type': 3,
                    'cc_type': 1,
                    'cc_type_name': 'visa',
                    'cc_number': '12345',
                    'cc_deal_type': 1,
                    'cc_num_of_payments': 1,
                    'cc_payment_num': 1,
                    'item_amount': 1,
                },
            },
            id='isr_transaction_context_ok',
        ),
    ),
)
async def test_generate(
        taxi_cargo_fiscal,
        mock_py2_fiscal_data,
        set_default_transactions_ng_response,
        stq,
        service,
        country,
        expected_code,
        additional_context,
):
    context = {
        'provider_inn': '123456789',
        'service_rendered_at': '2021-03-26T12:00:00+03:00',
        'title': 'Услуга доставки',
        'country': country,
    }
    additional_context = {**additional_context, **context}
    response = await generate_response(
        taxi_cargo_fiscal,
        service,
        additional_context,
        const.TOPIC_ID + country,
        const.TRANSACTION_ID + country,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        if country == 'RUS':
            times_called = (
                stq.cargo_fiscal_generate_transactions_ng.times_called
            )
        elif country == 'KAZ':
            times_called = stq.cargo_fiscal_generate_kaz_buhta.times_called
        elif country == 'ISR':
            times_called = stq.cargo_fiscal_generate_isr_ez.times_called
        assert times_called == 1


@pytest.mark.parametrize(
    'service, country', (('delivery', 'RUS'), ('delivery', 'KAZ')),
)
async def test_generate_already_success(
        taxi_cargo_fiscal,
        mock_py2_fiscal_data,
        set_default_transactions_ng_response,
        stq,
        pgsql,
        service,
        country,
):
    context = {
        'provider_inn': '123456789',
        'service_rendered_at': '2021-03-26T12:00:00+03:00',
        'title': 'Услуга доставки',
        'country': country,
    }
    response = await generate_response(
        taxi_cargo_fiscal,
        service,
        context,
        'topic_id_already_success' + country,
        'transaction_id_already_success' + country,
    )

    assert response.status_code == 200
    if country == 'RUS':
        times_called = stq.cargo_fiscal_generate_transactions_ng.times_called
    elif country == 'KAZ':
        times_called = stq.cargo_fiscal_generate_kaz_buhta.times_called
    assert times_called == 1

    cursor = pgsql['cargo_fiscal'].conn.cursor()
    cursor.execute(
        f"""UPDATE cargo_fiscal.transaction set url = 'some_url_received'
        where transaction_id =
        '{"transaction_id_already_success" + country}'""",
    )

    response = await generate_response(
        taxi_cargo_fiscal,
        service,
        context,
        'topic_id_already_success' + country,
        'transaction_id_already_success' + country,
    )
    assert response.status_code == 200
    if country == 'RUS':
        times_called = stq.cargo_fiscal_generate_transactions_ng.times_called
    elif country == 'KAZ':
        times_called = stq.cargo_fiscal_generate_kaz_buhta.times_called
    assert times_called == 1


async def test_generate_different_transaction_context(
        taxi_cargo_fiscal,
        mock_py2_fiscal_data,
        set_default_transactions_ng_response,
        stq,
):
    context = {
        'provider_inn': '123456789',
        'service_rendered_at': '2021-03-26T12:00:00+03:00',
        'title': 'Услуга доставки',
        'country': 'KAZ',
    }
    response = await generate_response(
        taxi_cargo_fiscal, 'delivery', context, 'topic_id1', 'transaction_id2',
    )
    assert response.status_code == 200

    # change transaction context
    response = await generate_response(
        taxi_cargo_fiscal,
        'delivery',
        context,
        'topic_id1',
        'transaction_id2',
        is_refund=True,
    )
    assert response.status_code == 400
    times_called = stq.cargo_fiscal_generate_kaz_buhta.times_called
    assert times_called == 1
    assert response.json() == {
        'code': 'transaction_validation_error',
        'details': {},
        'message': (
            'transactions context is different' ' from previously supplied'
        ),
    }


@pytest.mark.parametrize(
    'generate_tansaction_response_code,has_topic_context',
    (
        pytest.param(200, True, id='ok_with_topic_context'),
        pytest.param(400, False, id='bad_without_topic_context'),
        pytest.param(400, True, id='bad_generate_transacton_response'),
    ),
)
async def test_generate_pass(
        taxi_cargo_fiscal,
        mockserver,
        generate_tansaction_response_code,
        has_topic_context,
):
    data = const.REQUEST.copy()
    if has_topic_context:
        data['context'] = const.TOPIC_CONTEXT
    else:
        data['transactions'][0] = {
            **data['transactions'][0],
            **const.TOPIC_CONTEXT,
        }
    data['transactions'].append(data['transactions'][0])

    @mockserver.json_handler(
        '/cargo-fiscal/internal/cargo-fiscal/'
        'receipts/delivery/orders/generate-transaction',
    )
    def _mock_generate_transaction(request):
        if generate_tansaction_response_code == 200:
            assert request.query == {
                'topic_id': 'topic_id',
                'transaction_id': 'transaction_id',
            }
            assert request.json == {
                **data['transactions'][0],
                **data['context'],
            }
            return mockserver.make_response(
                status=generate_tansaction_response_code, json={},
            )
        return mockserver.make_response(
            status=generate_tansaction_response_code,
            json={
                'code': 'error_code',
                'message': 'error_message',
                'details': {},
            },
        )

    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts'
        f'/delivery/orders/generate?topic_id=topic_id',
        json=data,
    )
    if generate_tansaction_response_code == 200:
        assert _mock_generate_transaction.times_called == 2
        assert response.status_code == 200
    if generate_tansaction_response_code == 400:
        if has_topic_context:
            # generate returns 20 even if generate-transaction
            # returns 400 for some transactions
            assert response.status_code == 200
            assert response.json() == {}
        else:
            assert response.status_code == 400
            assert response.json() == {
                'code': '400',
                'message': (
                    'Parse error at pos 879, path \'\': '
                    'missing required field \'context\''
                ),
            }
