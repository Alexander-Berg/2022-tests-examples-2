import json

import pytest

from taxi_plotva_ml.api import smm_support_v1


BASE_PATH = '/smm_support'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_support_taxi'}),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_support_eats'}),
]

TAXI_TAG = 'smmtaxi_v1'
EATS_TAG = 'smmeats_v1'
CONTROL_TAG = 'ml_fail_control'


@pytest.mark.client_experiments3(
    consumer=smm_support_v1.EXP3_SMM_SUPPORT_CONSUMER,
    experiment_name='smm_support_ml_quality',
    args=[{'name': 'mention_id', 'type': 'string', 'value': '91392'}],
    value={'post_for_control': False},
)
async def test_post_not_for_control_requests(web_app_client, load):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200

    response = await web_app_client.post(V1_PATH, data={})
    assert response.status == 400

    response = await web_app_client.post(
        V1_PATH, data=load('taxi_spam_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert TAXI_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('taxi_not_reply_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert TAXI_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('taxi_reply_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert TAXI_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('taxi_reply_because_rules_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert TAXI_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('eats_reply_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert EATS_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('eats_hiring_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert EATS_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('eats_no_text_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert EATS_TAG in data.get('tags')
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('unknown_topic_group_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data.get('topic') == str()
    assert data.get('topics_probabilities') == list()
    assert CONTROL_TAG not in data['tags']


@pytest.mark.client_experiments3(
    consumer=smm_support_v1.EXP3_SMM_SUPPORT_CONSUMER,
    experiment_name='smm_support_ml_quality',
    args=[{'name': 'mention_id', 'type': 'string', 'value': '91392'}],
    value={'post_for_control': True},
)
async def test_post_for_control_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('eats_hiring_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert EATS_TAG in data['tags']
    assert CONTROL_TAG in data['tags']
