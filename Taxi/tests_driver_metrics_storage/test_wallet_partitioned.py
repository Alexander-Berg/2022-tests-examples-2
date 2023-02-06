import pytest

from tests_driver_metrics_storage import util


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
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_wallet_history_partitioned(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udid': '100000000000000000000000',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'amount': 16,
            'reason': '',
            'tariff_zone': 'moscow',
            'timestamp': '2000-01-01T00:00:06+00:00',
            'transaction_id': 'ev-6',
            'value': 16,
        },
        {
            'amount': 31,
            'reason': '',
            'timestamp': '2000-01-01T00:00:05+00:00',
            'transaction_id': 'ev-5',
            'value': 15,
        },
        {
            'amount': 43,
            'reason': '',
            'tariff_zone': 'moscow',
            'timestamp': '2000-01-01T00:00:02+00:00',
            'transaction_id': 'ev-2',
            'value': 12,
        },
        {
            'amount': 54,
            'reason': '',
            'timestamp': '2000-01-01T00:00:01+00:00',
            'transaction_id': 'ev-1',
            'value': 11,
        },
    ]

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2000-01-01T00:00:05+0000',
            'udid': '100000000000000000000000',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'amount': 12,
            'reason': '',
            'tariff_zone': 'moscow',
            'timestamp': '2000-01-01T00:00:02+00:00',
            'transaction_id': 'ev-2',
            'value': 12,
        },
        {
            'amount': 23,
            'reason': '',
            'timestamp': '2000-01-01T00:00:01+00:00',
            'transaction_id': 'ev-1',
            'value': 11,
        },
    ]

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:05+0000',
            'ts_to': '2000-01-01T00:00:10+0000',
            'udid': '100000000000000000000000',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'amount': 16,
            'reason': '',
            'tariff_zone': 'moscow',
            'timestamp': '2000-01-01T00:00:06+00:00',
            'transaction_id': 'ev-6',
            'value': 16,
        },
        {
            'amount': 31,
            'reason': '',
            'timestamp': '2000-01-01T00:00:05+00:00',
            'transaction_id': 'ev-5',
            'value': 15,
        },
    ]

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/history',
        json={
            'ts_from': '2000-01-01T00:00:02+0000',
            'ts_to': '2000-01-01T00:00:06+0000',
            'udid': '100000000000000000000000',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'amount': 15,
            'reason': '',
            'timestamp': '2000-01-01T00:00:05+00:00',
            'transaction_id': 'ev-5',
            'value': 15,
        },
        {
            'amount': 27,
            'reason': '',
            'tariff_zone': 'moscow',
            'timestamp': '2000-01-01T00:00:02+00:00',
            'transaction_id': 'ev-2',
            'value': 12,
        },
    ]


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
@pytest.mark.pgsql('drivermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_wallet_balance_partitioned(taxi_driver_metrics_storage):
    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udids': ['100000000000000000000000', '200000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 4,
            'last_ts': '2000-01-01T00:00:08+00:00',
            'udid': '100000000000000000000000',
            'value': 54,
        },
        '200000000000000000000000': {
            'count': 4,
            'last_ts': '2000-01-01T00:00:08+00:00',
            'udid': '200000000000000000000000',
            'value': 54,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2000-01-01T00:00:05+0000',
            'udids': ['100000000000000000000000', '200000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:04+00:00',
            'udid': '100000000000000000000000',
            'value': 23,
        },
        '200000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:04+00:00',
            'udid': '200000000000000000000000',
            'value': 23,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:05+0000',
            'ts_to': '2000-01-01T00:00:10+0000',
            'udids': ['100000000000000000000000', '200000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:08+00:00',
            'udid': '100000000000000000000000',
            'value': 31,
        },
        '200000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:08+00:00',
            'udid': '200000000000000000000000',
            'value': 31,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:02+0000',
            'ts_to': '2000-01-01T00:00:06+0000',
            'udids': ['100000000000000000000000', '200000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:05+00:00',
            'udid': '100000000000000000000000',
            'value': 27,
        },
        '200000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:05+00:00',
            'udid': '200000000000000000000000',
            'value': 27,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2100-01-01T00:00:00+0000',
            'udids': ['100000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 4,
            'last_ts': '2000-01-01T00:00:08+00:00',
            'udid': '100000000000000000000000',
            'value': 54,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:00+0000',
            'ts_to': '2000-01-01T00:00:05+0000',
            'udids': ['100000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:04+00:00',
            'udid': '100000000000000000000000',
            'value': 23,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:05+0000',
            'ts_to': '2000-01-01T00:00:10+0000',
            'udids': ['100000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:08+00:00',
            'udid': '100000000000000000000000',
            'value': 31,
        },
    }

    response = await taxi_driver_metrics_storage.post(
        'v1/wallet/balance',
        json={
            'ts_from': '2000-01-01T00:00:02+0000',
            'ts_to': '2000-01-01T00:00:06+0000',
            'udids': ['100000000000000000000000'],
        },
    )
    assert response.status_code == 200
    assert util.to_map(response.json(), 'udid') == {
        '100000000000000000000000': {
            'count': 2,
            'last_ts': '2000-01-01T00:00:05+00:00',
            'udid': '100000000000000000000000',
            'value': 27,
        },
    }
