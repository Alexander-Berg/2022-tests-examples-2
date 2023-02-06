import json

from tests_vgw_api import db_voice_gateways as vg


async def test_voice_gateway_get_token(taxi_vgw_api):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    response = await taxi_vgw_api.get('v1/voice_gateways/token', params=params)

    assert response.status_code == 200
    assert response.json() == {vg.K_TOKEN: vg.GATEWAY1[vg.K_TOKEN]}


async def test_voice_gateway_get_token_not_found(taxi_vgw_api):
    params = {vg.K_ID: 'non_existing_gateway'}

    response = await taxi_vgw_api.get('v1/voice_gateways/token', params=params)

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'


async def test_voice_gateway_put_token(taxi_vgw_api, pgsql):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {vg.K_TOKEN: 'new_token'}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/token', params=params, data=json.dumps(data),
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert vg.select_gateways(pgsql)[0].token == data[vg.K_TOKEN]


async def test_voice_gateway_put_token_errors(taxi_vgw_api):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {'enabled': False}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/token', params=params, data=json.dumps(data),
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'

    params = {vg.K_ID: 'non_existing_gateway'}

    data = {vg.K_TOKEN: 'new_token'}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/token', params=params, data=json.dumps(data),
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'
