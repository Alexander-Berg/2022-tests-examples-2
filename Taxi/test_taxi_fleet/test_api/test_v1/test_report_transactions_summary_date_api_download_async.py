import aiohttp.web

URL = '/api/v1/reports/transactions-summary-date-api/download-async'

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
            'period': 'monthly',
            'accrued_at': {
                'from': '2019-09-08T11:16:11+00:00',
                'to': '2019-09-09T11:16:11+00:00',
            },
        },
    )

    assert response.status == 200
