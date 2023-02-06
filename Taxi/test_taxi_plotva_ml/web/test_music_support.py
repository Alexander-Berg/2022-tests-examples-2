import pytest


BASE_PATH = '/music_support'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'music_support'}),
]


async def test_trivial(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200

    response = await web_app_client.post(V1_PATH, data={})
    assert response.status == 400


async def test_error_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('error_request.json'),
    )
    assert response.status == 200


async def test_content_wishes_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('content_wishes_request.json'),
    )
    assert response.status == 200
