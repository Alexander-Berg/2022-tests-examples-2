import copy
import datetime

import pytest

import tests_dispatch_airport.utils as utils


# dbid_uuid0 queued + no_classes, nothing changed
# dbid_uuid1 new_driver -> entered
# dbid_uuid2 entered -> queued
# dbid_uuid3 queued + left_queue -> filtered
# dbid_uuid4 entered -> forbidden_by_partner
# dbid_uuid5 entered -> no_classes
# dbid_uuid6 queued -> no_classes
# dbid_uuid7 queued-> left_queue
# dbid_uuid8 queued + last_freeze -> no freeze
# dbid_uuid9 entered + no_classes -> entered
# dbid_uuid10 queued + no_classes + flag ->
# queued + left_queue + no_classes, do not send yet -> send now

NUMBER_OF_DRIVERS = 11
ALL_DRIVERS = sorted(['dbid_uuid' + str(i) for i in range(NUMBER_OF_DRIVERS)])


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize('number_of_pushes', [0, 3, None])
async def test_force_polling_order(
        taxi_dispatch_airport,
        mockserver,
        testpoint,
        load_json,
        redis_store,
        now,
        pgsql,
        taxi_config,
        number_of_pushes,
):
    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('force_polling_order')
    def force_polling(driver_id):
        return driver_id

    @testpoint('force_polling_order_next_iteration')
    def force_polling_next_iteration(driver_id):
        return driver_id

    @testpoint('send_force_bulk_push')
    def send_force_bulk_push(driver_ids):
        return driver_ids

    current_drivers = copy.deepcopy(ALL_DRIVERS)
    current_drivers.remove('dbid_uuid3')

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert sorted(request.json['driver_ids']) == current_drivers
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return {
            'drivers': [
                {
                    'car_id': 'car_id_' + str(i),
                    'categories': ['econom'],
                    'driver_id': 'uuid' + str(i),
                    'park_id': 'dbid',
                }
                for i in range(NUMBER_OF_DRIVERS)
            ],
        }

    @mockserver.json_handler(
        '/dispatch-airport-partner-protocol/service/v2/parked_drivers',
    )
    def _dapp_parked_drivers(request):
        assert 'parking_id' in request.json
        assert request.json['parking_id'] == '42'
        return {
            'drivers': [
                {'driver_id': driver_id}
                for driver_id in ALL_DRIVERS
                if driver_id != 'dbid_uuid4'
            ],
        }

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    @mockserver.json_handler('/candidates/satisfy')
    def _satisfy(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        return {
            'drivers': [
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid8',
                    'details': {'partners/qc_block': []},
                },
            ],
        }

    config = utils.custom_config(True)
    config['DISPATCH_AIRPORT_ZONES']['ekb']['partner_parking_id'] = '42'
    config['DISPATCH_AIRPORT_ZONES']['ekb']['qc_check_allowed'] = True
    config['DISPATCH_AIRPORT_FORBIDDEN_BY_PARTNER_TIMEOUTS'] = {
        '__default__': {'filter_timeout': 300},
    }
    if number_of_pushes is not None:
        config['DISPATCH_AIRPORT_FORCE' '_POLLING_ORDER_PUSH_SETTINGS'] = {
            'max_number_of_pushes': number_of_pushes,
            'ttl': 5,
        }
    else:
        number_of_pushes = 100
    taxi_config.set_values(config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid10': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    called_drivers = copy.deepcopy(ALL_DRIVERS)
    called_drivers.remove('dbid_uuid0')
    assert force_polling.times_called == 0
    assert (
        utils.get_calls_sorted(
            force_polling_next_iteration,
            len(called_drivers),
            'driver_id',
            None,
        )
        == called_drivers
    )

    etalons = load_json('etalons.json')
    utils.check_drivers_queue(pgsql['dispatch_airport'], etalons)

    for etalon in etalons:
        if etalon['driver_id'] != 'dbid_uuid0':
            etalon.pop('force_polling_order')

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # was filtered, do not force push
    called_drivers.remove('dbid_uuid3')
    assert force_polling_next_iteration.times_called == 0
    assert (
        utils.get_calls_sorted(
            force_polling, len(called_drivers), 'driver_id', None,
        )
        == called_drivers
    )
    utils.check_drivers_queue(pgsql['dispatch_airport'], etalons)

    assert send_force_bulk_push.times_called == min(1, number_of_pushes)

    if number_of_pushes >= len(called_drivers):
        assert (
            sorted(send_force_bulk_push.next_call()['driver_ids'])
            == called_drivers
        )
