import json

import pytest


BASE_PATH = '/parks_support'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'parks_support'}),
]


@pytest.mark.xfail
async def test_trivial(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200

    response = await web_app_client.post(V1_PATH, data={})
    assert response.status == 400


@pytest.mark.xfail
async def test_payment_not_recieved(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('payment_not_recieved.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.7


@pytest.mark.xfail
async def test_driver_rating(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('driver_rating.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.7


@pytest.mark.xfail
async def test_feedback_about_rider_general(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('feedback_about_rider_general.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('parent_confidence') > 0.5
    assert response_data.get('confidence') < 0.5


@pytest.mark.xfail
async def test_lost_items(web_app_client, load):
    response = await web_app_client.post(V1_PATH, data=load('lost_items.json'))
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.7
