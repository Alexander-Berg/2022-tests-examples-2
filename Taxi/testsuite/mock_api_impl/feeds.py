NAME = 'feeds'


def _handler_create(context):
    def handler(request):
        channels = request.json['channels']
        service = request.json['service']
        assert {
            'channel': 'taximeter:Driver:PARK-01:CONTRACTOR-01',
        } in channels
        assert {
            'channel': 'taximeter:Driver:PARK-01:CONTRACTOR-02',
        } in channels
        assert {
            'channel': 'taximeter:Driver:PARK-01:CONTRACTOR-03',
        } in channels
        assert len(channels) == 3
        assert service == 'fleet-communications'
        assert request.json['payload']['text'] == r'MESSAGE\{\}'
        assert request.json['payload']['title'] == r'TITLE\{\}'
        assert 'MAILING-' in request.json['payload']['series_id']

        return {
            'service': service,
            'filtered': [],
            'feed_ids': {
                request.json['channels'][0][
                    'channel'
                ]: 'f6dc672653aa443d9ecf48cc5ef4cb22',
            },
        }

    return handler


def _handler_delete(context):
    def handler(request):
        return {}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/create', _handler_create(context))
    add('/v1/remove_by_request_id', _handler_delete(context))

    return mocks
