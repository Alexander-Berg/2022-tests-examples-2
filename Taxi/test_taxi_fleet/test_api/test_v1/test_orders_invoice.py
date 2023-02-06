import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mock_parks_replica,
        mock_billing_replication,
        mock_driver_orders,
        load_json,
):
    stub = load_json('success.json')

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def _get_parks_billing_client_id(request):
        assert request.query['consumer'] == 'taxi-fleet'
        assert request.query['park_id'] == '111111'
        return aiohttp.web.json_response(stub['parks_response'])

    @mock_billing_replication('/person/')
    async def _get_person(request):
        assert request.query['client_id'] == 'billing_client_id'
        return aiohttp.web.json_response(stub['billing_response'])

    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        assert request.json == stub['api7_request']
        return aiohttp.web.json_response(stub['api7_response'])

    response = await web_app_client.post(
        '/api/v1/orders/invoice',
        headers=headers,
        json={
            'id': 'aaq3bcras60d499f8ac57tc52aj8fs9p',
            'booked_at': '2019-09-06T14:16:11+03:00',
        },
    )

    assert response.status == 200
