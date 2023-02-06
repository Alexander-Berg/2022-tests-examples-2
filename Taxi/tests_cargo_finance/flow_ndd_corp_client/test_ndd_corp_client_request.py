import pytest


UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/'
    'upsert?flow=claims&entity_id=test_id'
)


@pytest.mark.parametrize(
    [
        'upsert_request',
        'expected_billing_orders_request_name',
        'only_one',
        'expected_orders_count',
    ],
    [
        pytest.param(
            'upsert_request_b2b_logistic_payment.json',
            'expected_billing_orders_request_b2b_logistic_payment.json',
            True,
            1,
            id='delivery_client_b2b_logistics_payment',
        ),
        pytest.param(
            'upsert_request_b2b_user_on_delivery_fee.json',
            'expected_billing_orders_request_b2b_user_on_delivery_fee.json',
            True,
            1,
            id='b2b_user_on_delivery_payment_fee',
        ),
        pytest.param(
            'upsert_request_user_on_delivery_payment.json',
            'expected_billing_orders_request_user_on_delivery_payment.json',
            True,
            1,
            id='user_on_delivery_payment',
        ),
        pytest.param(
            'upsert_request_all_three.json', '{}', False, 3, id='all_three',
        ),
    ],
)
@pytest.mark.config(
    CARGO_FINANCE_BILLING_ORDERS_REVISE_JOB_SETTINGS={
        'allow_cargo_finance_testsuite_only_sending': True,
    },
)
async def test_ndd_corp_client_request(
        taxi_cargo_finance,
        load_json,
        mockserver,
        upsert_request,
        expected_billing_orders_request_name,
        only_one,
        expected_orders_count,
):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _handler(request):
        if only_one:
            assert request.json == load_json(
                expected_billing_orders_request_name,
            )
        return mockserver.make_response(
            status=200,
            json={
                'orders': [{'topic': '1', 'external_ref': '2', 'doc_id': 3}],
            },
        )

    response = await taxi_cargo_finance.post(
        UPSERT_URI, json=load_json(upsert_request),
    )
    assert response.status == 200
    assert _handler.times_called == expected_orders_count
