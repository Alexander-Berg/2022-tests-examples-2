NAME = 'yql'


def _handler_create(context):
    def handler(request):
        return {'id': 'OPERATION_ID'}

    return handler


def _handler_run(context):
    def handler(request):
        return {'id': 'OPERATION_ID', 'status': 'COMPLETED'}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/api/v2/operations', _handler_create(context))
    add('/api/v2/operations/OPERATION_ID', _handler_run(context))

    return mocks
