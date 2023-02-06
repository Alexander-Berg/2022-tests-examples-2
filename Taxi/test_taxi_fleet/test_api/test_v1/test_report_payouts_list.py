import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_billing_bank_orders,
):
    service_stub = load_json('service_success.json')
    billing_bank_orders_stub = load_json('billing_bank_orders_success.json')

    @mock_billing_bank_orders('/v1/parks/payments/search')
    async def _v1_parks_payments_search(request):
        assert request.json == billing_bank_orders_stub['request']
        return aiohttp.web.json_response(billing_bank_orders_stub['response'])

    response = await web_app_client.post(
        'api/v1/reports/payouts/list',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
