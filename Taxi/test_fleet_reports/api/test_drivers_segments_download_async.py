import aiohttp.web

URL = '/reports-api/v1/drivers/segments/download-async'

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


async def test_success(
        web_app_client, headers, mock_fleet_reports_storage, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    response = await web_app_client.post(
        URL, headers=headers, params=QUERY, json=stub['service']['request'],
    )

    assert response.status == 200
