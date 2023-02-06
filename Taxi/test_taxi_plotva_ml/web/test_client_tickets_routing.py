import asyncio
import json

import pytest


BASE_PATH = '/client_tickets_routing'
PATH = BASE_PATH + '/v1'
PING_PATH = BASE_PATH + '/ping'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'client_tickets_routing'}),
]

# For urgent comments on car accidents or emergencies involving police.
CAR_ACCIDENT_CLASS = 0
# For urgent comments related to finances.
URGENT_FINANCE_CLASS = 4
# For strong urgent comments.
URGENT_STRONG_CLASS = 5
# For weak (all other) urgent comments.
URGENT_CLASS = 6
# For comments on regular lost items (earphones, hat, etc.).
LOST_ITEM_FIRST_CLASS = 1
# For comments on more valuable lost items (passport, phone, etc.).
LOST_ITEM_SECOND_CLASS = 2
# For comments that are none of the above.
OTHER_CLASS = 3


@pytest.mark.skip
async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


@pytest.mark.skip
async def test_default(web_app_client):
    tasks = [
        web_app_client.post(PATH, data='{}'),
        web_app_client.post(PATH, data='{"comment": "lol}'),
        web_app_client.post(PATH, data='{"comment": "lol"}'),
    ]
    result = await asyncio.gather(*tasks)

    values = [(response.status, await response.text()) for response in result]
    assert values[0][0] == 400
    assert values[1][0] == 400
    assert values[2][0] == 200
    assert 'probabilities' in values[2][1]


@pytest.mark.skip
async def test_lost_item_keywords(web_app_client, load):
    response = await web_app_client.post(
        PATH, data=load('lost_item_keywords.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())

    assert (
        response_data['probabilities']['lost_item_first']
        + response_data['probabilities']['lost_item_second']
    ) >= 0.7
    assert response_data['predicted_class'] == LOST_ITEM_SECOND_CLASS
    assert response_data['lost_item_second_keywords_triggered'] == 1
    assert response_data['urgent_keywords_triggered'] == 0


@pytest.mark.skip
async def test_lost_item_ml(web_app_client, load):
    response = await web_app_client.post(PATH, data=load('lost_item_ml.json'))
    assert response.status == 200
    response_data = json.loads(await response.text())

    assert (
        response_data['probabilities']['lost_item_first']
        + response_data['probabilities']['lost_item_second']
    ) >= 0.7
    assert response_data['lost_item_second_keywords_triggered'] == 0
    assert response_data['urgent_keywords_triggered'] == 0


@pytest.mark.skip
async def test_urgent_keywords(web_app_client, load):
    response = await web_app_client.post(
        PATH, data=load('urgent_keywords.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())

    assert response_data['probabilities']['car_accident'] >= 0.5
    assert response_data['ml_class'] == CAR_ACCIDENT_CLASS
    assert response_data['lost_item_second_keywords_triggered'] == 0
    assert response_data['urgent_keywords_triggered'] == 1


@pytest.mark.skip
async def test_urgent_ml(web_app_client, load):
    response = await web_app_client.post(PATH, data=load('urgent_ml.json'))
    assert response.status == 200
    response_data = json.loads(await response.text())

    assert response_data['probabilities']['urgent'] >= 0.3
    assert response_data['ml_class'] == URGENT_CLASS
    assert response_data['predicted_class'] == URGENT_CLASS
    assert response_data['lost_item_second_keywords_triggered'] == 0
    assert response_data['urgent_keywords_triggered'] == 0


@pytest.mark.skip
async def test_urgent_strong_ml(web_app_client, load):
    response = await web_app_client.post(
        PATH, data=load('strong_urgent_ml.json'),
    )
    assert response.status == 200
    response_data = json.loads(await response.text())

    assert response_data['probabilities']['urgent_strong'] >= 0.55
    assert response_data['ml_class'] == URGENT_STRONG_CLASS
    assert response_data['predicted_class'] == URGENT_STRONG_CLASS
    assert response_data['lost_item_second_keywords_triggered'] == 0
    assert response_data['urgent_keywords_triggered'] == 1
