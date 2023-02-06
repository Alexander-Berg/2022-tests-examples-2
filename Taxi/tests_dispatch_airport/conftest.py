# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from dispatch_airport_plugins import *  # noqa: F403 F401
import pytest

import tests_dispatch_airport.utils as utils


@pytest.fixture(name='queues_needs')
def _queues_needs(mockserver, load_json, driver_categories_api):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariff(request):
        return load_json('tariff_zones.json')

    @mockserver.json_handler('/taxi-tariffs/v1/tariff/current')
    def _current_tariff(request):
        assert request.query['zone'] in ('ekb_home_zone', 'svo_home_zone')

        if request.query['zone'] == 'ekb_home_zone':
            return load_json('ekb_categories.json')

        return load_json('svo_categories.json')

    @mockserver.json_handler('/umlaas/airport_queue_size/v1')
    def _umlaas(request):
        tariff = request.query['tariff']
        airport = request.query['airport']

        assert tariff in (
            'econom',
            'business',
            'business2',
            'comfortplus',
            'vip',
        )
        assert airport in ('ekb_airport', 'svo_airport')
        assert request.query['nearest_mins'] == '30'

        estimated_times_json = load_json('airport_queue_predictions.json')
        estimated_times_airport = estimated_times_json.get(airport, {})
        estimated_times_tariff = estimated_times_airport.get(tariff, {})
        estimated_times = estimated_times_tariff.get('predicted', [])
        response = {'estimated_times': estimated_times}
        if tariff != 'vip':
            response['queue_size'] = 10
        return response


@pytest.fixture(name='default_mocks')
def _default_mocks(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_app_profiles(request):
        return {'profiles': []}

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(_):
        return {'profiles': []}

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return {'drivers': []}

    @mockserver.json_handler('/candidates/satisfy')
    def _satisfy(request):
        return {'drivers': []}

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        return {'categories': []}

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers([]),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def _driver_metrics_storage(request):
        return {'events': []}

    @mockserver.json_handler('/client-notify/v2/bulk-push')
    def _client_notify_bulk_push(request):
        return {'notification_id': ''}


@pytest.fixture(autouse=True)
async def _clear_driver_pos_processor_state(taxi_dispatch_airport):
    yield
    # driver_pos_processor component is not recreated between consecutive
    # test runs. Tracks state is cleared after each test run, so it won't
    # affect next test.
    await taxi_dispatch_airport.run_task('driver_pos_processor/clear_state')


@pytest.fixture(params=['old', 'new', 'mixed_base_old', 'mixed_base_new'])
async def mode(request, taxi_config):
    utils.set_mode_in_config(taxi_config, request.param)
    yield request.param
