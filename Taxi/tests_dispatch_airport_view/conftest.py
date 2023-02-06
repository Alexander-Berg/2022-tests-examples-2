# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

from dispatch_airport_view_plugins import *  # noqa: F403 F401

import tests_dispatch_airport_view.utils as utils


@pytest.fixture(name='base_mocks')
def _base_mocks(mockserver, load_json):
    @mockserver.json_handler('/dispatch-airport/v1/pins_info')
    def _pins_info(_):
        return {
            'ekb': [
                {'allowed_class': 'econom', 'expected_wait_time': 3000},
                {'allowed_class': 'comfortplus', 'expected_wait_time': 1000},
                {'allowed_class': 'business'},
            ],
            'kamenskuralsky': [
                {'allowed_class': 'econom', 'expected_wait_time': 1000},
            ],
        }

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        assert set(request.json['projection']) == set({'data.orders_provider'})
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        # check no airport zones drivers in request
        if request.json['zone_id'] == 'ekb_home_zone':
            assert sorted(request.json['driver_ids']) == [
                'dbid_uuid0',
                'dbid_uuid1',
                'dbid_uuid2',
                'dbid_uuid3',
                'dbid_uuid4',
                'dbid_uuid7',
                'dbid_uuid8',
            ]
            return load_json('ekb_candidates.json')
        if request.json['zone_id'] == 'kamenskuralsky_home_zone':
            assert sorted(request.json['driver_ids']) == [
                'dbid_uuid6',
                'dbid_uuid7',
                'dbid_uuid8',
                'dbid_uuid9',
            ]
            return load_json('kamenskuralsky_candidates.json')
        return {'drivers': []}

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition_api(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() == b'kamenskuralsky'

        drivers = [{'dbid': 'dbid', 'uuid': 'uuid7'}]
        return mockserver.make_response(
            response=utils.generate_reposition_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/v1/service/airport_queue/get_drivers_en_route',
    )
    def _reposition_api_drivers_en_route(request):
        return {}

    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        return {'notification_id': ''}

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def _da_reposition_availability(request):
        return {'allowed': [], 'forbidden': []}


@pytest.fixture(params=['old', 'new', 'mixed_base_old', 'mixed_base_new'])
async def mode(request, taxi_config):
    utils.set_mode_in_config(taxi_config, request.param)
    yield request.param
