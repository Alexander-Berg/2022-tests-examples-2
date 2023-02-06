# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def url():
    return '/v1/get'


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_get_existed_response(web_app_client, url, load_json):
    request = {'ref': 'tumbling'}
    response = await web_app_client.post(url, json=request)
    assert response.status == 200
    data = await response.json()
    assert data == load_json('response_ok.json')


async def test_get_nonexisted_response(web_app_client, url, load_json):
    request = {'ref': 'nonexistent'}
    response = await web_app_client.post(url, json=request)
    assert response.status == 404
    data = await response.json()
    assert data == load_json('response_not_found.json')
