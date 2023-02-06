import asyncio
import json

import pytest

from taxi_plotva_ml.api import autoreply_general_v1


BASE_PATH = '/autoreply_general'
PATH = BASE_PATH + '/v1'
PATH_V2 = BASE_PATH + '/v2'
PING_PATH = PATH + '/ping'
PING_PATH_V2 = PATH_V2 + '/ping'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.enable_ml_handler(url_path=PATH_V2),
    pytest.mark.download_ml_resource(attrs={'type': 'autoreply_general'}),
    pytest.mark.download_ml_resource(
        attrs={'type': 'taxi_client_chat_support'},
    ),
]

CONTROL_TAG = 'ml_fail_control'


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200
    response = await web_app_client.get(PING_PATH_V2)
    assert response.status == 200


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER,
    experiment_name='autoreply_general_control',
    args=[
        {'name': 'user_or_request_id', 'type': 'string', 'value': 'user_id'},
    ],
    value={'user_in_control': False},
)
async def test_general_default(web_app_client):
    tasks = [
        web_app_client.post(PATH, data='{}'),
        web_app_client.post(PATH, data='{"comment": "lol"}'),
        web_app_client.post(
            PATH,
            data='{"comment": "Нет прома","request_id":"1", '
            '"user_id":"user_id", "request_repeated": false, '
            '"ml_request_id":"1234"}',
        ),
    ]
    result = await asyncio.gather(*tasks)
    values = [(response.status, await response.text()) for response in result]
    assert values[0][0] == 400
    assert values[1][0] == 400
    assert values[2][0] == 200


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER,
    experiment_name='autoreply_general_control',
    args=[
        {
            'name': 'user_or_request_id',
            'type': 'string',
            'value': 'no_such_user_id_in_your_base',
        },
    ],
    value={'user_in_control': False},
)
async def test_general_antifrod_logic(web_app_client, load):
    response_new_user = await web_app_client.post(
        PATH, data=load('new_ride_user.json'),
    )
    assert response_new_user.status == 200
    data = json.loads(await response_new_user.text())
    assert CONTROL_TAG not in data['tags']


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER_CHANGE,
    experiment_name='autoreply_general_control_change',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_general_topic_no_change(web_app_client, load):
    response_no_change = await web_app_client.post(
        PATH, data=load('topic_no_change.json'),
    )
    assert response_no_change.status == 200
    data = json.loads(await response_no_change.text())
    assert data.get('predicted_change', 37) == 37
    assert data.get('predicted_promo_value', 40) >= 37
    assert CONTROL_TAG not in data['tags']


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
async def test_general_no_user_request_id(web_app_client, load):
    response_user = await web_app_client.post(
        PATH, data=load('no_user_id.json'),
    )
    assert response_user.status == 400
    response_request = await web_app_client.post(
        PATH, data=load('no_request_id.json'),
    )
    assert response_request.status == 400


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_ok_request(web_app_client, load):
    response = await web_app_client.post(PATH_V2, data=load('ok_request.json'))
    assert response.status == 200


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_not_reply_request(web_app_client, load):
    response = await web_app_client.post(
        PATH_V2, data=load('not_reply_request.json'),
    )
    assert response.status == 200


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
@pytest.mark.client_experiments3(
    consumer=autoreply_general_v1.EXP3_AUTOREPLY_GENERAL_CONSUMER,
    experiment_name='autoreply_general_control',
    args=[{'name': 'user_id', 'type': 'string', 'value': 'user_id'}],
    value={'user_in_control': False},
)
async def test_nope_request(web_app_client, load):
    response = await web_app_client.post(
        PATH_V2, data=load('nope_request.json'),
    )
    assert response.status == 200


@pytest.mark.skip(reason='To heavy support_config, to be fixed in TAXIML-3278')
async def test_no_user_id_request(web_app_client, load):
    response = await web_app_client.post(
        PATH_V2, data=load('no_user_id_request.json'),
    )
    assert response.status == 400
