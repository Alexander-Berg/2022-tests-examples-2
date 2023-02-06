import copy

from tests_vgw_api import db_consumers as consumers
from tests_vgw_api import db_voice_gateways as vg


async def test_voice_gateway_get(taxi_vgw_api):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    was_enabled = not vg.GATEWAY1[vg.K_SETTINGS][vg.K_DISABLED]

    response = await taxi_vgw_api.get('v1/voice_gateways/id', params=params)

    assert response.status_code == 200
    response_json = response.json()
    if was_enabled:
        assert vg.is_now_str(response_json.pop(vg.K_ENABLED_AT))
        assert not response_json.get(vg.K_DISABLED_AT)
    else:
        assert not response_json.get(vg.K_ENABLED_AT)
        assert vg.is_now_str(response_json.pop(vg.K_DISABLED_AT))

    vg_without_token = copy.deepcopy(vg.GATEWAY1)
    vg_without_token.pop(vg.K_TOKEN)
    assert response_json == vg_without_token


async def test_voice_gateway_get_errors(taxi_vgw_api):
    # Not found
    params = {vg.K_ID: 'non_existing_gateway'}

    response = await taxi_vgw_api.get('v1/voice_gateways/id', params=params)

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'


async def test_voice_gateway_delete(taxi_vgw_api, pgsql):
    assert len(vg.select_gateways(pgsql)) == 2

    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    gateways = consumers.select_consumer_vg_by_gateway(
        pgsql, vg.GATEWAY1[vg.K_ID],
    )
    assert gateways

    response = await taxi_vgw_api.delete('v1/voice_gateways/id', params=params)

    assert response.status_code == 200
    assert response.json() == {}
    vgws = vg.select_gateways(pgsql)
    was_deleted = False
    for vgw in vgws:
        if vgw.id == vg.GATEWAY1[vg.K_ID]:
            was_deleted = vgw.deleted

    gateways = consumers.select_consumer_vg_by_gateway(
        pgsql, vg.GATEWAY1[vg.K_ID],
    )
    assert not gateways
    assert was_deleted


async def test_voice_gateway_delete_not_found(taxi_vgw_api):
    params = {vg.K_ID: 'non_existing_gateway'}

    response = await taxi_vgw_api.delete('v1/voice_gateways/id', params=params)

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'
