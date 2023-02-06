import bson
import pytest

ENDPOINT = '/fleet/fleet-orders/v1/orders/item/edit/comment'

GET_FIELDS_REQUEST = {
    'fields': [
        'order.status',
        'order.request.white_label_requirements.source_park_id',
        'order.performer.db_id',
    ],
}


def build_headers(park_id):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }


@pytest.mark.parametrize(
    'mock_response, status, body',
    [
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'assigned',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            204,
            {},
            id='order not completed',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'assigned',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                        'performer': {'db_id': 'contractor_park_id'},
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            400,
            {'code': 'no_permission'},
            id='wrong contractor park',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'finished',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            400,
            {'code': 'order_completed'},
            id='order completed',
        ),
    ],
)
async def test_editing_comment_put(
        mockserver, taxi_fleet_orders, mock_response, status, body,
):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_fields(request):
        assert request.args['order_id'] == 'c62650ea917edb5e99e3f62420617435'
        assert bson.BSON.decode(request.get_data()) == GET_FIELDS_REQUEST
        return mockserver.make_response(
            bson.BSON.encode(mock_response),
            200,
            content_type='application/bson',
        )

    @mockserver.json_handler('/order-core/internal/processing/v1/event-batch')
    def _mock_event_batch(request):
        assert bson.BSON.decode(request.get_data()) == {
            'events': [{'event_key': 'handle_editing'}],
            'extra_update': {
                '$set': {'order.request.comment': 'Test comment'},
            },
            'filter': {'order.version': 42},
        }
        return mockserver.make_response(
            bson.BSON.encode({}), 200, content_type='application/bson',
        )

    endpoint_response = await taxi_fleet_orders.put(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        json={'comment': 'Test comment'},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert endpoint_response.status == status

    if status == 400:
        assert endpoint_response.json() == body


async def test_editing_comment_put_failure_404(mockserver, taxi_fleet_orders):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_fields(request):
        assert request.args['order_id'] == 'c62650ea917edb5e99e3f62420617435'
        assert bson.BSON.decode(request.get_data()) == GET_FIELDS_REQUEST
        return mockserver.make_response(
            json={'code': 'no_such_order', 'message': 'Order not found'},
            status=404,
        )

    response = await taxi_fleet_orders.put(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        json={'comment': 'Test comment'},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert response.status == 404
