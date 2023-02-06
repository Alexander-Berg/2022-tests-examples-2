import json

import pytest

from fbs.tracker import ChainBusyDriverList


#
# For all tests disable Ymaps and 42Group router to use fallback router
#
# Set explicitly
# "ROUTER_FALLBACK_DISTANCE_CORRECTION": 1.0
# "ROUTER_FALLBACK_SPEED": 25.0
# used for distance and time calculation
#
# See config.json for this test


def _check_drivers_in_list(busy_driver_list, drivers_to_check):
    if len(drivers_to_check) != busy_driver_list.ListLength():
        return False

    ids_from_list = set()
    for ind in range(busy_driver_list.ListLength()):
        ids_from_list.add(busy_driver_list.List(ind).DriverId().decode())

    for driver in drivers_to_check:
        if driver not in ids_from_list:
            return False

    return True


#
# Only default settings in config
# Drivers points set so that driver "999012_a5709ce56c2...."
# is drop from set by time to point B (see MAX_ROUTE_TIME: 180)
#
@pytest.mark.config(
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 180,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
    },
)
def test_deflim_drop_driver_by_time(taxi_labor, tracker, redis_store, now):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.786380, 37.564700,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.779101, 37.579721,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 1

    buffer = redis_store.get('chain_busy_drivers:data')
    assert len(buffer) > 0

    chain_busy_driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            buffer, 0,
        )
    )

    assert _check_drivers_in_list(
        chain_busy_driver_list, ['999012_46037aeff0e942e0a31a17330bd931f0'],
    )
    # Here we check that we do not add pax exchange time to time left
    assert chain_busy_driver_list.List(0).LeftTime() < 120


#
# Only default settings in config
# Drivers points set so that driver "999012_a5709ce56c2...."
# is drop from set by line distance to point B
#
@pytest.mark.config(
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 2000,
                'MAX_ROUTE_DISTANCE': 3000,
                'MAX_ROUTE_TIME': 400,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
    },
)
def test_deflim_drop_driver_by_dist(taxi_labor, tracker, redis_store, now):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.786380, 37.564700,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.774673, 37.588466,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 1

    buffer = redis_store.get('chain_busy_drivers:data')
    assert len(buffer) > 0

    chain_busy_driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            buffer, 0,
        )
    )

    assert _check_drivers_in_list(
        chain_busy_driver_list, ['999012_46037aeff0e942e0a31a17330bd931f0'],
    )


#
# Check that setting for current zone_id / class NOT used to
# check chain settings, but most soft available setting are
# used (default in test)
#
@pytest.mark.config(
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 10000,
                'MAX_ROUTE_DISTANCE': 20000,
                'MAX_ROUTE_TIME': 1500,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
        'moscow': {
            'econom': {
                'MAX_LINE_DISTANCE': 10,
                'MAX_ROUTE_DISTANCE': 15,
                'MAX_ROUTE_TIME': 10,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
    },
)
def test_no_drop_driver_by_curr_order_limits_1(
        taxi_labor, tracker, redis_store, now,
):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.786380, 37.564700,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.774673, 37.588466,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 2

    buffer = redis_store.get('chain_busy_drivers:data')
    assert len(buffer) > 0

    chain_busy_driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            buffer, 0,
        )
    )

    assert _check_drivers_in_list(
        chain_busy_driver_list,
        [
            '999012_46037aeff0e942e0a31a17330bd931f0',
            '999012_a5709ce56c2740d9a536650f5390de0b',
        ],
    )


#
# most soft available setting are used (other zone and other tariff)
#
@pytest.mark.config(
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 10,
                'MAX_ROUTE_DISTANCE': 15,
                'MAX_ROUTE_TIME': 10,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
        'moscow': {
            'econom': {
                'MAX_LINE_DISTANCE': 10,
                'MAX_ROUTE_DISTANCE': 15,
                'MAX_ROUTE_TIME': 10,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
        'kaluga': {
            'vip': {
                'MAX_LINE_DISTANCE': 10000,
                'MAX_ROUTE_DISTANCE': 20000,
                'MAX_ROUTE_TIME': 1500,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
    },
)
def test_no_drop_driver_by_curr_order_limits_2(
        taxi_labor, tracker, redis_store, now,
):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.786380, 37.564700,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.774673, 37.588466,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 2

    buffer = redis_store.get('chain_busy_drivers:data')
    assert len(buffer) > 0

    chain_busy_driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            buffer, 0,
        )
    )

    assert _check_drivers_in_list(
        chain_busy_driver_list,
        [
            '999012_46037aeff0e942e0a31a17330bd931f0',
            '999012_a5709ce56c2740d9a536650f5390de0b',
        ],
    )


#
# driver "999012_46037a...." does not fit (time) to limits corresponding
# to its currecnt order (zone_id and) class but fit to most soft
# limits  - this driver shold be added to redis as chain busy
#
# driver "999012_a5709ce..." does not fit (time) to most soft
# limits  - this driver shold NOT be added to redis as chain busy
#
@pytest.mark.config(
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 4000,
                'MAX_ROUTE_DISTANCE': 6000,
                'MAX_ROUTE_TIME': 400,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
        'moscow': {
            'econom': {
                'MAX_LINE_DISTANCE': 200,
                'MAX_ROUTE_DISTANCE': 300,
                'MAX_ROUTE_TIME': 60,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
    },
)
def test_drop_driver_by_max_limits_time(taxi_labor, tracker, redis_store, now):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.777765, 37.581329,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.758778, 37.585536,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 1

    buffer = redis_store.get('chain_busy_drivers:data')
    assert len(buffer) > 0

    chain_busy_driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            buffer, 0,
        )
    )
    assert _check_drivers_in_list(
        chain_busy_driver_list, ['999012_46037aeff0e942e0a31a17330bd931f0'],
    )


#
# driver "999012_46037a...." does not fit (distance) to limits corresponding
# to its currecnt order (zone_id and) class but fit to most soft
# limits  - this driver shold be added to redis as chain busy
#
# driver "999012_a5709ce..." does not fit (distance) to most soft
# limits  - this driver shold NOT be added to redis as chain busy
#
@pytest.mark.config(
    ORDER_CHAIN_SETTINGS={
        '__default__': {
            '__default__': {
                'MAX_LINE_DISTANCE': 200,
                'MAX_ROUTE_DISTANCE': 300,
                'MAX_ROUTE_TIME': 60,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
        'moscow': {
            'econom': {
                'MAX_LINE_DISTANCE': 200,
                'MAX_ROUTE_DISTANCE': 300,
                'MAX_ROUTE_TIME': 60,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
        'kaluga': {
            'vip': {
                'MAX_LINE_DISTANCE': 3000,
                'MAX_ROUTE_DISTANCE': 4500,
                'MAX_ROUTE_TIME': 600,
                'PAX_EXCHANGE_TIME': 120,
            },
        },
    },
)
def test_drop_driver_by_max_limits_distance(
        taxi_labor, tracker, redis_store, now,
):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.777765, 37.581329,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.758778, 37.585536,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 1

    buffer = redis_store.get('chain_busy_drivers:data')
    assert len(buffer) > 0

    chain_busy_driver_list = (
        ChainBusyDriverList.ChainBusyDriverList.GetRootAsChainBusyDriverList(
            buffer, 0,
        )
    )
    assert _check_drivers_in_list(
        chain_busy_driver_list, ['999012_46037aeff0e942e0a31a17330bd931f0'],
    )
