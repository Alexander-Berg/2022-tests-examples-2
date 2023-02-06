import aiohttp.web

URL = '/reports-api/v1/summary/cars/download-async'

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


async def test_success(
        web_app_client, headers, load_json, mock_fleet_reports_storage, stq,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    response = await web_app_client.post(
        URL, headers=headers, params=QUERY, json=stub['service']['request'],
    )

    assert stq.fleet_reports_summary_cars_download_async.has_calls
    assert response.status == 204
