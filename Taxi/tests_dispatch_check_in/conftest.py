import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from dispatch_check_in_plugins import *  # noqa: F403 F401


@pytest.fixture(name='default_mocks')
def _default_mocks(mockserver):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _mock_order_set_fields(request):
        return mockserver.make_response('', 200)


@pytest.fixture(autouse=True)
def dispatch_airport_request(mockserver):
    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': 'dbid0_uuid0',
                            'queued': '2019-06-10T13:02:20Z',
                        },
                        {
                            'dbid_uuid': 'dbid0_uuid1',
                            'queued': '2019-06-10T13:03:20Z',
                        },
                        {
                            'dbid_uuid': 'dbid0_uuid2',
                            'queued': '2019-06-10T13:04:20Z',
                        },
                    ],
                },
            ],
        }


@pytest.fixture(autouse=True)
def special_zones_request(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _localize(request):
        assert request.json['uris'] == [
            'pickup_point_uri2',
            'pickup_point_uri1',
        ]
        return {
            'results': [{'position': [10, 20]}, {'position': [37.62, 55.75]}],
        }
