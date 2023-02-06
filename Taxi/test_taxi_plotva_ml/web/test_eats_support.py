import json

import pytest

from taxi_plotva_ml.api import eats_support_v1


BASE_PATH = '/eats/support'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'eats_support'}),
]

CONTROL_TAG = 'ml_fail_control'


@pytest.mark.skip
@pytest.mark.client_experiments3(
    consumer=eats_support_v1.EXP3_EATS_SUPPORT_CONSUMER,
    experiment_name='user',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'sioosidfksdf'}],
    value={'user_in_control': False},
)
async def test_user_not_in_control_requests(web_app_client, load):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200

    response = await web_app_client.post(V1_PATH, data={})
    assert response.status == 400

    response = await web_app_client.post(
        V1_PATH, data=load('empty_comment_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None

    response = await web_app_client.post(
        V1_PATH, data=load('empty_predefined_comments_request.json'),
    )
    assert response.status == 200

    response = await web_app_client.post(
        V1_PATH, data=load('several_predefined_comments_request.json'),
    )
    assert response.status == 200

    response = await web_app_client.post(
        V1_PATH,
        data=load('missed_dish_feedback_is_not_required_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None

    response = await web_app_client.post(
        V1_PATH, data=load('taste_message_and_comment_request_not_reply.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None

    response = await web_app_client.post(
        V1_PATH, data=load('taste_message_and_comment_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None

    response = await web_app_client.post(
        V1_PATH, data=load('not_for_autoreply_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None

    response = await web_app_client.post(
        V1_PATH, data=load('urgent_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None
    assert CONTROL_TAG not in data['tags']

    response = await web_app_client.post(
        V1_PATH, data=load('unknown_comment.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data.get('topics_probabilities') is None


@pytest.mark.skip
@pytest.mark.client_experiments3(
    consumer=eats_support_v1.EXP3_EATS_SUPPORT_CONSUMER,
    experiment_name='user',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'sioosidfksdf'}],
    value={'user_in_control': True},
)
async def test_user_in_control_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('not_for_autoreply_request.json'),
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert data['most_probable_topic'] is not None
    assert CONTROL_TAG in data['tags']
