# -*- coding: utf-8 -*-

import pytest

from tests_driver_metrics_storage import util

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76'
    'Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXDiiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848P'
    'W-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkH'
    'R3s'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-metrics-storage'}],
)
@pytest.mark.parametrize('suffix', ['', '/'])
@pytest.mark.parametrize('tvm,code', [(True, 400), (False, 401)])
async def test_400(suffix, tvm, code, taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_stats_unprocessed(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed',
        params={'max_timestamp': '2000-01-01T01:00:00+0000'},
    )
    assert response.status_code == 200
    assert util.to_map(response.json()['items'], 'type') == {
        'type-X': {'count': 5, 'type': 'type-X'},
        'type-Y': {'count': 3, 'type': 'type-Y'},
        'type-Z': {'count': 1, 'type': 'type-Z'},
    }

    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed',
        params={'max_created': '2000-01-01T00:25:00+0000'},
    )
    assert response.status_code == 200
    assert util.to_map(response.json()['items'], 'type') == {
        'type-X': {'count': 4, 'type': 'type-X'},
        'type-Y': {'count': 3, 'type': 'type-Y'},
    }

    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed',
        params={'max_timestamp': '2000-01-01T00:25:00+0000'},
    )
    assert response.status_code == 200
    assert util.to_map(response.json()['items'], 'type') == {
        'type-X': {'count': 4, 'type': 'type-X'},
        'type-Y': {'count': 3, 'type': 'type-Y'},
    }

    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed',
        params={
            'max_timestamp': '2000-01-01T00:25:00+0000',
            'max_created': '2000-01-01T01:00:00+0000',
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json()['items'], 'type') == {
        'type-X': {'count': 4, 'type': 'type-X'},
        'type-Y': {'count': 3, 'type': 'type-Y'},
    }

    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed',
        params={'max_timestamp': '2000-01-01T00:00:00+0000'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}

    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed', params={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Request error: Handler needs at least one parameter',
    }

    response = await taxi_driver_metrics_storage.get(
        'v1/stats/events/unprocessed', params={'max_created': 'xxxbrokenxxx'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'invalid datetime value of \'max_created\' in query: xxxbrokenxxx'
        ),
    }
