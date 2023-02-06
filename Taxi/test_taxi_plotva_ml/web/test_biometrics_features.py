# flake8: noqa
# pylint: disable=W0621,E0102,R1705
import pytest

BASE_PATH = '/biometrics_features'
V1_PATH = BASE_PATH + '/v1'
V2_PATH = BASE_PATH + '/v2'
PING_PATH = BASE_PATH + '/ping'


# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.enable_ml_handler(url_path=V2_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'biometrics_features'}),
]


async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


async def test_empty_request(web_app_client):
    response_v1 = await web_app_client.post(V1_PATH, data={})
    assert response_v1.status == 400

    response_v2 = await web_app_client.post(V2_PATH, data={})
    assert response_v2.status == 400
