# flake8: noqa
# pylint: disable=W0621,E0102,R1705
import pytest

BASE_PATH = '/drive_classifier'
PATH = BASE_PATH + '/v1'
PING_PATH = BASE_PATH + '/ping'


# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'drive_classifier'}),
]


async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


async def test_empty_request(web_app_client):
    response = await web_app_client.post(PATH, data={})
    assert response.status == 400
