import aiohttp.web
import pytest


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_REPORTS_CHART_RATINGS_HISTORY={
        'chart_line_color': '#00CA50',
        'chart_smoothing': True,
        'critical_minimum': 1.2,
        'critical_minimum_color': '#F5222D',
    },
)
async def test_success(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/ratings-history/retrieve',
    )
    async def _ratings_history_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/ratings-history/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
