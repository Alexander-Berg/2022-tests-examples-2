import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.now('2021-01-01T10:15:00+00:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_FILTERED_DRIVERS_PROCESSING_SETTINGS={
        'enabled': True,
        'excluded_reasons': ['wrong_client'],
    },
)
async def test_filtered_drivers_processing(
        taxi_dispatch_airport,
        mockserver,
        testpoint,
        load_json,
        mocked_time,
        pgsql,
        now,
):
    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert sorted(request.json['driver_ids']) == [
            'dbid_uuid0',
            'dbid_uuid2',
        ]
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # dbid_uuid0: filtered_driver, candidates info should be updated
    # dbid_uuid1: filtered_driver, skipped by excluded reason
    # dbid_uuid2: filtered driver, no new info from candidates

    start_now = mocked_time.now()
    mocked_time.sleep(1)

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    etalons = [
        {
            'airport': 'ekb',
            'areas': ['main', 'notification', 'waiting'],
            'classes': [],
            'driver_id': 'dbid_uuid0',
            'old_mode_enabled': True,
            'reason': 'offline',
            'state': 'filtered',
            'taximeter_tariffs': ['econom'],
            'taximeter_status': 'new_taximeter_status',
            'driver_very_busy_status': 'new_driver_status',
            'updated': mocked_time.now(),
            'filtered_tp': start_now,
        },
        {
            'airport': 'ekb',
            'areas': ['main', 'notification', 'waiting'],
            'classes': [],
            'driver_id': 'dbid_uuid1',
            'old_mode_enabled': True,
            'reason': 'wrong_client',
            'state': 'filtered',
            'taximeter_tariffs': ['econom'],
            'taximeter_status': 'off',
            'driver_very_busy_status': 'verybusy',
            'updated': start_now,
            'filtered_tp': start_now,
        },
        {
            'airport': 'ekb',
            'areas': ['main', 'notification', 'waiting'],
            'classes': [],
            'driver_id': 'dbid_uuid2',
            'old_mode_enabled': True,
            'reason': 'offline',
            'state': 'filtered',
            'taximeter_tariffs': ['econom'],
            'taximeter_status': 'off',
            'driver_very_busy_status': 'verybusy',
            'updated': mocked_time.now(),
            'filtered_tp': start_now,
        },
    ]
    utils.check_drivers_queue(pgsql['dispatch_airport'], etalons)
