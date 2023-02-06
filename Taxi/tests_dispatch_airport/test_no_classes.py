import datetime

import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue_no_classes.sql'])
@pytest.mark.parametrize('taximeter_tariffs_affects_queues', [True, False])
async def test_no_classes_filter_timeout(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        taxi_config,
        mocked_time,
        taximeter_tariffs_affects_queues,
        now,
        redis_store,
        load_json,
):
    config = utils.custom_config(True)
    config['DISPATCH_AIRPORT_ZONES']['ekb']['no_classes_allowed_time_sec'] = 3
    taxi_config.set_values(config)
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_TAXIMETER_TARIFFS_AFFECT_QUEUES': (
                taximeter_tariffs_affects_queues
            ),
        },
    )

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('no-classes-filter-finished')
    def candidates_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        assert sorted(request.json['driver_ids']) == [
            'dbid_uuid0',
            'dbid_uuid1',
            'dbid_uuid2',
        ]
        return {
            'drivers': [
                {
                    'car_id': 'car_id_0',
                    'classes': [],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'status': {'driver': 'free', 'taximeter': 'free'},
                    'uuid': 'uuid0',
                },
                {
                    'car_id': 'car_id_1',
                    'classes': [],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'status': {'driver': 'free', 'taximeter': 'free'},
                    'uuid': 'uuid1',
                },
                {
                    'car_id': 'car_id_2',
                    'classes': [],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'status': {'driver': 'free', 'taximeter': 'free'},
                    'uuid': 'uuid2',
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def driver_categories(request):
        assert len(request.json['drivers']) == 3
        return {
            'drivers': [
                {
                    'car_id': 'car_id_0',
                    'categories': ['comfortplus', 'econom'],
                    'driver_id': 'uuid0',
                    'park_id': 'dbid',
                },
                {
                    'car_id': 'car_id_1',
                    'categories': ['comfortplus', 'econom'],
                    'driver_id': 'uuid1',
                    'park_id': 'dbid',
                },
                {
                    'car_id': 'car_id_2',
                    'categories': ['econom'],
                    'driver_id': 'uuid2',
                    'park_id': 'dbid',
                },
            ],
        }

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid0 - stored driver: queued- > no_classes after timeout
    # dbid_uuid1 - stored driver: entered -> no_classes
    # dbid_uuid2 - new driver

    utils.publish_positions(
        redis_store,
        {
            'dbid_uuid2': {
                'position': utils.WAITING_POSITION,
                'timestamp': now + datetime.timedelta(minutes=2),
            },
        },
        now,
    )
    await merge_finished.wait_call()

    etalon = load_json('driver_state_etalon_no_classes.json')

    # first iteration - no_classes started tp should be initialized
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await candidates_filter_finished.wait_call())['data']
    utils.check_filter_result(response, etalon['timeout_started'])
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    assert driver_categories.times_called == 1

    # second iteration - not enough time passed for filtered
    mocked_time.sleep(2)
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await candidates_filter_finished.wait_call())['data']
    utils.check_filter_result(response, etalon['queued'])
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    assert driver_categories.times_called == 2

    # third iteration - filter by no classes
    mocked_time.sleep(2)
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await candidates_filter_finished.wait_call())['data']
    utils.check_filter_result(response, etalon['filtered'])
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    assert driver_categories.times_called == 3

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid2']
    assert not utils.get_driver_events(db)
