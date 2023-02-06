import datetime
import json

import psycopg2.tz
import pytest

from tests_vgw_api import db_voice_gateways as vg


async def test_voice_gateway_get_enabled(taxi_vgw_api):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    response = await taxi_vgw_api.get(
        'v1/voice_gateways/enabled', params=params,
    )

    assert response.status_code == 200
    assert response.json() == {
        'enabled': not vg.GATEWAY1[vg.K_SETTINGS][vg.K_DISABLED],
    }


async def test_voice_gateway_get_enabled_not_found(taxi_vgw_api):
    params = {vg.K_ID: 'non_existing_gateway'}

    response = await taxi_vgw_api.get(
        'v1/voice_gateways/enabled', params=params,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'error': 'GatewayNotFound',
        'message': 'Gateway with id: ' + params[vg.K_ID] + ' not found',
    }


async def test_voice_gateway_put_enabled(taxi_vgw_api, pgsql):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    was_enabled = not vg.GATEWAY1[vg.K_SETTINGS][vg.K_DISABLED]

    data = {'enabled': not was_enabled}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
    )

    assert response.status_code == 200
    assert response.json() == {}
    is_enabled = not vg.select_gateways(pgsql)[0].settings.disabled
    assert is_enabled == (not was_enabled)


async def test_voice_gateway_put_enabled_errors(taxi_vgw_api):
    # Non existing gateway
    params = {vg.K_ID: 'non_existing_gateway'}

    data = {'enabled': False}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
    )

    assert response.status_code == 404
    response_json = response.json()
    assert response_json['code'] == '404'

    # Missing field
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    empty_data = {}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled',
        params=params,
        data=json.dumps(empty_data),
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'

    # Wrong json
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {vg.K_ID: 'wrong_format'}

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == '400'


@pytest.mark.config(
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 100,
    },
)
async def test_voice_gateway_disabling_history(taxi_vgw_api, pgsql):
    params = {vg.K_ID: vg.GATEWAY1[vg.K_ID]}

    data = {
        'enabled': False,
        'updated_by': 'mazgutov',
        'reason': 'manual',
        'additional_data': {'some': 'data'},
        'enable_after': '2021-09-11T12:10:10+0300',
    }

    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
    )
    # check gateway is disabled and history is written
    assert response.status_code == 200
    assert response.json() == {}
    is_enabled = not vg.select_gateways(pgsql)[0].settings.disabled
    assert not is_enabled
    history = vg.select_disabling_history(pgsql, vg.GATEWAY1[vg.K_ID])
    assert len(history) == 1
    assert history[0].disabled_by == 'mazgutov'
    assert history[0].disable_reason == 'manual'
    assert history[0].additional_disable_data == {'some': 'data'}
    assert history[0].enable_after == datetime.datetime(
        2021,
        9,
        11,
        12,
        10,
        10,
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
    )
    assert history[0].relapse_count == 0
    # check that disabling of disabled gateway produces 404
    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled', params=params, data=json.dumps(data),
    )
    assert response.status_code == 404

    # check enabling disabled gateway
    data = {'enabled': True, 'additional_data': {'test': 'data'}}
    response = await taxi_vgw_api.put(
        'v1/voice_gateways/enabled',
        params=params,
        data=json.dumps(data),
        headers={'X-Yandex-Login': 'mazgutov'},
    )
    assert response.status_code == 200
    assert response.json() == {}
    is_enabled = not vg.select_gateways(pgsql)[0].settings.disabled
    assert is_enabled
    history = vg.select_disabling_history(pgsql, vg.GATEWAY1[vg.K_ID])
    assert len(history) == 1
    assert history[0].enabled_by == 'mazgutov'
    assert history[0].additional_enable_data == {'test': 'data'}
