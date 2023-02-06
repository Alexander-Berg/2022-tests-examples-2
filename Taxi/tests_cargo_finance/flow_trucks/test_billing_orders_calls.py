import pytest

MOCK_NOW = '2022-07-03T19:16:00.925246+00:00'
UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/'
    'upsert?flow=trucks&entity_id=test_id'
)
BILLING_ORDERS_REQUEST_WITH_PAYMENTS_TLOG_ONLY = (
    'flow_trucks/expected_billing_orders_request_with_payments_tlog_only.json'
)
BILLING_ORDERS_REQUEST_WITH_REVENUES_TLOG_ONLY = (
    'flow_trucks/expected_billing_orders_request_with_revenues_tlog_only.json'
)


def _build_sorted_list_of_billing_orders_requests(*args):
    return sorted(args, key=lambda request: request['orders'][0]['topic'])


@pytest.mark.parametrize(
    'sum2pay_filename, expected_response_filename',
    [
        (
            'flow_trucks/sum2pay_with_payments_tlog_only.json',
            BILLING_ORDERS_REQUEST_WITH_PAYMENTS_TLOG_ONLY,
        ),
        (
            'flow_trucks/sum2pay_with_revenues_tlog_only.json',
            BILLING_ORDERS_REQUEST_WITH_REVENUES_TLOG_ONLY,
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_base_with_single_tlog_type(
        taxi_cargo_finance,
        load_json,
        mock_v2_process_async,
        sum2pay_filename,
        expected_response_filename,
):
    request = load_json(sum2pay_filename)
    expected_response = load_json(expected_response_filename)

    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert mock_v2_process_async.times_called == 1
    assert (
        mock_v2_process_async.next_call()['request'].json == expected_response
    )


@pytest.mark.now(MOCK_NOW)
async def test_base_with_both_tlog_types(
        taxi_cargo_finance, load_json, mock_v2_process_async,
):
    request = load_json('flow_trucks/sum2pay_with_both_tlog_types.json')
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert mock_v2_process_async.times_called == 2

    requests_in_billing = _build_sorted_list_of_billing_orders_requests(
        mock_v2_process_async.next_call()['request'].json,
        mock_v2_process_async.next_call()['request'].json,
    )
    expected_requests = _build_sorted_list_of_billing_orders_requests(
        load_json(BILLING_ORDERS_REQUEST_WITH_REVENUES_TLOG_ONLY),
        load_json(BILLING_ORDERS_REQUEST_WITH_PAYMENTS_TLOG_ONLY),
    )
    assert requests_in_billing == expected_requests
