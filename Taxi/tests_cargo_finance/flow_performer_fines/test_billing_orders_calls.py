import pytest

MOCK_NOW = '2022-07-03T19:16:00.925246+00:00'
UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/'
    'upsert?flow=performer_fines&entity_id=test_id'
)


@pytest.mark.config(
    CARGO_FINANCE_PERFORMER_FINES_FLOW_SETTINGS={'send_to_billing': True},
)
@pytest.mark.now(MOCK_NOW)
async def test_base(
        taxi_cargo_finance,
        mock_v2_process_async,
        get_expected_sum2pay,
        load_json,
):
    request = get_expected_sum2pay('expected_sum2pays.json', '1_request')
    expected = load_json('billing_request.json')
    expected['orders'][-1]['event_at'] = MOCK_NOW

    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert mock_v2_process_async.times_called == 1
    assert mock_v2_process_async.next_call()['request'].json == expected


@pytest.mark.config(
    CARGO_FINANCE_PERFORMER_FINES_FLOW_SETTINGS={'send_to_billing': False},
)
async def test_base_disabled(
        taxi_cargo_finance, mock_v2_process_async, get_expected_sum2pay,
):
    request = get_expected_sum2pay('expected_sum2pays.json', '1_request')

    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert mock_v2_process_async.times_called == 0
