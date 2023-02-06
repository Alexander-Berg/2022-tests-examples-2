# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def url():
    return '/ping'


async def test_ping(web_app_client, url):
    response = await web_app_client.get(url)
    assert response.status == 200
    content = await response.text()
    assert content == ''


@pytest.mark.config(TVM_ENABLED=True)
async def test_ping_tvm_enabled(web_app_client, url):
    response = await web_app_client.get(url)
    assert response.status == 200
