NAME = 'personal'


def _handler_v1_data_type_store(context):
    def handler(request):
        assert request.json['value'] == '+70000000000'
        assert request.json['validate']
        return {'id': 'pd_id1', 'value': '+70000000000'}

    return handler


def _handler_v1_data_type_retrieve(context):
    def handler(request):
        assert request.json['id'] == 'pd_id1'
        return {'id': 'pd_id1', 'value': '+70000000000'}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/phones/store', _handler_v1_data_type_store(context))
    add('/v1/phones/retrieve', _handler_v1_data_type_retrieve(context))

    return mocks
