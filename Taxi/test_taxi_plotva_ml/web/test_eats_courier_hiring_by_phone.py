import pytest


BASE_PATH = '/eats_courier_hiring_by_phone'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(
        attrs={'type': 'eats_courier_hiring_by_phone'},
    ),
]


async def test_trivial(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200

    response = await web_app_client.post(V1_PATH, data={})
    assert response.status == 400


async def test_candidate_is_busy_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('candidate_is_busy_first_request.json'),
    )
    assert response.status == 200
    response = await web_app_client.post(
        V1_PATH, data=load('candidate_is_busy_second_request.json'),
    )
    assert response.status == 200


async def test_candidate_not_interested_in_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('candidate_not_interested_in_request.json'),
    )
    assert response.status == 200


async def test_candidate_says_nothing_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('candidate_says_nothing_request.json'),
    )
    assert response.status == 200


async def test_author_type_not_maintained_request(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH, data=load('author_type_not_maintained_request.json'),
    )
    assert response.status == 400
