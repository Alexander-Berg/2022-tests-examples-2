import datetime

import bson
import pytest

ENDPOINT = '/fleet/fleet-orders/v1/orders/item/edit/location-from'

GET_FIELDS_REQUEST = {
    'fields': [
        'order.status',
        'performer.seen',
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
                        'status': 'pending',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'performer': {},
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            204,
            {},
            id='order without driver',
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
                        'performer': {'db_id': 'contractor_park_id'},
                    },
                    'performer': {},
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
                        'status': 'pending',
                        'request': {
                            'white_label_requirements': {
                                'source_park_id': (
                                    'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'
                                ),
                            },
                        },
                    },
                    'performer': {
                        'seen': datetime.datetime(2022, 1, 1, 0, 0, 0),
                    },
                    '_id': 'order_id1',
                },
                'revision': {'order.version': 42},
            },
            400,
            {'code': 'order_in_progress'},
            id='order in progress',
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
                    'performer': {
                        'seen': datetime.datetime(2022, 1, 1, 0, 0, 0),
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
async def test_editing_location_from_put(
        mockserver, taxi_fleet_orders, mock_response, status, body,
):
    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _mock_parks(request):
        return {
            'city_id': 'city_id1',
            'country_id': 'country_id1',
            'demo_mode': False,
            'driver_partner_source': 'yandex',
            'id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
            'is_active': True,
            'is_billing_enabled': False,
            'is_franchising_enabled': False,
            'locale': 'en',
            'login': 'login',
            'name': 'name',
            'tz_offset': 1,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        }

    @mockserver.json_handler('/addrs.yandex/search')
    def _mock_geosearch(request):
        return mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

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
                '$set': {
                    'order.request.source': {
                        'fullname': '',
                        'geopoint': [0.0, 0.0],
                        'short_text': '',
                        'type': 'address',
                    },
                },
            },
            'filter': {'order.version': 42},
        }
        return mockserver.make_response(
            bson.BSON.encode({}), 200, content_type='application/bson',
        )

    endpoint_response = await taxi_fleet_orders.put(
        ENDPOINT,
        params={'id': 'c62650ea917edb5e99e3f62420617435'},
        json={'location_from': {'coordinates': {'lat': 0.0, 'lon': 0.0}}},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert endpoint_response.status == status

    if status == 400:
        assert endpoint_response.json() == body


async def test_editing_location_from_put_failure_404(
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
        json={'location_from': {'coordinates': {'lat': 0.0, 'lon': 0.0}}},
        headers=build_headers('c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    )

    assert response.status == 404
