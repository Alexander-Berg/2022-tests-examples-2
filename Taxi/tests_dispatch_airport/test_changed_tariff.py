import pytest

import tests_dispatch_airport.utils as utils


CANDIDATES_FILTER_NAME = 'candidates-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_IGNORE_NEVER_AVAILABLE_TARIFFS_FOR_CHANGE_TARIFF_FILTER=True,  # noqa: E501
)
async def test_changed_tariff_ignore_never_available_tariffs(
        taxi_dispatch_airport, testpoint, mockserver, load_json, taxi_config,
):
    config = utils.custom_config(True)
    config['DISPATCH_AIRPORT_ZONES']['ekb'][
        'changed_tariff_allowed_time_sec'
    ] = 0
    taxi_config.set_values(config)

    @testpoint('change-tariffs-filter-finished')
    def change_tariffs_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 2
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return load_json('driver_categories.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    etalons = {
        'dbid_uuid0': {
            'driver_id': 'dbid_uuid0',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kChangeTariff,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'taximeter_tariffs': ['econom'],
            'ever_available_classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'old_mode_enabled': True,
            'areas': [1, 2],
            'classes': ['econom'],
            'taximeter_tariffs': ['econom'],
            'ever_available_classes': ['econom'],
        },
    }

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await change_tariffs_filter_finished.wait_call())['data']

    utils.check_filter_result(response, etalons)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
