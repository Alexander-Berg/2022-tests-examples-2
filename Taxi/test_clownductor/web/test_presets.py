import pytest


@pytest.mark.pgsql('clownductor')
async def test_get_developer_presets(web_app_client):
    response = await web_app_client.get('/v1/presets/developer/')
    assert response.status == 200
    content = await response.json()
    assert len(content['presets']) == 6


@pytest.mark.pgsql('clownductor')
async def test_get_admin_presets(web_app_client):
    response = await web_app_client.get('/v1/presets/admin/')
    assert response.status == 200
    content = await response.json()
    assert len(content['presets']) == 6
