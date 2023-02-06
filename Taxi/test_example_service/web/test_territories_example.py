import pytest


@pytest.mark.usefixtures('territories_mock')
async def test_get_countries(web_app_client):
    response = await web_app_client.get('/territories/get_countries')
    assert response.status == 200
    assert int(await response.read()) == 1
