import json

import pytest

from taxi_plotva_ml.api import drivers_support_v1

BASE_PATH = '/drivers_support'
V1_PATH = BASE_PATH + '/v1'
V2_PATH = BASE_PATH + '/v2'
PING_V1_PATH = V1_PATH + '/ping'
PING_V2_PATH = V1_PATH + '/ping'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.enable_ml_handler(url_path=V2_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'drivers_support'}),
    pytest.mark.download_ml_resource(
        attrs={'type': 'taxi_drivers_chat_support'},
    ),
]


@pytest.mark.skip
async def test_trivial(web_app_client):
    response = await web_app_client.get(PING_V1_PATH)
    assert response.status == 200
    response = await web_app_client.get(PING_V2_PATH)
    assert response.status == 200

    response = await web_app_client.post(V1_PATH, data={})
    assert response.status == 400


@pytest.mark.skip
async def test_payment_not_recieved(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('payment_not_recieved.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
async def test_driver_rating(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('driver_rating.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
async def test_feedback_about_rider_general(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('feedback_about_rider_general.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('parent_confidence') > 0.5
    assert response_data.get('confidence') < 0.5


@pytest.mark.skip
async def test_feedback_about_rider_excessive_cancellations(
        web_app_client, load,
):
    response = await web_app_client.post(
        V1_PATH,
        data=load('feedback_about_rider_excessive_cancellations.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
async def test_feedback_about_rider_kids(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('feedback_about_rider_kids.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
async def test_feedback_about_rider_minor_altercation(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('feedback_about_rider_minor_altercation.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
async def test_feedback_about_rider_suspected_fraud(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('feedback_about_rider_suspected_fraud.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
async def test_lost_items(web_app_client, load):
    response = await web_app_client.post(V1_PATH, data=load('lost_items.json'))
    assert response.status == 200
    response_data = json.loads(await response.text())
    assert response_data.get('confidence') >= 0.2


@pytest.mark.skip
@pytest.mark.client_experiments3(
    consumer=drivers_support_v1.EXP3_DRIVERS_SUPPORT,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_ok_request(web_app_client, load):
    response = await web_app_client.post(V2_PATH, data=load('ok_request.json'))
    assert response.status == 200


@pytest.mark.skip
@pytest.mark.client_experiments3(
    consumer=drivers_support_v1.EXP3_DRIVERS_SUPPORT,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_not_reply_request(web_app_client, load):
    response = await web_app_client.post(
        V2_PATH, data=load('not_reply_request.json'),
    )
    assert response.status == 200


@pytest.mark.skip
@pytest.mark.client_experiments3(
    consumer=drivers_support_v1.EXP3_DRIVERS_SUPPORT,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_nope_request(web_app_client, load):
    response = await web_app_client.post(
        V2_PATH, data=load('nope_request.json'),
    )
    assert response.status == 200


@pytest.mark.skip
async def test_no_user_id_request(web_app_client, load):
    response = await web_app_client.post(
        V2_PATH, data=load('no_user_id_request.json'),
    )
    assert response.status == 200
