import json

from tests_vgw_api import db_voice_gateways as vg


async def test_voice_gateway_put_settings(taxi_vgw_api, pgsql):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {
        vg.K_WEIGHT: vg.GATEWAY1[vg.K_SETTINGS][vg.K_WEIGHT] + 1,
        vg.K_DISABLED: not vg.GATEWAY1[vg.K_SETTINGS][vg.K_DISABLED],
        vg.K_NAME: 'new_name',
        vg.K_IDLE_EXPIRES_IN: (
            vg.GATEWAY1[vg.K_SETTINGS][vg.K_IDLE_EXPIRES_IN] + 1
        ),
    }

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/settings', params=params, data=json.dumps(data),
    )

    assert response.status_code == 200
    assert response.json() == {}
    settings = vg.select_gateways(pgsql)[0].settings
    assert settings.weight == data[vg.K_WEIGHT]
    assert settings.disabled == data[vg.K_DISABLED]
    assert settings.name == data[vg.K_NAME]
    assert settings.idle_expires_in == data[vg.K_IDLE_EXPIRES_IN]


async def test_voice_gateway_put_settings_errors(taxi_vgw_api):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {'enabled': False}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/settings', params=params, data=json.dumps(data),
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'

    params = {vg.K_ID: 'non_existing_gateway'}

    data = {
        vg.K_WEIGHT: vg.GATEWAY2[vg.K_SETTINGS][vg.K_WEIGHT],
        vg.K_DISABLED: vg.GATEWAY2[vg.K_SETTINGS][vg.K_DISABLED],
        vg.K_NAME: vg.GATEWAY2[vg.K_SETTINGS][vg.K_NAME],
        vg.K_IDLE_EXPIRES_IN: vg.GATEWAY2[vg.K_SETTINGS][vg.K_IDLE_EXPIRES_IN],
    }

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/settings', params=params, data=json.dumps(data),
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'
