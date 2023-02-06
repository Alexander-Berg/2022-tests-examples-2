import pytest

DRIVER_AUTH_URL = '/driver/v1/driver-lessons/v1/lessons'
SELFREG_AUTH_URL = '/selfreg/v1/driver-lessons/v1/lessons'


@pytest.mark.parametrize(
    'platform,lessons_count', [('ios', 2), ('android', 2)],
)
async def test_hide_stories_for_ios(
        web_app_client, make_dap_headers, platform, lessons_count,
):
    response = await web_app_client.get(
        DRIVER_AUTH_URL,
        headers=make_dap_headers(
            park_id='park', driver_id='driver_ios', app_platform=platform,
        ),
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['lessons']) == lessons_count


@pytest.mark.parametrize(
    'platform,lessons_count', [('ios', 2), ('android', 2)],
)
async def test_selfreg_hide_stories_for_ios(
        web_app_client,
        make_selfreg_headers,
        make_selfreg_params,
        platform,
        lessons_count,
):
    response = await web_app_client.get(
        SELFREG_AUTH_URL,
        headers=make_selfreg_headers(app_platform=platform),
        params=make_selfreg_params('token'),
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['lessons']) == lessons_count
