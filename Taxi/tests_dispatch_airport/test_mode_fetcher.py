import datetime

import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.experiments3(
    filename='experiments3_dispatch_airport_new_mode_enabled.json',
)
@pytest.mark.parametrize('old_mode_enabled', [True, False])
async def test_mode_fetcher(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        taxi_config,
        old_mode_enabled,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('mode-fetcher-finished')
    def mode_fetcher_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    custom_config = utils.custom_config(old_mode_enabled=old_mode_enabled)
    taxi_config.set_values(custom_config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - driver is allowed with experiment [new_mode_enabled=True]
    # dbid_uuid2 - driver is allowed with experiment [new_mode_enabled=False]
    # dbid_uuid3 - driver is not allowed with experiment [fallback to config]

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
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await mode_fetcher_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': False,
            'areas': [2],
            'classes': [],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [2],
            'classes': [],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': [],
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1', 'dbid_uuid2', 'dbid_uuid3']
    assert not utils.get_driver_events(db)
