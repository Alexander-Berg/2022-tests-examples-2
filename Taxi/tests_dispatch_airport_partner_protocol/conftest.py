import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from dispatch_airport_partner_protocol_plugins import *  # noqa: F403 F401

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.fixture(autouse=True)
async def _clear_tracks_state(taxi_dispatch_airport_partner_protocol):
    yield
    # driver_pos_processor component is not recreated between consecutive
    # test runs. Tracks state is cleared after each test run, so it won't
    # affect next test.
    await taxi_dispatch_airport_partner_protocol.run_task(
        'driver_pos_processor/clear_tracks_state',
    )


@pytest.fixture(autouse=True)
async def _clear_merged_drivers(taxi_dispatch_airport_partner_protocol):
    yield
    # driver_pos_processor component is not recreated between consecutive
    # test runs. Merged drivers is cleared after each test run, so it won't
    # affect next test.
    await taxi_dispatch_airport_partner_protocol.run_task(
        'driver_pos_processor/clear_merged_drivers',
    )


@pytest.fixture(autouse=True)
async def _clear_list_cars(taxi_dispatch_airport_partner_protocol):
    yield
    # list_cars component is not recreated between consecutive
    # test runs. This fixture clears state after each test run, so it won't
    # affect next test.
    await taxi_dispatch_airport_partner_protocol.run_task(
        'list_cars/clear_state',
    )


@pytest.fixture(name='default_mocks')
def _default_mocks(mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        return utils.form_driver_profile_response(
            request, load_json('driver_profiles.json'),
        )

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _fleet_vehicles(request):
        return []

    @mockserver.json_handler(
        '/driver-diagnostics/internal/'
        'driver-diagnostics/v1/common/restrictions',
    )
    def _driver_diagnostics(request):
        return []

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status(request):
        return []

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _unique_drivers(request):
        return []

    @mockserver.json_handler('/dispatch-airport/v1/partner_drivers_info')
    def _partners_drivers_info(request):
        return []

    @mockserver.json_handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_info(request):
        return []
