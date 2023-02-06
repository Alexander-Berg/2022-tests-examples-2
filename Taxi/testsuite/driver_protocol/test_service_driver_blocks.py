import json

import pytest


def test_service_driver_blocks(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/driver/blocks',
        params={'park_id': '1488', 'driver_profile_id': 'uuid1'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'can_take_orders': True,
        'reasons': {},
        'blocklist_reasons': {},
    }


@pytest.mark.redis_store(
    ['hset', 'Aggregator:YandexClid', '1369', 'agg_1369'],
    ['sadd', 'Aggregator:Disable', 'agg_1369'],
    ['hset', 'Aggregator:YandexClid', '1370', 'agg_1370'],
    ['hset', 'Aggregator:Balance:agg_1370', '1489', '-200'],
    ['hset', 'Aggregator:agg_1370', 'BalanceLimitAlert', '-100'],
)
@pytest.mark.parametrize(
    'park_id, reasons',
    [
        ('1488', {'ParkAggregatorDisabled': []}),
        (
            '1489',
            {
                'ParkAggregatorDebt': [
                    'limit: -100.000000, balance: -200.000000',
                ],
            },
        ),
    ],
)
def test_service_driver_blocks_aggregator(
        taxi_driver_protocol, park_id, reasons,
):
    response = taxi_driver_protocol.get(
        '/service/driver/blocks',
        params={'park_id': park_id, 'driver_profile_id': 'uuid1'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'can_take_orders': False,
        'reasons': reasons,
        'blocklist_reasons': {},
    }


@pytest.mark.now('2020-06-06T23:59:00Z')
@pytest.mark.redis_store(
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps(
            {'TillDate': '2020-06-10T01:23:45Z', 'Reason': 'car block'},
        ),
    ],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps({'Reason': 'driver block'}),
    ],
    [
        'hset',
        'Driver:DKB:DateNext:Chair:1488',
        'driverSS',
        '"2020-06-05T23:59:00Z"',
    ],
)
def test_service_driver_blocks_blocklist(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/driver/blocks',
        params={
            'park_id': '1488',
            'driver_profile_id': 'driverSS',
            'accept': 'ru',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'blocklist_reasons': {
            'DriverCarBlacklistedTemp': {
                'message': (
                    'Машина временно отключена от заказов. Причина: '
                    'car block. Блокировка снимется через 3 дней'
                ),
                'till': '2020-06-10T01:23:45+0000',
                'title': 'Доступ приостановлен',
            },
            'DriverLicenseBlacklisted': {
                'message': (
                    'Ваша лицензия в чёрном списке. Обратитесь в '
                    'службу поддержки. Причина: driver block'
                ),
                'title': 'Доступ запрещен',
            },
        },
        'can_take_orders': False,
        'reasons': {'need_childchair_photos': []},
    }
