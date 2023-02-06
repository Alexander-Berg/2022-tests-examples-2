import datetime

import pytest

import tests_dispatch_airport.utils as utils


CANDIDATES_FILTER_NAME = 'candidates-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize('old_mode_enabled', [True, False])
@pytest.mark.parametrize('taximeter_tariffs_affects_queues', [True, False])
async def test_candidates_filter(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        load_json,
        taxi_config,
        old_mode_enabled,
        taximeter_tariffs_affects_queues,
):
    config = utils.custom_config(old_mode_enabled)
    config['DISPATCH_AIRPORT_ZONES']['ekb']['no_classes_allowed_time_sec'] = 0
    config['DISPATCH_AIRPORT_ZONES']['ekb'][
        'changed_tariff_allowed_time_sec'
    ] = 0
    config[
        'DISPATCH_AIRPORT_TAXIMETER_TARIFFS_AFFECT_QUEUES'
    ] = taximeter_tariffs_affects_queues
    taxi_config.set_values(config)

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(CANDIDATES_FILTER_NAME + '-finished')
    def candidates_filter_finished(data):
        return data

    @testpoint('change-tariffs-filter-finished')
    def change_tariffs_filter_finished(data):
        return data

    @testpoint('driver-mode-fetcher-finished')
    def driver_mode_fetcher_finished(data):
        return data

    @testpoint('offline-filter-finished')
    def offline_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 13
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return load_json('driver_categories.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]

        append_queued_etalon = [
            'dbid_uuid3',
            'dbid_uuid5',
            'dbid_uuid6',
            'dbid_uuid7',
            'dbid_uuid11',
            'dbid_uuid13',
        ]
        if old_mode_enabled:
            append_queued_etalon += ['dbid_uuid1']
        if not taximeter_tariffs_affects_queues:
            append_queued_etalon += ['dbid_uuid14']

        append_entered_etalon = []
        if old_mode_enabled:
            append_entered_etalon += ['dbid_uuid0', 'dbid_uuid2']

        remove_queued_etalon = ['dbid_uuid10', 'dbid_uuid12']
        if taximeter_tariffs_affects_queues:
            remove_queued_etalon += ['dbid_uuid14']

        remove_entered_etalon = ['dbid_uuid3', 'dbid_uuid5', 'dbid_uuid11']

        utils.check_airport_tags(
            append, append_queued_etalon, append_entered_etalon,
        )
        utils.check_airport_tags(
            remove, remove_queued_etalon, remove_entered_etalon,
        )
        return {}

    async def check_filter_testpoint(filter_testpoint, etalons):
        response = (await filter_testpoint.wait_call())['data']
        assert len(response) == len(etalons)
        for driver in response:
            etalon = etalons[driver['driver_id']]
            utils.check_drivers(driver, etalon)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid0 - new driver: notification zone
    # dbid_uuid1 - new driver: waiting zone
    # dbid_uuid2 - new driver: 'busy' taximeter status
    # dbid_uuid3 - stored driver: old_mode, waiting zone
    # dbid_uuid4 - new driver: empty classes
    # dbid_uuid5 - stored driver: old_mode, waiting zone
    # dbid_uuid6 - stored driver: queued
    # dbid_uuid7 - stored driver: queued, extended tariffs
    # dbid_uuid10 - stored driver: queued -> 'busy' taximeter status
    # dbid_uuid11 - stored driver: entered + offline -> online
    # dbid_uuid12 - stored driver: queued, changed tariffs
    # dbid_uuid13 - stored driver: queued, but if
    #               taximeter_tariffs_affects_queues is True then comfortplus
    #               is removed from driver classes
    # dbid_uuid14 - stored driver: queued, but if
    #               taximeter_tariffs_affects_queues is True then no_classes

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid0': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid1': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # candidates-filter check
    updated_etalons = {
        'dbid_uuid0': {
            'driver_id': 'dbid_uuid0',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['econom'],
            'taximeter_tariffs': [],
        },
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_tariffs': [],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_status': 'busy',
            'offline_started_tp': False,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus'],
            'taximeter_status': 'free',
            'taximeter_tariffs': ['comfortplus'],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': [],
            'taximeter_status': 'free',
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus'],
            'taximeter_status': 'free',
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'taximeter_status': 'free',
            'taximeter_tariffs': ['econom'],
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_status': 'free',
            'taximeter_tariffs': ['econom'],
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_status': 'busy',
            'offline_started_tp': False,
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kEntered,
            'reason': 'old_mode',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_status': 'free',
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'taximeter_status': 'free',
            'taximeter_tariffs': ['comfortplus', 'econom'],
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'taximeter_status': 'free',
            'taximeter_tariffs': ['econom'],
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'taximeter_status': 'free',
            'taximeter_tariffs': [],
        },
    }
    await check_filter_testpoint(candidates_filter_finished, updated_etalons)
    # change_tariffs
    updated_etalons['dbid_uuid0']['taximeter_tariffs'] = ['business2', 'uberx']
    updated_etalons['dbid_uuid1']['taximeter_tariffs'] = ['uberx']
    updated_etalons['dbid_uuid3']['taximeter_tariffs'] = [
        'business2',
        'comfortplus',
    ]
    updated_etalons['dbid_uuid6']['taximeter_tariffs'] = [
        'business2',
        'comfortplus',
        'econom',
    ]
    updated_etalons['dbid_uuid7']['taximeter_tariffs'] = [
        'comfortplus',
        'econom',
    ]
    if taximeter_tariffs_affects_queues:
        updated_etalons['dbid_uuid12']['classes'] = ['econom']
        updated_etalons['dbid_uuid13']['classes'] = ['econom']
        updated_etalons['dbid_uuid14']['classes'] = []
    updated_etalons['dbid_uuid12']['state'] = utils.State.kFiltered
    updated_etalons['dbid_uuid12']['reason'] = utils.Reason.kChangeTariff
    updated_etalons['dbid_uuid12']['taximeter_tariffs'] = ['econom']
    await check_filter_testpoint(
        change_tariffs_filter_finished, updated_etalons,
    )
    updated_etalons.pop('dbid_uuid12')
    # driver_mode
    await check_filter_testpoint(driver_mode_fetcher_finished, updated_etalons)
    # offline
    for driver_id in ['dbid_uuid2', 'dbid_uuid10']:
        if driver_id == 'dbid_uuid10':
            updated_etalons[driver_id]['state'] = utils.State.kFiltered
            updated_etalons[driver_id]['reason'] = utils.Reason.kQueuedOffline
        if driver_id == 'dbid_uuid2' and not old_mode_enabled:
            updated_etalons[driver_id]['state'] = utils.State.kFiltered
            updated_etalons[driver_id]['reason'] = utils.Reason.kOffline
        updated_etalons[driver_id]['offline_started_tp'] = True
    await check_filter_testpoint(offline_filter_finished, updated_etalons)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue_full(db)
    assert [driver['driver_id'] for driver in drivers] == [
        'dbid_uuid0',
        'dbid_uuid1',
        'dbid_uuid10',
        'dbid_uuid11',
        'dbid_uuid12',
        'dbid_uuid13',
        'dbid_uuid14',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
    ]
    # dbid_uuid4 and dbid_uuid14 are now filtered for no classes
    # in class_validation
    if old_mode_enabled:
        assert utils.get_state(drivers[9]['state']) == utils.State.kFiltered
        assert drivers[9]['reason'] == utils.Reason.kNoClasses
    else:
        assert utils.get_state(drivers[9]['state']) == utils.State.kFiltered
        assert drivers[9]['reason'] == utils.Reason.kFullQueue
    if taximeter_tariffs_affects_queues:
        assert utils.get_state(drivers[6]['state']) == utils.State.kFiltered
        assert drivers[6]['reason'] == utils.Reason.kNoClasses
    else:
        assert utils.get_state(drivers[6]['state']) == utils.State.kQueued
        assert drivers[6]['reason'] == utils.Reason.kOldMode
    # class_queued is now set in class_validation
    class_queued = drivers[11]['class_queued']
    assert class_queued['econom']
    assert class_queued['comfortplus']
    assert class_queued['comfortplus'] > class_queued['econom']
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue_no_classes.sql'])
async def test_candidates_filter_changed_tariffs_timeout(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        taxi_config,
        mocked_time,
):
    config = utils.custom_config(False)
    config['DISPATCH_AIRPORT_ZONES']['ekb'][
        'changed_tariff_allowed_time_sec'
    ] = 3
    taxi_config.set_values(config)

    @testpoint('change-tariffs-filter-finished')
    def change_tariffs_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        return {
            'drivers': [
                {
                    'car_id': 'car_id_0',
                    'classes': ['comfortplus', 'econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'status': {'driver': 'free', 'taximeter': 'free'},
                    'uuid': 'uuid0',
                },
                {
                    'car_id': 'car_id_1',
                    'classes': ['comfortplus', 'econom'],
                    'dbid': 'dbid',
                    'position': [0, 0],
                    'status': {'driver': 'free', 'taximeter': 'free'},
                    'uuid': 'uuid1',
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 2
        return {
            'drivers': [
                {
                    'car_id': 'car_id_0',
                    'categories': ['comfortplus'],
                    'driver_id': 'uuid0',
                    'park_id': 'dbid',
                },
                {
                    'car_id': 'car_id_1',
                    'categories': ['comfortplus'],
                    'driver_id': 'uuid1',
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
    # dbid_uuid0 - stored driver: queued -> changed_tariffs after timeout
    # dbid_uuid1 - stored driver: entered -> queued (don't filter entered
    #              drivers if they change tariffs)

    queued_etalon_dbid_uuid0 = {
        'driver_id': 'dbid_uuid0',
        'state': utils.State.kQueued,
        'reason': utils.Reason.kOldMode,
        'airport': 'ekb',
        'old_mode_enabled': False,
        'areas': [1, 2],
        'classes': ['comfortplus', 'econom'],
        'taximeter_tariffs': ['comfortplus', 'econom'],
    }

    filtered_etalon_dbid_uuid0 = {
        'driver_id': 'dbid_uuid0',
        'state': utils.State.kFiltered,
        'reason': utils.Reason.kChangeTariff,
        'airport': 'ekb',
        'old_mode_enabled': False,
        'areas': [1, 2],
        'classes': ['comfortplus', 'econom'],
        'taximeter_tariffs': ['comfortplus'],
    }

    entered_etalon_dbid_uuid1 = {
        'driver_id': 'dbid_uuid1',
        'state': utils.State.kEntered,
        'reason': utils.Reason.kOldMode,
        'airport': 'ekb',
        'old_mode_enabled': False,
        'areas': [1, 2],
        'classes': ['comfortplus', 'econom'],
        'taximeter_tariffs': ['comfortplus'],
    }

    queued_etalon_dbid_uuid1 = {
        'driver_id': 'dbid_uuid1',
        'state': utils.State.kQueued,
        'reason': utils.Reason.kOldMode,
        'airport': 'ekb',
        'old_mode_enabled': False,
        'areas': [1, 2],
        'classes': ['comfortplus', 'econom'],
        'taximeter_tariffs': ['comfortplus'],
    }

    # first iteration - changed_tariff started tp should be initialized
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await change_tariffs_filter_finished.wait_call())['data']
    utils.check_filter_result(
        response,
        {
            'dbid_uuid0': queued_etalon_dbid_uuid0,
            'dbid_uuid1': entered_etalon_dbid_uuid1,
        },
    )
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # second iteration - not enough time passed for filtered
    mocked_time.sleep(2)
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await change_tariffs_filter_finished.wait_call())['data']
    utils.check_filter_result(
        response,
        {
            'dbid_uuid0': queued_etalon_dbid_uuid0,
            'dbid_uuid1': queued_etalon_dbid_uuid1,
        },
    )
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # thirt iteration - filter by changed tariffs
    mocked_time.sleep(2)
    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await change_tariffs_filter_finished.wait_call())['data']
    utils.check_filter_result(
        response,
        {
            'dbid_uuid0': filtered_etalon_dbid_uuid0,
            'dbid_uuid1': queued_etalon_dbid_uuid1,
        },
    )
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid0', 'dbid_uuid1']
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['driver_mode_drivers_queue.sql'])
@pytest.mark.parametrize(
    'mixed_mode_enabled, drivers_allowed, allowed_drivers_config',
    [
        # allowed_for_all in ekb in switch_settings
        (
            True,
            True,
            {
                'allowed_drivers': [],
                'enabled': True,
                'airport_switch_settings': {'ekb': {'allowed_for_all': True}},
            },
        ),
        # driver is in allowed_drivers in switch_settings in ekb
        (
            True,
            True,
            {
                'allowed_drivers': [],
                'enabled': True,
                'airport_switch_settings': {
                    'ekb': {
                        'allowed_for_all': False,
                        'allowed_drivers': [
                            'dbid_uuid0',
                            'dbid_uuid1',
                            'dbid_uuid2',
                            'dbid_uuid3',
                            'dbid_uuid4',
                            'dbid_uuid5',
                            'dbid_uuid6',
                            'dbid_uuid7',
                            'dbid_uuid8',
                            'dbid_uuid9',
                            'dbid_uuid10',
                        ],
                    },
                },
            },
        ),
        # no switch_settings in ekb, default is used, filtration not enabled
        (
            True,
            True,
            {
                'allowed_drivers': [],
                'enabled': False,
                'airport_switch_settings': {},
            },
        ),
        # driver is in allowed_drivers in default
        (
            True,
            True,
            {
                'allowed_drivers': [
                    'dbid_uuid0',
                    'dbid_uuid1',
                    'dbid_uuid2',
                    'dbid_uuid3',
                    'dbid_uuid4',
                    'dbid_uuid5',
                    'dbid_uuid6',
                    'dbid_uuid7',
                    'dbid_uuid8',
                    'dbid_uuid9',
                    'dbid_uuid10',
                ],
                'enabled': True,
            },
        ),
        # switch settings exist for ekb, drivers are not allowed
        (
            True,
            False,
            {
                'allowed_drivers': [],
                'enabled': False,
                'airport_switch_settings': {'ekb': {'allowed_for_all': False}},
            },
        ),
        # no switch settings for ekb, global filtration enabled
        (True, False, {'allowed_drivers': [], 'enabled': True}),
        # mixed mode is not set for ekb in DISPATCH_AIRPORT_ZONES
        (False, True, {'allowed_drivers': [], 'enabled': False}),
    ],
)
async def test_driver_mode(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        taxi_config,
        load_json,
        now,
        redis_store,
        mixed_mode_enabled,
        drivers_allowed,
        allowed_drivers_config,
):
    zones = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones['ekb']['old_mode_enabled'] = True
    zones['ekb']['mixed_mode_enabled'] = mixed_mode_enabled
    zones['ekb']['whitelist_classes']['comfortplus']['old_mode_tariff'] = False
    taxi_config.set_values({'DISPATCH_AIRPORT_ZONES': zones})
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_MIXED_MODE_ALLOWED_DRIVERS': (
                allowed_drivers_config
            ),
        },
    )

    mixed_mode_works = mixed_mode_enabled and drivers_allowed

    number_of_drivers = 11
    all_drivers = sorted(
        ['dbid_uuid' + str(i) for i in range(number_of_drivers)],
    )

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @testpoint('reset_mode')
    def reset_mode(driver_id):
        return driver_id

    @testpoint('set_base_mode')
    def set_base_mode(driver_id):
        return driver_id

    @testpoint('set_old_mode')
    def set_old_mode(driver_id):
        return driver_id

    @testpoint('set_new_mode')
    def set_new_mode(driver_id):
        return driver_id

    @testpoint('set_mixed_mode')
    def set_mixed_mode(driver_id):
        return driver_id

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == number_of_drivers
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('driver_mode_candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == number_of_drivers
        return load_json('driver_mode_categories.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    # transitions (resulting mixed mode becomes base if not mixed_mode_works)
    # dbid_uuid0 - entered, no mode -> base mode (no tariffs)
    # dbid_uuid1 - no state, no mode -> old_mode
    # dbid_uuid2 - entered, no_mode -> new_mode
    # dbid_uuid3 - queued, no_mode -> mixed_mode
    # dbid_uuid4 - entered, old_mode -> mixed_mode
    # dbid_uuid5 - queued, old_mode -> old_mode
    # (dca returns new mode tariff, but not old_mode)
    # mode doesn't change because for queued tariffs can not be reduced
    # dbid_uuid6 - queued, new_mode -> mixed_mode
    # dbid_uuid7 - entered, new_mode -> mixed_mode, while no new mode tariff
    # mixed mode is preserved
    # dbid_uuid8 - entered, mixed_mode -> mixed_mode,
    # while only old_mode tariffs
    # dbid_uuid9 - entered, mixed_mode -> mixed_mode,
    # while only new_mode tariffs
    # dbid_uuid10 - entered, mixed_mode -> mixed_mode, while no tariffs

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # check db state
    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue_full(db)
    drivers_old_mode = [
        driver['driver_id']
        for driver in drivers
        if driver['driver_mode'] == 'old'
    ]
    drivers_new_mode = [
        driver['driver_id']
        for driver in drivers
        if driver['driver_mode'] == 'new'
    ]
    drivers_mixed_mode = [
        driver['driver_id']
        for driver in drivers
        if driver['driver_mode'] == 'mixed'
    ]

    if mixed_mode_works:
        assert drivers_old_mode == ['dbid_uuid0', 'dbid_uuid1', 'dbid_uuid5']
        assert drivers_new_mode == ['dbid_uuid2']
        assert drivers_mixed_mode == sorted(
            ['dbid_uuid' + str(i) for i in range(3, 11) if i != 5],
        )
    else:
        assert drivers_old_mode == all_drivers
        assert drivers_new_mode == []
        assert drivers_mixed_mode == []

    # check set mode
    if not mixed_mode_works:
        assert (
            utils.get_calls_sorted(
                reset_mode, number_of_drivers, 'driver_id', None,
            )
            == all_drivers
        )
        assert set_base_mode.times_called == 0
        assert set_old_mode.times_called == 0
        assert set_new_mode.times_called == 0
    else:
        assert reset_mode.times_called == 0
        assert utils.get_calls_sorted(set_base_mode, 1, 'driver_id', None) == [
            'dbid_uuid0',
        ]
        assert utils.get_calls_sorted(set_old_mode, 2, 'driver_id', None) == [
            'dbid_uuid1',
            'dbid_uuid5',
        ]
        assert utils.get_calls_sorted(set_new_mode, 1, 'driver_id', None) == [
            'dbid_uuid2',
        ]
        assert utils.get_calls_sorted(
            set_mixed_mode, 4, 'driver_id', None,
        ) == sorted(['dbid_uuid' + str(i) for i in range(3, 8) if i != 5])
