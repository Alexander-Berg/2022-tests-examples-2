NAME = 'parks-replica'


def _handler_v1_parks_billing_client_id_retrieve(context):
    def handler(request):
        clid = request.query['park_id']
        bcid = None
        for item in context['taxi']['bcids']:
            if item['clid'] == clid:
                bcid = item['bcid']
                break
        return {'billing_client_id': bcid}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/v1/parks/billing_client_id/retrieve',
        _handler_v1_parks_billing_client_id_retrieve(context),
    )

    return mocks
