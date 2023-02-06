NAME = 'fleet-antifraud'


def _handler_v1_blocked_balance_get(context):
    def handler(request):
        return {'blocked_balance': '0.0000'}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/v1/park-check/blocked-balance',
        _handler_v1_blocked_balance_get(context),
    )

    return mocks
