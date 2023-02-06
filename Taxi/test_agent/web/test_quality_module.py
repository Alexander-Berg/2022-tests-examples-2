import pytest


@pytest.mark.parametrize(
    'url,status',
    [
        ('/v1/quality_module/webalex', 200),
        ('/v1/quality_module/detailing/webalex', 200),
        ('/v1/quality_module/detailing/id/item', 200),
    ],
)
async def test_quality_module(web_context, web_app_client, url, status):
    response = await web_app_client.get(
        url, headers={'X-Yandex-Login': 'test', 'Accept-Language': 'ru-ru'},
    )
    assert response.status == status
