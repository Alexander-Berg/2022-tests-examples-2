NAME = 'fleet-transactions-api'


def _handler_driver_list(context):
    def handler(request):
        limit = request.json['limit']
        cursor = request.json['cursor'] if 'cursor' in request.json else None
        park = request.json['query']['park']
        print(park['transaction']['event_at']['from'])
        print(park['transaction']['event_at']['to'])
        if (
                park['id'] == 'PARK-01'
                and park['driver_profile']['id'] == 'CONTRACTOR-01'
                and park['transaction']['event_at']['from']
                == '2019-12-31T23:00:00+00:00'
                and park['transaction']['event_at']['to']
                == '2020-01-01T12:00:00+00:00'
                and cursor != '1'
        ):
            return {
                'limit': limit,
                'cursor': '1',
                'transactions': [
                    {
                        'id': '4',
                        'event_at': '2020-01-01T00:00:00+00:00',
                        'category_id': 'tip',
                        'category_name': 'tip',
                        'amount': '200.0000',
                        'currency_code': 'RUB',
                        'description': 'a',
                        'created_by': {'identity': 'platform'},
                        'order_id': 'ORDER-04',
                    },
                ],
            }

        return {'limit': limit, 'cursor': '1', 'transactions': []}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/v1/parks/driver-profiles/transactions/list',
        _handler_driver_list(context),
    )

    return mocks
