NAME = 'fleet-vehicles'


def _handler_retrieve(context):
    def handler(request):
        return context['fleet_vehicles_response']

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/vehicles/retrieve', _handler_retrieve(context))

    return mocks
