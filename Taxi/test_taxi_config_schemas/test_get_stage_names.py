import pytest


@pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['test_2', 'test_1'])
async def test_get_stage_names(monkeypatch, web_app_client):
    response = await web_app_client.get('/v1/stage-names/list/')
    assert await response.json() == {'stage_names': ['test_1', 'test_2']}
