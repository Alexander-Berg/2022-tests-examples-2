import pytest

import tests_dispatch_airport.utils as utils


CANDIDATES_FILTER_NAME = 'candidates-filter'
ALL_DRIVERS = ['dbid_uuid10', 'dbid_uuid11']
NUMBER_OF_DRIVERS = len(ALL_DRIVERS)


def _check_response(
        response,
        is_offline,
        queued_removed_expected,
        entered_removed_expected,
        taximeter_status_expected,
        old_mode_enabled,
):
    etalons = {
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': (
                utils.State.kFiltered
                if queued_removed_expected
                else utils.State.kQueued
            ),
            'reason': (
                utils.Reason.kQueuedOffline
                if queued_removed_expected
                else utils.Reason.kOnReposition
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_status': taximeter_status_expected,
            'offline_started_tp': is_offline,
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': (
                utils.State.kFiltered
                if entered_removed_expected
                else utils.State.kEntered
            ),
            'reason': (
                utils.Reason.kOffline
                if entered_removed_expected
                else utils.Reason.kOnReposition
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['econom'],
            'taximeter_status': taximeter_status_expected,
            'offline_started_tp': is_offline,
        },
    }

    assert len(response) == len(etalons)
    for driver in response:
        etalon = etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)


def _process_tags(request, queued_removed_expected, entered_removed_expected):
    tag_category_queued = 'remove' if queued_removed_expected else 'append'
    tag_category_entered = 'remove' if entered_removed_expected else 'append'
    if tag_category_queued == tag_category_entered:
        for tags_change in request.json[tag_category_queued]:
            utils.check_airport_tags(
                tags_change, ('dbid_uuid10',), ('dbid_uuid11',),
            )
    else:
        utils.check_airport_tags(
            request.json[tag_category_queued][0], ('dbid_uuid10',),
        )
        utils.check_airport_tags(
            request.json[tag_category_entered][0], (), ('dbid_uuid11',),
        )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize('old_mode_enabled', [True, False])
async def test_candidates_filter_by_timeout(
        taxi_dispatch_airport,
        testpoint,
        mockserver,
        load_json,
        taxi_config,
        mocked_time,
        old_mode_enabled,
):
    custom_config = utils.custom_config(old_mode_enabled=old_mode_enabled)
    custom_config['DISPATCH_AIRPORT_ZONES']['ekb'][
        'offline_allowed_time_sec'
    ] = 10
    taxi_config.set_values(custom_config)

    @testpoint('offline-filter-finished')
    def offline_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == NUMBER_OF_DRIVERS
        assert sorted(request.json['driver_ids']) == ALL_DRIVERS
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return load_json('driver_categories.json')

    removed_expected = False

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        _process_tags(
            request,
            removed_expected,
            removed_expected and not old_mode_enabled,
        )
        return {}

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        drivers = [
            {'dbid': 'dbid', 'uuid': 'uuid10', 'airport_id': 'ekb'},
            {'dbid': 'dbid', 'uuid': 'uuid11', 'airport_id': 'ekb'},
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    async def update_iteration(
            is_offline, old_mode_enabled, taximeter_status_expected='busy',
    ):
        await taxi_dispatch_airport.run_task(
            'distlock/queue-update-scheduler-ekb',
        )

        response = (await offline_filter_finished.wait_call())['data']
        _check_response(
            response,
            is_offline,
            removed_expected,
            removed_expected and not old_mode_enabled,
            taximeter_status_expected,
            old_mode_enabled,
        )
        await _tags.wait_call()
        await utils.wait_certain_testpoint('ekb', queue_update_finished)

        await taxi_dispatch_airport.invalidate_caches()

    # dbid_uuid10 - queued driver
    # dbid_uuid11 - entered driver

    # iteration 1 - driver becomes offline
    removed_expected = False
    await update_iteration(is_offline=True, old_mode_enabled=old_mode_enabled)

    # iteration 2 - driver still offline, but timeout is not reached
    removed_expected = False
    mocked_time.sleep(5)
    await update_iteration(is_offline=True, old_mode_enabled=old_mode_enabled)

    # iteration 3 - kick
    removed_expected = True
    mocked_time.sleep(6)
    await update_iteration(is_offline=True, old_mode_enabled=old_mode_enabled)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize('old_mode_enabled', [True, False])
async def test_candidates_filter_by_timeout_total_time(
        taxi_dispatch_airport,
        testpoint,
        mockserver,
        load_json,
        taxi_config,
        mocked_time,
        old_mode_enabled,
):
    custom_config = utils.custom_config(old_mode_enabled=old_mode_enabled)
    custom_config['DISPATCH_AIRPORT_ZONES']['ekb'][
        'offline_allowed_time_sec'
    ] = 10
    taxi_config.set_values(custom_config)

    @testpoint('offline-filter-finished')
    def offline_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    is_offline = True

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == NUMBER_OF_DRIVERS
        assert sorted(request.json['driver_ids']) == ALL_DRIVERS
        assert request.json['zone_id'] == 'ekb_home_zone'
        response = load_json('candidates.json')
        if not is_offline:
            for driver in response['drivers']:
                driver['status'] = {'driver': 'free', 'taximeter': 'free'}
        return response

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return load_json('driver_categories.json')

    removed_expected = False

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        _process_tags(request, removed_expected, False)
        return {}

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        drivers = [
            {'dbid': 'dbid', 'uuid': 'uuid10', 'airport_id': 'ekb'},
            {'dbid': 'dbid', 'uuid': 'uuid11', 'airport_id': 'ekb'},
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    async def update_iteration(
            is_offline, old_mode_enabled, taximeter_status_expected='busy',
    ):
        await taxi_dispatch_airport.run_task(
            'distlock/queue-update-scheduler-ekb',
        )

        response = (await offline_filter_finished.wait_call())['data']
        _check_response(
            response,
            is_offline,
            removed_expected,
            False,
            taximeter_status_expected,
            old_mode_enabled,
        )
        await _tags.wait_call()
        await utils.wait_certain_testpoint('ekb', queue_update_finished)

        await taxi_dispatch_airport.invalidate_caches()

    # iteration 1 - driver becomes offline
    removed_expected = False
    is_offline = True
    await update_iteration(is_offline, old_mode_enabled=old_mode_enabled)

    # iteration 2 - driver becomes online
    removed_expected = False
    is_offline = False
    mocked_time.sleep(5)
    await update_iteration(
        is_offline,
        old_mode_enabled=old_mode_enabled,
        taximeter_status_expected='free',
    )

    # iteration 3 - driver becomes offline, but not kicked
    removed_expected = False
    is_offline = True
    mocked_time.sleep(5)
    await update_iteration(is_offline, old_mode_enabled=old_mode_enabled)

    # iteration 4 - driver still offline, but timeout is not reached
    removed_expected = False
    is_offline = True
    mocked_time.sleep(4)
    await update_iteration(is_offline, old_mode_enabled=old_mode_enabled)

    # iteration 5 - kick
    removed_expected = True
    is_offline = True
    mocked_time.sleep(2)
    await update_iteration(is_offline, old_mode_enabled=old_mode_enabled)
