import datetime

import bson
import pytest

ENDPOINT = '/fleet/fleet-orders/v1/orders/item/edit/booked-at'

GET_FIELDS_REQUEST = {
    'fields': [
        'order.status',
        'order_info.statistics.status_updates',
        'order.preorder_request_id',
        'order.request.source',
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
    'mock_response, mock_due, request_body, response_status, response_body',
    [
        pytest.param(
            {
                'document': {
                    'order': {
                        'status': 'pending',
                        'request': {
                            'source': {'geopoint': [0.0, 0.0]},
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 0, 0),
            {'booked_at': '1970-01-01T00:00:00Z'},
            400,
            {'code': 'not_preorder'},
            id='not preorder',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'preorder_request_id': 'preorder_request_id',
                        'status': 'pending',
                        'request': {
                            'source': {'geopoint': [0.0, 0.0]},
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 1, 0),
            {'booked_at': '1970-01-01T01:00:00Z'},
            204,
            {},
            id='order before start lookup',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'preorder_request_id': 'preorder_request_id',
                        'status': 'pending',
                        'request': {
                            'source': {'geopoint': [0.0, 0.0]},
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                        'performer': {'db_id': 'contractor_park_id'},
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 1, 0),
            {'booked_at': '1970-01-01T01:00:00Z'},
            400,
            {'code': 'no_permission'},
            id='wrong contractor park',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'preorder_request_id': 'preorder_request_id',
                        'status': 'pending',
                        'request': {
                            'source': {'geopoint': [37.375, 55.525]},
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 1, 0),
            {'booked_at': '1970-01-01T01:00:00Z'},
            400,
            {'code': 'incorrect_value'},
            id='incorrect value specific zone',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'preorder_request_id': 'preorder_request_id',
                        'status': 'pending',
                        'request': {
                            'source': {'geopoint': [0.0, 0.0]},
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'order_info': {'statistics': {'status_updates': []}},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 0, 0),
            {'booked_at': '1970-01-01T00:00:00Z'},
            400,
            {'code': 'incorrect_value'},
            id='incorrect value',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'preorder_request_id': 'preorder_request_id',
                        'status': 'pending',
                        'request': {
                            'source': {'geopoint': [0.0, 0.0]},
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
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 0, 0),
            {'booked_at': '1970-01-01T00:00:00Z'},
            400,
            {'code': 'order_in_progress'},
            id='order in progress',
        ),
        pytest.param(
            {
                'document': {
                    'order': {
                        'preorder_request_id': 'preorder_request_id',
                        'status': 'finished',
                        'request': {
                            'source': {'geopoint': [0.0, 0.0]},
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
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            datetime.datetime(1970, 1, 1, 0, 0),
            {'booked_at': '1970-01-01T00:00:00Z'},
            400,
            {'code': 'order_completed'},
            id='order completed',
        ),
    ],
)
@pytest.mark.config(
    PREORDER_AVAILABLE_V1_ML_ZONE_RULES={
        'rules': [
            {
                'action': 'permit',
                'affected_tariff_classes': [
                    'econom',
                    'business',
                    'comfortplus',
                    'vip',
                    'ultimate',
                    'maybach',
                    'uberlux',
                ],
                'max_preorder_shift_hours': 3,
                'min_preorder_shift_minutes': 120,
                'rule_name': 'mkad_permit',
                'schedule': [
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '00:00:00',
                        'utc_time_end': '23:00:00',
                    },
                    {
                        'schedule_type': 'daily',
                        'utc_time_begin': '22:00:00',
                        'utc_time_end': '01:00:00',
                    },
                ],
                'zone_polygon': [
                    [37.35, 55.50],
                    [37.35, 55.55],
                    [37.40, 55.55],
                    [37.40, 55.50],
                ],
            },
        ],
    },
)
@pytest.mark.now('1970-01-01T00:00:00Z')
async def test_editing_booked_at_put(
        mockserver,
        taxi_fleet_orders,
        mock_response,
        mock_due,
        request_body,
        response_status,
        response_body,
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
            'extra_update': {'$set': {'order.request.due': mock_due}},
            'filter': {'order.version': 42},
        }
        return mockserver.make_response(
            bson.BSON.encode({}), 200, content_type='application/bson',
        )

    endpoint_response = await taxi_fleet_orders.put(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        json=request_body,
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert endpoint_response.status == response_status

    if response_status == 400:
        assert endpoint_response.json() == response_body


async def test_editing_booked_at_put_failure_404(
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

    response = await taxi_fleet_orders.put(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        json={'booked_at': '1970-01-01T00:00:00Z'},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert response.status == 404
