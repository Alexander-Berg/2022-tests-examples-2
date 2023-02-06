import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_PSQL_FILTERED_DRIVER_TTL={
        '__default__': {
            '__default__': 1200,
            'blacklist': 500,
            'offline': 180,
            'user_cancel': 300,
        },
        'svo': {'__default__': 180, 'user_cancel': 1200},
    },
)
async def test_queue_cleanup(
        taxi_dispatch_airport, mockserver, testpoint, pgsql,
):
    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-svo')

    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    await utils.wait_certain_testpoint('svo', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid11',
        'dbid_uuid12',
        'dbid_uuid13',
        'dbid_uuid3',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid8',
        'dbid_uuid9',
    ]
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['driver_events.sql'])
@pytest.mark.parametrize('driver_events_psql_enabled', [False, True])
async def test_dispatch_airport_cleanup(
        taxi_dispatch_airport,
        pgsql,
        driver_events_psql_enabled,
        taxi_config,
        mocked_time,
):
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_DRIVER_EVENTS_PSQL_ENABLED': (
                driver_events_psql_enabled
            ),
        },
    )

    etalon = {
        ('udid0', 'old_session_id0', 'entered_on_repo'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid0',
        },
        ('udid1', 'old_session_id1', 'filtered_by_forbidden_reason'): {
            'airport_id': 'ekb',
            'driver_id': 'dbid_uuid1',
        },
    }

    # Clear only staled events
    await taxi_dispatch_airport.run_task('distlock/psql-cleaner')
    if driver_events_psql_enabled:
        del etalon[
            ('udid1', 'old_session_id1', 'filtered_by_forbidden_reason')
        ]
    driver_events = utils.get_driver_events(pgsql['dispatch_airport'])
    assert driver_events == etalon

    # Nothing changed
    mocked_time.sleep(60)
    await taxi_dispatch_airport.run_task('distlock/psql-cleaner')
    assert driver_events == etalon

    # Clear all events
    mocked_time.sleep(3600)
    await taxi_dispatch_airport.run_task('distlock/psql-cleaner')
    if driver_events_psql_enabled:
        etalon.clear()
    driver_events = utils.get_driver_events(pgsql['dispatch_airport'])
    assert driver_events == etalon
