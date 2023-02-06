import aiohttp.web

URL = '/reports-api/v1/cards/driver/transactions/order/download-async'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
}

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


async def test_success(
        web_app_client, headers, load_json, mock_fleet_reports_storage,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    response = await web_app_client.post(
        URL,
        headers=headers,
        params=QUERY,
        json={
            'query': {
                'park': {
                    'order': {'id': '293a821804555a5fa7da56f8101d4ab9'},
                    'driver_profile': {
                        'id': 'baw9fja3bran0l99fjac27tct2hjbfs1p',
                    },
                },
            },
        },
    )

    assert response.status == 200
