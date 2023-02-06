import aiohttp.web
import pytest


@pytest.mark.parametrize(
    'stub_json', ['success.json', 'success_no_kis_art.json'],
)
async def test_success(
        web_app_client,
        headers,
        mock_parks_certifications,
        load_json,
        stub_json,
):
    stub = load_json(stub_json)

    @mock_parks_certifications('/v1/parks/certifications/list')
    async def _parks_certifications_list(request):
        assert request.json == stub['certifications']['request']
        return aiohttp.web.json_response(stub['certifications']['response'])

    response = await web_app_client.post(
        '/dashboard-api/v1/widget/certification', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
