# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=import-only-modules
import json

from geobus_tools.geobus import geobus_publisher_extender  # noqa: F401 C5521
import pytest

from driver_route_responder_plugins import *  # noqa: F403 F401

# pylint: disable=redefined-outer-name
@pytest.fixture
def driver_route_responder_adv(
        taxi_driver_route_responder, geobus_publisher_extender,  # noqa: F811
):
    return geobus_publisher_extender(taxi_driver_route_responder)


@pytest.fixture(autouse=True)
def contractor_transport_request(mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '123456_4':
            return {'contractors_transport': [], 'cursor': '1234567_4'}
        data = {
            'contractors_transport': [
                {
                    'contractor_id': 'dbid_uuidpedestrian',
                    'is_deleted': False,
                    'revision': '1234567_2',
                    'transport_active': {'type': 'pedestrian'},
                },
                {
                    'contractor_id': 'park3_driver3',
                    'is_deleted': False,
                    'revision': '1234567_3',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
                {
                    'contractor_id': 'park4_driver4',
                    'is_deleted': False,
                    'revision': '1234567_4',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car4'},
                },
            ],
            'cursor': '1234567_4',
        }
        return mockserver.make_response(response=json.dumps(data))
