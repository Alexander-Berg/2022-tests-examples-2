import json

from tests_vgw_api import db_voice_gateways as vg


async def test_voice_gateway_put_info(taxi_vgw_api, pgsql):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {
        vg.K_HOST: 'new_host',
        vg.K_IGNORE_CERTIFICATE: not vg.GATEWAY1[vg.K_INFO][
            vg.K_IGNORE_CERTIFICATE
        ],
    }

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/info', params=params, data=json.dumps(data),
    )

    assert response.status_code == 200
    assert response.json() == {}
    info = vg.select_gateways(pgsql)[0].info
    assert info.host == data[vg.K_HOST]
    assert info.ignore_certificate == data[vg.K_IGNORE_CERTIFICATE]


async def test_voice_gateway_put_info_error(taxi_vgw_api):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {'enabled': False}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/info', params=params, data=json.dumps(data),
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'

    params = {vg.K_ID: 'non_existing_gateway'}

    data = {
        vg.K_HOST: 'new_host',
        vg.K_IGNORE_CERTIFICATE: not vg.GATEWAY1[vg.K_INFO][
            vg.K_IGNORE_CERTIFICATE
        ],
    }

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/info', params=params, data=json.dumps(data),
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'
