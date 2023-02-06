from aiohttp import web
import pytest

HEADERS = {'Accept-Language': 'ruRu'}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[pytest.mark.config(DRIVER_CHECK_CONFIG_3_0_ENABLE=True)],
        ),
        pytest.param(
            marks=[pytest.mark.config(DRIVER_CHECK_CONFIG_3_0_ENABLE=False)],
        ),
    ],
)
async def test_retrieve_state(
        web_app_client, mockserver, load_json, mock_quality_control_py3,
):
    @mock_quality_control_py3('/api/v1/state')
    def _mock_state_bulk_retrieve(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(
                id=request.query['id'], type=request.query['type'], exams=[],
            ),
        )

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock_fetch_tags(request):
        return {'tags': ['tag1', 'tag2']}

    response = await web_app_client.post(
        '/v1/retrieve_state',
        headers=HEADERS,
        json=dict(driver_profile_id='1', car_id='1', park_id='1'),
    )

    assert response.status == 200
    assert await response.json() == load_json('retrieve_state_response.json')
