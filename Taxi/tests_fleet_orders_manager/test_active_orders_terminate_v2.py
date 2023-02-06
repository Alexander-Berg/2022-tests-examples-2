import bson
import pytest


ORDER_CORE_FIELDS = {
    'fields': [
        'candidates.driver_id',
        'candidates.alias_id',
        'candidates.db_id',
        'order.request.white_label_requirements',
        'order.user_id',
        'performer',
        'status',
    ],
}

DOCUMENT_DATA = {
    'document': {
        'processing': {'version': 20},
        '_id': 'd2651f7dfa4bcf16a5be8906cae7a4e8',
        'order': {
            'version': 10,
            'request': {'dispatch_type': 'forced_performer'},
            'user_id': 'user_id',
        },
        'candidates': [
            {
                'alias_id': 'order_alias_id',
                'db_id': 'park_id_2',
                'driver_id': 'park_driver_id1',
            },
        ],
        'performer': {'candidate_index': 0, 'alias_id': 'order4_alias'},
        'status': 'assigned',
    },
    'revision': {'order.version': 10, 'processing.version': 20},
}


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-Login': 'user_login',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }

    return headers


@pytest.mark.parametrize(
    (
        'endpoint',
        'params',
        'park_id',
        'body',
        'order_core_status',
        'app_api_request',
        'app_api_response',
    ),
    [
        (
            '/fleet/fleet-orders-manager/v2/active-orders/cancellation',
            {'order_id': 'order4'},
            'park_id_2',
            {},
            'assigned',
            {
                'park_id': 'park_id_2',
                'driver_profile_id': 'driver_id1',
                'setcar_id': 'order4_alias',
                'should_notify': True,
                'origin': 'yandex_dispatch',
            },
            {'status': 'cancelled'},
        ),
        (
            '/fleet/fleet-orders-manager/v2/active-orders/cancellation',
            {'order_id': 'order4'},
            'park_id',
            {},
            'pending',
            {},
            {'status': 'cancelled'},
        ),
        (
            '/fleet/fleet-orders-manager/v2/active-orders/completion-by-fix',
            {'order_id': 'order4'},
            'park_id_2',
            {},
            'assigned',
            {
                'park_id': 'park_id_2',
                'driver_profile_id': 'driver_id1',
                'setcar_id': 'order4_alias',
                'should_notify': True,
                'origin': 'yandex_dispatch',
                'dispatch_selected_price': 'fixed',
            },
            {'status': 'complete'},
        ),
        (
            '/fleet/fleet-orders-manager/v2/active-orders/'
            'completion-by-taximeter',
            {'order_id': 'order4'},
            'park_id_2',
            {},
            'assigned',
            {
                'park_id': 'park_id_2',
                'driver_profile_id': 'driver_id1',
                'setcar_id': 'order4_alias',
                'should_notify': True,
                'origin': 'yandex_dispatch',
                'dispatch_selected_price': 'taximeter',
            },
            {'status': 'complete'},
        ),
    ],
)
async def test_terminate_handlers(
        taxi_fleet_orders_manager,
        mockserver,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        park_id,
        doaa_mock,
        endpoint,
        order_core_status,
        params,
        body,
        app_api_request,
        app_api_response,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert bson.BSON.decode(request.get_data()) == ORDER_CORE_FIELDS
        DOCUMENT_DATA['document']['status'] = order_core_status
        return mockserver.make_response(
            bson.BSON.encode(DOCUMENT_DATA), status=200,
        )

    @mockserver.json_handler('/integration-api/v1/orders/cancel')
    def _mock_integration_api(request):
        return mockserver.make_response(json={'status': 'cancel'}, status=200)

    doaa_mock.set_request_body(app_api_request)
    doaa_mock.set_status_code(200)
    doaa_mock.set_json(app_api_response)

    response = await taxi_fleet_orders_manager.post(
        endpoint, params=params, json=body, headers=build_headers(park_id),
    )

    assert response.status_code == 204
    assert doaa_mock.times_called() == (order_core_status == 'assigned')


async def test_not_found(taxi_fleet_orders_manager, doaa_mock, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert bson.BSON.decode(request.get_data()) == ORDER_CORE_FIELDS
        return mockserver.make_response(
            status=404, json={'code': 'no_such_order', 'message': 'something'},
        )

    response = await taxi_fleet_orders_manager.post(
        '/fleet/fleet-orders-manager/v2/active-orders/cancellation',
        params={'order_id': 'order_id1'},
        headers=build_headers('park_id_2'),
    )

    assert response.status_code == 404
    assert response.json()['message'] == 'Order not found'
    assert doaa_mock.times_called() == 0


async def test_conflicts(taxi_fleet_orders_manager, mockserver, doaa_mock):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert bson.BSON.decode(request.get_data()) == ORDER_CORE_FIELDS
        return mockserver.make_response(
            bson.BSON.encode(DOCUMENT_DATA), status=200,
        )

    doaa_mock.set_request_body(
        {
            'park_id': 'park_id_2',
            'driver_profile_id': 'driver_id1',
            'setcar_id': 'order4_alias',
            'should_notify': True,
            'origin': 'yandex_dispatch',
            'dispatch_selected_price': 'fixed',
        },
    )
    doaa_mock.set_status_code(410)
    doaa_mock.set_json(
        {'code': '410', 'message': 'Order has already been cancelled'},
    )

    response = await taxi_fleet_orders_manager.post(
        '/fleet/fleet-orders-manager/v2/active-orders/completion-by-fix',
        params={'order_id': 'order4'},
        headers=build_headers('park_id_2'),
    )

    assert response.status_code == 409
    assert response.json()['message'] == 'Operation conflict'
    assert doaa_mock.times_called() == 1
