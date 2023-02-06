import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/quality-metrics/retrieve',
    )
    async def _quality_metrics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/quality-metrics/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
