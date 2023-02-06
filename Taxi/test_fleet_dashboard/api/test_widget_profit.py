import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_territories_api,
        mock_billing_reports,
        load_json,
):
    stub = load_json('success.json')

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/profit',
        headers=headers,
        json={
            'date_from': '2020-01-20T00:00:00+03:00',
            'date_to': '2020-01-27T00:00:00+03:00',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_empty_response(
        web_app_client,
        headers,
        mock_parks,
        mock_territories_api,
        mock_billing_reports,
        load_json,
):
    stub = load_json('success_empty.json')

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/profit',
        headers=headers,
        json={
            'date_from': '2020-01-20T00:00:00+03:00',
            'date_to': '2020-01-27T00:00:00+03:00',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_empty_one(
        web_app_client,
        headers,
        mock_parks,
        mock_territories_api,
        mock_billing_reports,
        load_json,
):
    stub = load_json('success_empty_one.json')

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/profit',
        headers=headers,
        json={
            'date_from': '2020-01-20T00:00:00+03:00',
            'date_to': '2020-01-27T00:00:00+03:00',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
