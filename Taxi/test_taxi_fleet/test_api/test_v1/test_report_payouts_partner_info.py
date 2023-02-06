import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_parks_replica,
        mock_billing_replication,
        mock_parks_activation,
):
    service_stub = load_json('service.json')

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def _v1_parks_billing_client_id_retrieve(request):
        stub = load_json('parks_replica__get_parks_billing_client_id.json')
        assert request.query == stub['request']
        return aiohttp.web.json_response(stub['response'])

    @mock_billing_replication('/person/')
    async def _person(request):
        stub = load_json('billing_replication__get_person.json')
        assert request.query == stub['request']
        return aiohttp.web.json_response(stub['response'])

    @mock_billing_replication('/contract/')
    async def _contract(request):
        stub = load_json('billing_replication__contract_get.json')
        assert request.query == stub['request']
        return aiohttp.web.json_response(stub['response'])

    @mock_parks_activation('/v1/parks/activation/balances')
    async def _v1_parks_activation_balances(request):
        stub = load_json('parks_activation_balances__get.json')
        assert request.query == stub['request']
        return aiohttp.web.json_response(stub['response'])

    response = await web_app_client.post(
        '/api/v1/reports/payouts/partner/info', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
