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
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history' + suffix,
        headers={'X-Ya-Service-Ticket': MOCK_TICKET if tvm else ''},
        json={},
    )
    assert response.status_code == code


@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_wallet(taxi_driver_metrics_storage, pgsql):

    cursor = pgsql['drivermetrics'].conn.cursor()
    for x in range(15):
        cursor.execute(
            'insert into common.udids (udid_id,udid)values('
            + str(x + 1)
            + ',\'udid-'
            + str(x + 1)
            + '\')',
        )
    await taxi_driver_metrics_storage.invalidate_caches()

    # запрос баланса (в т.ч. с невалидным udid)
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udids': [
                'udid-1',
                'uuid-invalid',
                'udid-2',
                'udid-12',
                'udid-1111',
            ],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        'udid-1': {'count': 0, 'udid': 'udid-1', 'value': 0},
        'udid-1111': {'count': 0, 'udid': 'udid-1111', 'value': 0},
        'udid-12': {'count': 0, 'udid': 'udid-12', 'value': 0},
        'udid-2': {'count': 0, 'udid': 'udid-2', 'value': 0},
        'uuid-invalid': {'count': 0, 'udid': 'uuid-invalid', 'value': 0},
    }


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_CLEANER_SETTINGS={
        'wallet_logs_expire_days': 20000,
        'wallet_logs_clean_limit': 300,
        'wallet_logs_clean_repeat': 1,
        'events_expire_days': 20000,
        'events_clean_limit': 300,
        'events_clean_repeat': 1,
        'events_logs_partitioned_clean_limit': 300,
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_wallet_history(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udid': 'Q',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'amount': 10,
            'reason': '',
            'tariff_zone': 'ZZZ',
            'timestamp': '2000-01-01T00:00:01+00:00',
            'transaction_id': 'ev-2',
            'value': 10,
        },
        {
            'amount': 20,
            'reason': '',
            'timestamp': '2000-01-01T00:00:01+00:00',
            'transaction_id': 'ev-1',
            'value': 10,
        },
    ]

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udid': 'Q.2',
        },
    )
    assert response.status_code == 200
    assert response.json() == []

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udids': ['Q', 'Q.1', 'Q.2', 'Q.3', 'W', 'E'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        'E': {'count': 0, 'udid': 'E', 'value': 0},
        'Q': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:02+00:00',
            'udid': 'Q',
            'value': 20,
        },
        'Q.1': {'count': 0, 'udid': 'Q.1', 'value': 0},
        'Q.2': {'count': 0, 'udid': 'Q.2', 'value': 0},
        'Q.3': {
            'count': 1,
            'last_ts': '2000-01-01T00:00:02+00:00',
            'udid': 'Q.3',
            'value': 6,
        },
        'W': {'count': 0, 'udid': 'W', 'value': 0},
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2000-01-01T01:20:00+0000',
            'udid': 'Q',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'amount': 10,
            'reason': '',
            'tariff_zone': 'ZZZ',
            'timestamp': '2000-01-01T00:00:01+00:00',
            'transaction_id': 'ev-2',
            'value': 10,
        },
        {
            'amount': 20,
            'reason': '',
            'timestamp': '2000-01-01T00:00:01+00:00',
            'transaction_id': 'ev-1',
            'value': 10,
        },
    ]

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2000-01-01T04:20:00+0300',
            'udids': ['Q', 'Q.1', 'Q.2', 'Q.3', 'W', 'E'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        'E': {'count': 0, 'udid': 'E', 'value': 0},
        'Q': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:02+00:00',
            'udid': 'Q',
            'value': 20,
        },
        'Q.1': {'count': 0, 'udid': 'Q.1', 'value': 0},
        'Q.2': {'count': 0, 'udid': 'Q.2', 'value': 0},
        'Q.3': {
            'count': 1,
            'last_ts': '2000-01-01T00:00:02+00:00',
            'udid': 'Q.3',
            'value': 6,
        },
        'W': {'count': 0, 'udid': 'W', 'value': 0},
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udid': 'invalid-udid',
        },
    )
    assert response.status_code == 200
    assert response.json() == []

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-02T00:00:00+0000',
            'ts_to': '2000-01-01T04:20:00+0000',
            'udids': ['Q', 'Q.1', 'Q.2', 'Q.3', 'W', 'E'],
        },
    )
    assert response.status_code == 400


@pytest.mark.config(
    DRIVER_METRICS_STORAGE_CLEANER_SETTINGS={
        'wallet_logs_expire_days': 20000,
        'wallet_logs_clean_limit': 300,
        'wallet_logs_clean_repeat': 1,
        'events_expire_days': 20000,
        'events_clean_limit': 300,
        'events_clean_repeat': 1,
        'events_logs_partitioned_clean_limit': 300,
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_wallet_balance_nonexistent_udid(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udids': ['nonexistentudid000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        'nonexistentudid000000000': {
            'count': 0,
            'udid': 'nonexistentudid000000000',
            'value': 0,
        },
    }
