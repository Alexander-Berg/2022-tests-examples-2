# root conftest for service contractor-orders-polling
# pylint: disable=W0612, wrong-import-order, import-error
from fbs.models.etag_cache import Response
import flatbuffers
import pytest

import driver_status_helpers

pytest_plugins = ['contractor_orders_polling_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def driver_statuses_mock(mockserver, load_json):
    @mockserver.handler('/driver-status/v2/statuses/updates')
    def _mock_driver_statuses(request):
        result = driver_status_helpers.make_driver_status_response(
            {
                'revision': 10000,
                'items': [
                    {
                        'park_id': 'park_1',
                        'driver_id': 'driver_is_online',
                        'status': 'online',
                        'updated_ts': 100,
                    },
                    {
                        'park_id': 'park_1',
                        'driver_id': 'driver_is_busy',
                        'status': 'busy',
                        'updated_ts': 101,
                    },
                    {
                        'park_id': 'park_1',
                        'driver_id': 'driver_is_offline',
                        'status': 'offline',
                        'updated_ts': 102,
                    },
                ],
            },
        )

        return mockserver.make_response(
            response=result,
            headers={'Content-Type': 'application/flatbuffer'},
            status=200,
        )


@pytest.fixture(name='location_settings_empty_cache', autouse=True)
def _location_settings_empty_cache(mockserver):
    def _make_repsonse():
        builder = flatbuffers.Builder(0)
        Response.ResponseStart(builder)
        response = Response.ResponseEnd(builder)
        builder.Finish(response)
        return bytes(builder.Output())

    @mockserver.handler('coord-control/etag-cache/full')
    async def etag_cache_full(request):
        return mockserver.make_response(
            _make_repsonse(),
            status=200,
            content_type='application/flatbuffer',
        )

    @mockserver.handler('coord-control/etag-cache/incremental')
    async def etag_cache_incremental(request):
        return mockserver.make_response(
            _make_repsonse(),
            status=200,
            content_type='application/flatbuffer',
        )


@pytest.fixture(name='airport_queues_cache', autouse=True)
def _airport_queues_cache(mockserver):
    @mockserver.json_handler('dispatch-airport/v1/info/drivers')
    async def etag_cache_full(request):
        return {
            'driver_infos': [
                {
                    'dbid_uuid': '999_888',
                    'active_zone': {
                        'zone_info': {
                            'icon_id': 'airport',
                            'zone_name': 'ufa_airport_waiting',
                            'queue_title': {
                                'key': 'dispatch_airport.error.driver_kick',
                            },
                            'airport_title': {
                                'key': (
                                    'dispatch_airport.info.airport_title_ufa'
                                ),
                            },
                        },
                        'queues_infos': [],
                    },
                    'state': 'out',
                    'dialogs': [
                        {
                            'text': {'key': 'dispatch_airport.error.gps'},
                            'dialog_id': 'leave_queue',
                        },
                    ],
                    'transitions': [
                        {
                            'from': 'in',
                            'to': 'out',
                            'dialog_id': 'leave_queue',
                        },
                        {'from': 'near', 'to': 'out', 'dialog_id': 'l'},
                    ],
                },
            ],
        }


@pytest.fixture(name='dispatch_airport_view_empty_cache', autouse=True)
def _dispatch_airport_view_empty_cache(mockserver):
    @mockserver.json_handler('/dispatch-airport-view/v1/etag-cache/full')
    def full(request):
        return {'current_chunk': 0, 'total_chunks': 1, 'etags': []}

    @mockserver.json_handler(
        '/dispatch-airport-view/v1/etag-cache/incremental',
    )
    def incremental(request):
        return {'etags': []}


@pytest.fixture(name='dispatch_airport_view_preview', autouse=True)
def _dispatch_airport_view_preview(mockserver):
    @mockserver.json_handler('/dispatch-airport-view/v1/preview')
    def preview(request):
        return {'previews': [], 'etag': 0}
