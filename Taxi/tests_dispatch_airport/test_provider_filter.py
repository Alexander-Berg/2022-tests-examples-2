import datetime

import pytest

import tests_dispatch_airport.utils as utils

PROVIDER_FILTER_NAME = 'provider-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('provider_check_allowed', [True, False])
async def test_provider_filter_by_profiles(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        provider_check_allowed,
):
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_ORDER_PROVIDERS_CHECK': {
                'enabled': provider_check_allowed,
                'providers': ['taxi'],
            },
        },
    )

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(PROVIDER_FILTER_NAME + '-finished')
    def provider_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert len(request.json['id_in_set']) == 5
        assert set(request.json['projection']) == set({'data.orders_provider'})
        return load_json('profiles.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: taxi
    # dbid_uuid2 - new driver: lavka
    # dbid_uuid3 - new driver: courier
    # dbid_uuid4 - new driver: taxi + courier
    # dbid_uuid5 - new driver: no provider, fallback check

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await provider_filter_finished.wait_call())['data']
    state = (
        utils.State.kFiltered
        if provider_check_allowed
        else utils.State.kEntered
    )
    reason = utils.Reason.kWrongProvider if provider_check_allowed else ''
    updated_etalon = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': None,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': state,
            'reason': reason,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': None,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': state,
            'reason': reason,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': None,
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': None,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': None,
        },
    }
    assert len(response) == len(updated_etalon)
    for driver in response:
        etalon = updated_etalon[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
    ]
