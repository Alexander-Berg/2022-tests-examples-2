NAME = 'personal'


def _handler_retrieve(context):
    def handler(request):
        assert '_PD' in request.json['id']
        return {
            'id': request.json['id'],
            'value': request.json['id'].replace('_PD', ''),
        }

    return handler


def _handler_store(context):
    def handler(request):
        if '_' in request.json['value']:
            return {
                'id': request.json['value'].replace('_', '_PD_'),
                'value': request.json['value'],
            }
        return {
            'id': request.json['value'] + '_PD',
            'value': request.json['value'],
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/tins/retrieve', _handler_retrieve(context))
    add('/v1/tins/store', _handler_store(context))
    add('/v1/identifications/retrieve', _handler_retrieve(context))
    add('/v1/identifications/store', _handler_store(context))

    return mocks
