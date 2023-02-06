import pytest

from taxi_config_schemas import settings
from test_taxi_config_schemas.configs import common


@pytest.mark.config(CONFIG_SCHEMAS_STAGE_NAMES=['test_1', 'test_3'])
@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_stage_names(monkeypatch, web_app_client):
    monkeypatch.setattr(settings, 'ALLOW_STAGE_NAME', True)

    async def _get(stage_name=None):
        params = {}
        if stage_name:
            params['stage_name'] = stage_name
        return await web_app_client.get(
            '/v1/configs/DEVICENOTIFY_USER_TTL/', params=params,
        )

    async def _post(old_value, new_value, stage_name=None):
        params = {}
        if stage_name:
            params['stage_name'] = stage_name
        return await web_app_client.post(
            '/v1/configs/DEVICENOTIFY_USER_TTL/',
            params=params,
            json={'old_value': old_value, 'new_value': new_value},
        )

    response = await _get()
    assert (await response.json())['value'] == 90
    response = await _get('test_2')
    assert response.status == 400
    response = await _get('test_1')
    assert (await response.json())['value'] == 90
    response = await _post(90, 100, 'test_2')
    assert response.status == 400
    response = await _post(90, 100, 'test_1')
    assert response.status == 200
    response = await _post(90, 102, 'test_3')
    assert response.status == 200
    response = await _post(90, 101)
    assert response.status == 200
    response = await _get()
    assert (await response.json())['value'] == 101
    response = await _get('test_1')
    assert (await response.json())['value'] == 100
    response = await _get('test_3')
    assert (await response.json())['value'] == 102
