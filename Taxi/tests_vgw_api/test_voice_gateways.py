import json

import pytest

from tests_vgw_api import db_voice_gateways as vg


@pytest.mark.pgsql(
    'vgw_api', queries=['TRUNCATE voice_gateways.voice_gateways CASCADE'],
)
async def test_voice_gateways_post(taxi_vgw_api, pgsql):
    assert vg.select_gateways(pgsql) == []

    def assertions(db_data, sent_data):
        assert db_data.id == sent_data['id']
        if sent_data['settings']['disabled']:
            assert not db_data.enabled_at
            assert vg.is_now(db_data.disabled_at)
        else:
            assert vg.is_now(db_data.enabled_at)
            assert not db_data.disabled_at
        assert db_data.info.host == sent_data['info']['host']
        assert (
            db_data.info.ignore_certificate
            == sent_data['info']['ignore_certificate']
        )
        assert db_data.settings.disabled == sent_data['settings']['disabled']
        assert db_data.settings.name == sent_data['settings']['name']
        assert db_data.settings.weight == sent_data['settings']['weight']
        assert (
            db_data.settings.idle_expires_in
            == sent_data['settings']['idle_expires_in']
        )
        assert db_data.token == sent_data['token']

    response1 = await taxi_vgw_api.post(
        'v1/voice_gateways', data=json.dumps(vg.GATEWAY1),
    )

    gateways = vg.select_gateways(pgsql)
    assert response1.status_code == 200
    assert response1.json() == {}
    assert len(gateways) == 1
    assertions(gateways[0], vg.GATEWAY1)

    response2 = await taxi_vgw_api.post(
        'v1/voice_gateways', data=json.dumps(vg.GATEWAY2),
    )

    gateways = vg.select_gateways(pgsql)
    assert response2.status_code == 200
    response_json = response2.json()
    assert response_json == {}
    assertions(gateways[0], vg.GATEWAY1)
    assertions(gateways[1], vg.GATEWAY2)


async def test_voice_gateways_post_errors(taxi_vgw_api, pgsql):
    assert len(vg.select_gateways(pgsql)) == 2

    # Duplicate ID
    response = await taxi_vgw_api.post(
        'v1/voice_gateways', data=json.dumps(vg.GATEWAY1),
    )

    assert len(vg.select_gateways(pgsql)) == 2
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'

    # Invalid data
    missing_fields_data = {
        vg.K_ID: 'id_1',
        vg.K_TOKEN: 'token_1',
        vg.K_INFO: {vg.K_HOST: 'host_1', vg.K_IGNORE_CERTIFICATE: False},
        vg.K_SETTINGS: {vg.K_NAME: 'name_1', vg.K_WEIGHT: 10},
    }

    response = await taxi_vgw_api.post(
        'v1/voice_gateways', data=json.dumps(missing_fields_data),
    )

    assert len(vg.select_gateways(pgsql)) == 2
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'


async def test_voice_gateways_get(taxi_vgw_api):
    response = await taxi_vgw_api.get('v1/voice_gateways')

    assert response.status_code == 200
    assert response.json() == [
        {
            'id': vg.GATEWAY1[vg.K_ID],
            'host': vg.GATEWAY1[vg.K_INFO][vg.K_HOST],
            'enabled': not vg.GATEWAY1[vg.K_SETTINGS][vg.K_DISABLED],
        },
        {
            'id': vg.GATEWAY2[vg.K_ID],
            'host': vg.GATEWAY2[vg.K_INFO][vg.K_HOST],
            'enabled': not vg.GATEWAY2[vg.K_SETTINGS][vg.K_DISABLED],
        },
    ]
