NAME = 'driver-orders'


def _handler_bulk_retrieve(context):
    def handler(request):
        if request.json['query']['park']['id'] == 'PARK-01':
            return {
                'orders': [
                    context['orders'][id]
                    for id in request.json['query']['park']['order']['ids']
                ],
            }

        return {'orders': []}

    return handler


def _handler_list(context):
    def handler(request):
        limit = request.json['limit']

        return {'limit': limit, 'cursor': '1', 'orders': []}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/parks/orders/bulk_retrieve', _handler_bulk_retrieve(context))
    add('/v1/parks/orders/list', _handler_list(context))

    return mocks
