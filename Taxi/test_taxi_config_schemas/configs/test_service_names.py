import pytest

from test_taxi_config_schemas.configs import common


@pytest.mark.custom_patch_configs_by_group(configs=common.CONFIGS)
@pytest.mark.usefixtures('patch_call_command', 'update_schemas_cache')
async def test_stage_names(monkeypatch, web_app_client):
    async def _get(service_name=None):
        params = {}
        if service_name:
            params['service_name'] = service_name
        return await web_app_client.get(
            '/v1/configs/DEVICENOTIFY_USER_TTL/', params=params,
        )

    async def _post(old_value, new_value, service_name=None):
        params = {}
        if service_name:
            params['service_name'] = service_name
        return await web_app_client.post(
            '/v1/configs/DEVICENOTIFY_USER_TTL/',
            params=params,
            json={'old_value': old_value, 'new_value': new_value},
        )

    response = await _get()
    assert (await response.json())['value'] == 90
    response = await _get('device-devicenotify')
    assert (await response.json())['value'] == 1050
    response = await _post(1050, 103, 'device-devicenotify')
    assert response.status == 200, await response.text()
    response = await _post(90, 102, 'test_3')
    assert response.status == 200, await response.text()
    response = await _post(90, 101)
    assert response.status == 200, await response.text()
    response = await _get()
    assert (await response.json())['value'] == 101
    response = await _get('device-devicenotify')
    assert (await response.json())['value'] == 103
    response = await _get('test_3')
    assert (await response.json())['value'] == 102
