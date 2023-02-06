import datetime

import pytest

import tests_dispatch_airport_view.utils as utils

DRIVERS_UPDATER = 'drivers-updater'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.redis_store(
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {'updated_ts': '1000', 'geobus_ts': 1000, 'pins': '[]'},
    ],
)
@pytest.mark.parametrize('provider_check_enabled', [False, True])
@pytest.mark.now('2022-01-17T13:00:00+00:00')
async def test_provider(
        taxi_dispatch_airport_view,
        redis_store,
        testpoint,
        now,
        taxi_config,
        mockserver,
        load_json,
        provider_check_enabled,
):
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_ORDER_PROVIDERS_CHECK': {
                'enabled': provider_check_enabled,
                'providers': ['taxi'],
            },
        },
    )

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return {
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid0',
                },
                {
                    'classes': ['econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'uuid': 'uuid1',
                },
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert set(request.json['id_in_set']) == set(
            {'dbid_uuid0', 'dbid_uuid1'},
        )
        assert set(request.json['projection']) == set({'data.orders_provider'})
        return load_json('driver_profiles.json')

    @testpoint('position-processor-finished')
    def position_processor_finished(_):
        pass

    @testpoint(DRIVERS_UPDATER + '-finished')
    def drivers_updater_finished(data):
        return data

    await taxi_dispatch_airport_view.enable_testpoints()

    # existed drivers: dbid_uuid0
    # new drivers: dbid_uuid1
    # out of all ports driver: dbid_uuid2

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid0': {
            'position': utils.NEAR_EKB_AIRPORT_1,
            'timestamp': geobus_now,
        },
        'dbid_uuid1': {
            'position': utils.NEAR_EKB_AIRPORT_2,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.OUT_EKB_RADIUS,
            'timestamp': geobus_now,
        },
    }
    message = utils.edge_channel_message(geobus_drivers, now)
    redis_store.publish(utils.EDGE_TRACKS_CHANNEL, message)
    await position_processor_finished.wait_call()

    await taxi_dispatch_airport_view.run_distlock_task(DRIVERS_UPDATER)

    await drivers_updater_finished.wait_call()

    response_1 = redis_store.hgetall(utils.driver_info_key('dbid_uuid0'))
    response_2 = redis_store.hgetall(utils.driver_info_key('dbid_uuid1'))
    if provider_check_enabled:
        assert response_1.get(b'is_hidden') == b'false'
        assert response_2.get(b'is_hidden') == b'true'
    else:
        assert response_1.get(b'is_hidden') is None
        assert response_2.get(b'is_hidden') is None

    response_3 = redis_store.hgetall(utils.driver_info_key('dbid_uuid2'))
    assert response_3 == {}
