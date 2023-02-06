NAME = 'driver-orders'


def _handler_bulk_retrieve(context):
    def handler(request):
        if request.json['query']['park']['id'] == 'PARK-01':
            if 'ORDER-01' in request.json['query']['park']['order']['ids']:
                return {
                    'orders': [
                        {
                            'id': 'ORDER-01',
                            'order': {
                                'short_id': 111,
                                'status': 'complete',
                                'created_at': '2020-01-01T00:00:00+03:00',
                                'booked_at': '2020-01-01T00:00:00+03:00',
                                'provider': 'none',
                                'transporting_at': '2020-01-01T00:00:00+03:00',
                                'ended_at': '2020-01-01T00:00:10+03:00',
                                'price': '1000.0000',
                                'address_from': {'address': 'FROM'},
                                'address_to': {'address': 'TO'},
                            },
                        },
                    ],
                }

        return {'orders': []}

    return handler


def _handler_list(context):
    def handler(request):
        limit = request.json['limit']
        cursor = request.json['cursor'] if 'cursor' in request.json else None
        park = request.json['query']['park']
        if (
                park['id'] == 'PARK-01'
                and park['driver_profile']['id'] == 'CONTRACTOR-01'
                and park['order']['ended_at']['from']
                == '2020-01-01T00:00:00+00:00'
                and park['order']['ended_at']['to']
                == '2020-01-01T12:00:00+00:00'
                and cursor != '1'
        ):
            return {
                'limit': limit,
                'cursor': '1',
                'orders': [
                    {
                        'id': 'ORDER-04',
                        'short_id': 111,
                        'status': 'complete',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'none',
                        'price': '1000.0000',
                        'address_from': {
                            'address': 'FROM',
                            'lat': 0,
                            'lon': 0,
                        },
                        'amenities': [],
                        'route_points': [],
                        'ended_at': '2020-01-01T01:00:00+00:00',
                        'events': [
                            {
                                'event_at': '2020-01-01T00:00:00+00:00',
                                'order_status': 'transporting',
                            },
                        ],
                        'payment_method': 'card',
                    },
                    {
                        'id': 'ORDER-04',
                        'short_id': 111,
                        'status': 'cancelled',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'none',
                        'price': '1000.0000',
                        'address_from': {
                            'address': 'FROM',
                            'lat': 0,
                            'lon': 0,
                        },
                        'amenities': [],
                        'route_points': [],
                        'ended_at': '2020-01-01T01:00:00+00:00',
                        'events': [
                            {
                                'event_at': '2020-01-01T00:00:00+00:00',
                                'order_status': 'transporting',
                            },
                        ],
                        'payment_method': 'card',
                    },
                    {
                        'id': 'ORDER-05',
                        'short_id': 111,
                        'status': 'complete',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'none',
                        'price': '199.0000',
                        'address_from': {
                            'address': 'FROM',
                            'lat': 0,
                            'lon': 0,
                        },
                        'amenities': [],
                        'route_points': [],
                        'ended_at': '2020-01-01T01:00:00+00:00',
                        'events': [
                            {
                                'event_at': '2020-01-01T00:58:00+00:00',
                                'order_status': 'transporting',
                            },
                        ],
                        'payment_method': 'card',
                    },
                    {
                        'id': 'ORDER-06',
                        'short_id': 111,
                        'status': 'complete',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'none',
                        'price': '201.0000',
                        'address_from': {
                            'address': 'FROM',
                            'lat': 0,
                            'lon': 0,
                        },
                        'amenities': [],
                        'route_points': [],
                        'ended_at': '2020-01-01T01:00:00+00:00',
                        'events': [
                            {
                                'event_at': '2020-01-01T00:58:00+00:00',
                                'order_status': 'transporting',
                            },
                        ],
                        'payment_method': 'card',
                    },
                    {
                        'id': 'ORDER-07',
                        'short_id': 111,
                        'status': 'complete',
                        'created_at': '2020-01-01T00:00:00+00:00',
                        'booked_at': '2020-01-01T00:00:00+00:00',
                        'provider': 'none',
                        'price': '1000.0000',
                        'address_from': {
                            'address': 'FROM',
                            'lat': 0,
                            'lon': 0,
                        },
                        'amenities': [],
                        'route_points': [],
                        'ended_at': '2020-01-01T01:00:00+00:00',
                        'events': [
                            {
                                'event_at': '2020-01-01T00:00:00+00:00',
                                'order_status': 'transporting',
                            },
                        ],
                        'payment_method': 'cash',
                    },
                ],
            }

        return {'limit': limit, 'cursor': '1', 'orders': []}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/parks/orders/bulk_retrieve', _handler_bulk_retrieve(context))
    add('/v1/parks/orders/list', _handler_list(context))

    return mocks
