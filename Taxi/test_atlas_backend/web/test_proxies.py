import datetime

from aiohttp import web
import pytest

from generated.clients import driver_route_watcher as route_watcher_client
from generated.models import tigraph_router

from atlas_backend.utils.fbs import reposition_api_make_offer
from atlas_backend.utils.fbs import reposition_offer


@pytest.mark.parametrize(
    'status, get_modes_response',
    [
        (200, {'Mode1': {'offer_only': False, 'type': 'in_area'}}),
        (401, {'code': 'Unauthorized', 'message': 'Unauthorized'}),
    ],
)
async def test_reposition_get_modes(
        web_app_client,
        atlas_blackbox_mock,
        mock_reposition_api,
        status,
        get_modes_response,
):
    @mock_reposition_api('/v1/service/modes')
    async def handle(request):
        return web.json_response(get_modes_response, status=status)

    response = await web_app_client.get('/api/reposition/settings/modes')
    assert handle.times_called == 1
    assert response.status < 500

    content = await response.json()
    if response.status == 200:
        assert not content['Mode1']['offer_only']

    elif response.status == 401:
        assert content['code'] == 'Unauthorised::RepositionApi'


MAKE_OFFER_REQUEST = {
    'driver_id': '1',
    'park_db_id': 'a',
    'mode': 'd',
    'destination': [1, 1],
    'city': 'Nowhere',
    'address': 'Lenina Street',
    'start_until': '2022-01-01T00:00:00+00:00',
    'finish_until': '2022-01-01T12:00:00+00:00',
    'image_id': '4',
    'name': 'taximeter-000',
    'description': 'test',
    'tags': ['test', 'idk'],
}

MAKE_OFFER_RESPONSE = {
    'driver_id': '1236',
    'park_db_id': '1380',
    'point_id': '1480',
}


async def test_schema_make_offer(web_context, mock_reposition_api):
    @mock_reposition_api('/v1/service/make_offer')
    def handle(request):  # pylint: disable=unused-variable
        response = reposition_offer.Response.deserialize(
            {'results': [MAKE_OFFER_RESPONSE]},
        )

        return web.Response(
            status=200,
            content_type='application/x-flatbuffers',
            body=reposition_api_make_offer.build_response(response),
        )

    request_body = reposition_offer.Request.deserialize(
        {'offers': [MAKE_OFFER_REQUEST]},
    )

    response = (
        await web_context.clients.reposition_api.v1_service_make_offer_post(
            fbs_body=reposition_api_make_offer.build_request(request_body),
        )
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'status, test_request, ext_response',
    [
        (
            200,
            {'offers': [MAKE_OFFER_REQUEST]},
            {'results': [MAKE_OFFER_RESPONSE]},
        ),
        (400, None, None),
        (400, {'offers': [MAKE_OFFER_REQUEST]}, None),
    ],
)
async def test_reposition_make_offer(
        web_app_client,
        atlas_blackbox_mock,
        mock_reposition_api,
        status,
        test_request,
        ext_response,
):
    @mock_reposition_api('/v1/service/make_offer')
    async def handle(request):
        response = reposition_offer.Response.deserialize(ext_response)

        return web.Response(
            status=status,
            content_type='application/x-flatbuffers',
            body=reposition_api_make_offer.build_response(response),
        )

    response = await web_app_client.post(
        '/api/reposition/make_offer', json=test_request,
    )

    if handle.times_called == 0:
        assert response.status == status

    else:
        assert response.status < 500

        content = await response.json()
        if response.status == 200:
            assert content['results'][0]['point_id'] == '1480'

        elif response.status == 400:
            assert content['code'] == 'BadRequest::RepositionApi'


DIAG_DRIVER_REQUEST = {'driver': {'uuid': 'a', 'dbid': 'b'}}

DIAG_DRIVER_RESPONSE = {
    'driver_id': {'uuid': 'a', 'dbid': 'b'},
    'position': [0, 0],
    'destination': [1, 1],
    'time_left': 30,
    'distance_left': 500,
    'tracking_type': 'route_tracking',
    'direction': 10,
    'route': [[0, 0], [1, 1]],
}


async def test_schema_diag_driver(web_context, mock_driver_route_watcher):
    request_body = route_watcher_client.DiagDriverPostBody.deserialize(
        DIAG_DRIVER_REQUEST,
    )

    @mock_driver_route_watcher('/diag-driver')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(DIAG_DRIVER_RESPONSE)

    response = await web_context.clients.driver_route_watcher.diag_driver_post(
        request_body,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, DIAG_DRIVER_REQUEST, DIAG_DRIVER_RESPONSE),
        (400, None, None),
        (404, DIAG_DRIVER_REQUEST, None),
    ],
)
async def test_route_watcher_diag_driver(
        web_app_client,
        atlas_blackbox_mock,
        username,
        mock_driver_route_watcher,
        status,
        ext_request,
        ext_response,
):
    @mock_driver_route_watcher('/diag-driver')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/driver-route-watcher/diag-driver', json=ext_request,
    )

    assert response.status < 500

    content = await response.json()
    if response.status == 200:
        assert content['time_left'] == 30

    elif response.status == 400:
        assert content['message'] == 'Invalid request parameters'

    elif response.status == 404:
        assert content['message'] == 'Driver not found or no drivers in query'


ROUTER_REQUEST = {'route': [[0, 0], [1, 1]]}

ROUTER_RESPONSE = {
    'summary': {'duration': 1000, 'length': 4000, 'has_closure': False},
}


async def test_schema_route(web_context, mock_tigraph_router):
    request_body = tigraph_router.RouteRequest.deserialize(ROUTER_REQUEST)

    @mock_tigraph_router('/route')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ROUTER_RESPONSE)

    response = await web_context.clients.tigraph_router.route_post(
        request_body,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, ROUTER_REQUEST, ROUTER_RESPONSE),
        (400, None, None),
        (404, ROUTER_REQUEST, {'message': 'route not found'}),
    ],
)
async def test_tigraph_route(
        web_app_client,
        atlas_blackbox_mock,
        username,
        mock_tigraph_router,
        status,
        ext_request,
        ext_response,
):
    @mock_tigraph_router('/route')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/tigraph_router/route', json=ext_request,
    )

    assert response.status < 500

    content = await response.json()
    if response.status == 200:
        assert content['summary']['duration'] == 1000

    elif response.status == 400:
        assert content['message'] == 'Empty request body'

    elif response.status == 404:
        assert content['message'] == 'route not found'


DRAW_DESC_REQUEST = {
    'from_dt': '2020-01-01T00:00:00Z',
    'to_dt': '2020-01-01T00:10:00Z',
    'draw_id': 'fapodsfiunapor',
}

DRAW_DESC_BAD_REQUEST = {
    'to_dt': '2020-01-01T00:10:00Z',
    'draw_id': 'fapodsfiunapor',
}

DRAW_DESC_DIRECT_REQUEST = {
    'from_dt': datetime.datetime(2020, 1, 1, 0, 0, 0),
    'to_dt': datetime.datetime(2020, 1, 1, 0, 10, 0),
    'draw_id': None,
}

DRAW_DESC_RESPONSE = {
    'draw_id': 'fapodsfiunapor',
    'orders': {
        'order1': {
            'candidates': {
                'Edge1': {
                    'id': '1',
                    'geo_point': [0, 0],
                    'rd': 1,
                    'rt': 1,
                    'score': 1,
                    'winner': True,
                    'winner_applied': True,
                },
            },
            'stats': {'candidates_count': 1, 'geo_point': [0, 0]},
        },
    },
    'offers': {
        'offer1': {
            'candidates': {
                'Edge1': {
                    'id': '1',
                    'geo_point': [0, 0],
                    'rd': 1,
                    'rt': 1,
                    'score': 1,
                    'winner': True,
                    'winner_applied': True,
                },
            },
            'stats': {'candidates_count': 1, 'geo_point': [0, 0]},
        },
    },
    'candidates': {
        'candidate1': {
            'orders': {
                'Edge1': {
                    'id': '1',
                    'geo_point': [0, 0],
                    'rd': 1,
                    'rt': 1,
                    'score': 1,
                    'winner': True,
                    'winner_applied': True,
                },
            },
            'offers': {
                'Edge1': {
                    'id': '1',
                    'geo_point': [0, 0],
                    'rd': 1,
                    'rt': 1,
                    'score': 1,
                    'winner': True,
                    'winner_applied': True,
                },
            },
            'stats': {'orders_offers_count': 1, 'geo_point': [0, 0]},
        },
    },
    'agg_stats': {
        'orders_offers_count': 1,
        'candidates_count': 1,
        'orders_offers_hist': {1: 1},
        'candidates_hist': {1: 1},
    },
}

DRAW_DESC_PENDING_RESPONSE = {'draw_id': 'fapodsfiunapor', 'status': 'running'}


async def test_schema_draw_desc(web_context, mock_taxi_dispatch_logs_admin):
    request_body = DRAW_DESC_DIRECT_REQUEST

    @mock_taxi_dispatch_logs_admin('/draw_desc/')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(DRAW_DESC_RESPONSE)

    response = await web_context.clients.taxi_dispatch_logs_admin.draw_desc(
        **request_body,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, DRAW_DESC_REQUEST, DRAW_DESC_RESPONSE),
        (202, DRAW_DESC_REQUEST, DRAW_DESC_PENDING_RESPONSE),
        (200, DRAW_DESC_BAD_REQUEST, None),
    ],
)
async def test_dispatch_draw_desc(
        web_app_client,
        atlas_blackbox_mock,
        username,
        mock_taxi_dispatch_logs_admin,
        status,
        ext_request,
        ext_response,
):
    @mock_taxi_dispatch_logs_admin('/draw_desc/')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/dispatch_logs_admin/draw_desc', params=ext_request,
    )

    assert response.status < 500

    content = await response.json()
    if response.status == 200:
        assert content['orders']['order1']['stats']['candidates_count'] == 1

    elif response.status == 202:
        assert content['status'] == 'running'

    elif response.status == 400:
        assert content['message'] == 'Some parameters are invalid'


COORD_CONTROL_FINE_REQUEST = {'dbid_uuid': 'id0'}
COORD_CONTROL_BAD_REQUEST = {'dbid_uuid': 'id1'}
DRIVER_TRACK_RESPONSE = {
    'track': [
        {
            'source': 'android_gps',
            'points': [
                {
                    'lat': 55.73551,
                    'lon': 37.642776,
                    'datetime': '2021-06-16T17:59:18.932000+03:00',
                },
            ],
        },
    ],
}

DRIVER_TRACK_BAD_RESPONSE = {'message': 'performer_not_found'}


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, COORD_CONTROL_FINE_REQUEST, DRIVER_TRACK_RESPONSE),
        (400, None, None),
        (404, COORD_CONTROL_BAD_REQUEST, DRIVER_TRACK_BAD_RESPONSE),
    ],
)
async def test_driver_tack(
        web_app_client,
        atlas_blackbox_mock,
        mock_coord_control,
        status,
        ext_request,
        ext_response,
):
    @mock_coord_control('/atlas/track')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/coord-control/track', json=ext_request,
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content['track'][0]['source'] == 'android_gps'

    elif response.status == 400:
        assert content['message'] == 'Empty request body'

    elif response.status == 404:
        assert content['message'] == 'performer_not_found'


# Not specified in a yaml file
LOCATION_SETTINGS_RESPONSE = {'location-settings': 'normal'}


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, COORD_CONTROL_FINE_REQUEST, LOCATION_SETTINGS_RESPONSE),
        (400, None, None),
        (404, COORD_CONTROL_BAD_REQUEST, None),
    ],
)
async def test_driver_location_settings(
        web_app_client,
        atlas_blackbox_mock,
        mock_coord_control,
        status,
        ext_request,
        ext_response,
):
    @mock_coord_control('/atlas/location-settings')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/coord-control/location-settings', json=ext_request,
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content['location-settings'] == 'normal'

    if response.status == 400:
        assert content['message'] == 'Empty request body'

    elif response.status == 404:
        assert content['message'] == ''


COORD_CONTROL_GROUP_CHANGE_RESPONSE = {
    'verified': [
        {
            'start_timestamp': '2021-06-16T17:56:11.141390+03:00',
            'primary_group': [],
        },
    ],
    'realtime': [
        {
            'start_timestamp': '2021-06-16T17:56:11.141384+03:00',
            'primary_group': [],
        },
    ],
}
GROUP_CHANGE_BAD_RESPONSE = {'message': 'performer_not_found'}


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, COORD_CONTROL_FINE_REQUEST, COORD_CONTROL_GROUP_CHANGE_RESPONSE),
        (404, COORD_CONTROL_BAD_REQUEST, GROUP_CHANGE_BAD_RESPONSE),
        (400, None, None),
    ],
)
async def test_driver_primary_group_change(
        web_app_client,
        atlas_blackbox_mock,
        mock_coord_control,
        status,
        ext_request,
        ext_response,
):
    @mock_coord_control('/atlas/primary_group_change')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/coord-control/primary_group_change', json=ext_request,
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert not content['verified'][0]['primary_group']
    elif response.status == 404:
        assert content['message'] == 'performer_not_found'
    elif response.status == 400:
        assert content['message'] == 'Empty request body'


SHORTTRACK_REQUEST = {'driver_id': '1', 'type': 'raw'}
BAD_SHORTTRACK_REQUEST = {'driver_id': 'NULL', 'type': 'raw'}


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (
            200,
            SHORTTRACK_REQUEST,
            {
                'raw': [
                    {'lat': 55.7497, 'lon': 37.62444, 'timestamp': 1636626291},
                ],
            },
        ),
        (400, None, {'message': 'Empty request body'}),
        (400, BAD_SHORTTRACK_REQUEST, {'message': 'BadRequest'}),
        (404, SHORTTRACK_REQUEST, {'message': 'There is no record...'}),
    ],
)
async def test_driver_get_shorttrack(
        web_app_client,
        atlas_blackbox_mock,
        mock_driver_trackstory,
        status,
        ext_request,
        ext_response,
) -> None:
    @mock_driver_trackstory('/shorttrack')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/driver-trackstory/shorttrack', json=ext_request,
    )

    assert response.status == status

    content = await response.json()

    if response.status == 200:
        assert content['raw'] == [
            {'lat': 55.7497, 'lon': 37.62444, 'timestamp': 1636626291},
        ]

    else:
        message = content['message']

        if response.status == 400:
            if ext_request is None:
                assert message == 'Empty request body'
            else:
                assert message == 'BadRequest'

        elif response.status == 404:
            assert message == 'There is no record...'
