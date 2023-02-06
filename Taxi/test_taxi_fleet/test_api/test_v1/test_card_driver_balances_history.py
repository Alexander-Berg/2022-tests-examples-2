import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        mock_territories_countries_list,
        headers,
        mock_billing_reports,
        load_json,
):
    stub = load_json('success.json')

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/balances/history',
        headers=headers,
        json={
            'date_from': '2019-09-22T03:00:00+03:00',
            'date_to': '2019-09-22T05:00:00+03:00',
            'driver_id': 'aab36cr7560d499f8acbe2c52a7j7n9p',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_default(
        web_app_client,
        mock_parks,
        mock_territories_countries_list,
        headers,
        mock_billing_reports,
        load_json,
):
    stub = load_json('success_default.json')

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/balances/history',
        headers=headers,
        json={
            'date_from': '2019-09-22T03:00:00+03:00',
            'date_to': '2019-09-22T05:00:00+03:00',
            'driver_id': 'aab36cr7560d499f8acbe2c52a7j7n9p',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
