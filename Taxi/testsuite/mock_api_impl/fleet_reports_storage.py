NAME = 'fleet-reports-storage'


def _handler_create(context):
    def handler(request):
        return {}

    return handler


def _handler_upload(context):
    def handler(request):
        return {}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/internal/user/v1/operations/create', _handler_create(context))
    add('/internal/v1/file/upload', _handler_upload(context))

    return mocks
