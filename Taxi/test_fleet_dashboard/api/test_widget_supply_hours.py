import aiohttp.web


async def test_success(
        web_app_client, headers, mock_driver_supply_hours, load_json,
):
    stub = load_json('success.json')

    @mock_driver_supply_hours('/v1/parks/supply/retrieve/all-days')
    async def _supply_hours_all_days(request):
        assert request.json == stub['supply']['request']
        return aiohttp.web.json_response(stub['supply']['response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/supply-hours',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
