from aiohttp import web
import pytest


ORDER_SEARCH_REQUEST = {
    'point': [37.62, 55.75],
    'zone_id': 'moscow',
    'limit': 10,
    'free_preferred': 5,
    'class_limits': {'econom': 5, 'comfort': 3},
    'max_distance': 10000,
}

ORDER_SEARCH__PREDICT_POSITIONS_REQUEST = {
    'point': [37.62, 55.75],
    'zone_id': 'moscow',
    'limit': 10,
    'free_preferred': 5,
    'class_limits': {'econom': 5, 'comfort': 3},
    'max_distance': 10000,
    'prediction_seconds': 10,
    'shorttrack_num_positions': 20,
}

ORDER_SEARCH_RESPONSE = {
    'candidates': [
        {
            'car_number': 'some_number',
            'classes': ['econom'],
            'uuid': 'some_uuid1',
            'dbid': 'some_dbid1',
            'license_id': 'some_license_id',
            'position': [55, 35],
            'route_info': {},
            'profile': {},
            'status': {},
            'unique_driver_id': 'some_id',
        },
        {
            'car_number': 'some_number',
            'classes': ['vip', 'uberblack'],
            'uuid': 'some_uuid2',
            'dbid': 'some_dbid2',
            'license_id': 'some_license_id',
            'position': [55, 35],
            'route_info': {},
            'profile': {},
            'status': {},
            'chain_info': {
                'destination': [55.0, 35.0],
                'left_dist': 100,
                'left_time': 10,
                'order_id': 'some_order_id',
            },
            'unique_driver_id': 'some_id',
        },
    ],
}

ORDER_SEARCH_WITH_TRACKSTORY_RESPONSE = {
    'candidates': [
        {
            'car_number': 'some_number',
            'classes': ['econom'],
            'uuid': 'some_uuid1',
            'dbid': 'some_dbid1',
            'license_id': 'some_license_id',
            'position': [55, 35],
            'route_info': {},
            'profile': {},
            'status': {},
            'unique_driver_id': 'some_id',
            'predicted_position': {
                'predictions': [{'lat': 55.5, 'lon': 35.5, 'timestamp': 123}],
            },
            'trackstory': [{'lat': 56, 'lon': 36, 'timestamp': 123}],
        },
        {
            'car_number': 'some_number',
            'classes': ['vip', 'uberblack'],
            'uuid': 'some_uuid2',
            'dbid': 'some_dbid2',
            'license_id': 'some_license_id',
            'position': [55, 35],
            'route_info': {},
            'profile': {},
            'status': {},
            'chain_info': {
                'destination': [55.0, 35.0],
                'left_dist': 100,
                'left_time': 10,
                'order_id': 'some_order_id',
            },
            'unique_driver_id': 'some_id',
            'predicted_position': {
                'predictions': [{'lat': 55.5, 'lon': 35.5, 'timestamp': 123}],
            },
            'trackstory': [{'lat': 55, 'lon': 35, 'timestamp': 123}],
        },
    ],
}

DRIVER_TRACKSTORY_RESPONSE = {
    'some_dbid2_some_uuid2': {
        'raw': [{'timestamp': 123, 'lat': 55, 'lon': 35}],
    },
    'some_dbid1_some_uuid1': {
        'raw': [{'timestamp': 123, 'lat': 56, 'lon': 36}],
    },
}

YAGA_ADJUST_PREDICT_POSITIONS_RESPONSE = {
    'predictions': [{'timestamp': 123, 'lat': 55.5, 'lon': 35.5}],
}

ORDER_SEARCH_BAD_REQUEST_RESPONSE = {'message': 'wrong request schema'}


async def test_schema_order_search(web_context, mock_candidates):
    request_body = ORDER_SEARCH_REQUEST

    @mock_candidates('/order-search')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ORDER_SEARCH_RESPONSE)

    response = await web_context.clients.candidates.order_search_post(
        request_body,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'status, ext_request, ext_response',
    [
        (200, ORDER_SEARCH_REQUEST, ORDER_SEARCH_RESPONSE),
        (400, ORDER_SEARCH_REQUEST, ORDER_SEARCH_BAD_REQUEST_RESPONSE),
        (400, {'something': 'blah'}, ORDER_SEARCH_BAD_REQUEST_RESPONSE),
    ],
)
async def test_candidates_order_search(
        web_app_client,
        atlas_blackbox_mock,
        username,
        mock_candidates,
        status,
        ext_request,
        ext_response,
):
    @mock_candidates('/order-search')
    def handle(request):  # pylint: disable=unused-variable
        return web.json_response(ext_response, status=status)

    response = await web_app_client.post(
        '/api/v1/candidates/order-search', json=ext_request,
    )

    assert response.status < 500

    content = await response.json()
    if response.status == 200:
        assert content['candidates'][1]['chain_info']['left_time'] == 10

    elif response.status == 400:
        assert content['message'] == 'wrong request schema'


async def test_candidates_order_search_with_shorttrack_predict(
        web_app_client,
        atlas_blackbox_mock,
        username,
        mock_candidates,
        mock_driver_trackstory,
        mock_yaga_adjust,
):
    @mock_candidates('/order-search')
    def handle_candidates(request):  # pylint: disable=unused-variable
        return web.json_response(ORDER_SEARCH_RESPONSE, status=200)

    @mock_driver_trackstory('/shorttracks')
    def handle_driver_trackstory(request):  # pylint: disable=unused-variable
        return web.json_response(DRIVER_TRACKSTORY_RESPONSE, status=200)

    @mock_yaga_adjust('/predict/position')
    def handle_yaga_adjust(request):  # pylint: disable=unused-variable
        return web.json_response(
            YAGA_ADJUST_PREDICT_POSITIONS_RESPONSE, status=200,
        )

    response = await web_app_client.post(
        '/api/v1/candidates/order-search',
        json=ORDER_SEARCH__PREDICT_POSITIONS_REQUEST,
    )
    assert response.status == 200

    content = await response.json()

    assert content == ORDER_SEARCH_WITH_TRACKSTORY_RESPONSE
