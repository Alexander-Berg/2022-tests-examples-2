import datetime

import bson
import pytest

ENDPOINT = '/fleet/fleet-orders/v1/orders/item/edit/available-endpoints'

GET_FIELDS_REQUEST = {
    'fields': [
        'order.status',
        'order.preorder_request_id',
        'performer.seen',
        'order_info.statistics.status_updates',
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
    'mock_response, response',
    [
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    'performer': {},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment', 'driver', 'location-from', 'booked-at']},
            id='pre-order pending',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': 'source_park_id',
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    'performer': {},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': []},
            id='wrong contractor park',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [{'q': 'new_driver_found'}],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment']},
            id='pre-order pending driver found',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment']},
            id='pre-order pending driver received order',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment', 'location-from']},
            id='pre-order pending driver rejected order',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'assigned',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment']},
            id='pre-order assigned',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'finished',
                        'preorder_request_id': 'preorder_request_id',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': []},
            id='pre-order finished',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    'performer': {},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment', 'driver', 'location-from']},
            id='order pending',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [{'q': 'new_driver_found'}],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment']},
            id='order pending driver found',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment']},
            id='order pending driver received order',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment', 'location-from']},
            id='order pending driver rejected order',
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
                    },
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': ['comment']},
            id='order assigned',
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
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {'q': 'new_driver_found'},
                                {'q': 'seen_received'},
                            ],
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(1970, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            {'endpoints': []},
            id='order finished',
        ),
    ],
)
async def test_available_endpoints_get_success(
        mockserver, taxi_fleet_orders, mock_response, response,
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

    endpoint_response = await taxi_fleet_orders.get(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert endpoint_response.status == 200
    assert endpoint_response.json() == response


async def test_available_endpoints_get_failure_404(
        mockserver, taxi_fleet_orders,
):
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

    response = await taxi_fleet_orders.get(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert response.status == 404
