NAME = 'fleet-payouts'


def _handler_fleet_subscription_level_get(context, mockserver):
    def handler(request):
        park_id = request.query['clid']
        if park_id == 'clid_PARK-02':
            return {'fleet_subscription_level': 'base', 'park_rating': 'bad'}
        if park_id == 'clid_PARK-03':
            return {'fleet_subscription_level': '', 'park_rating': ''}
        return {'fleet_subscription_level': 'premium', 'park_rating': 'cool'}

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/internal/payouts/v1/fleet-subscription-level',
        _handler_fleet_subscription_level_get(context, mockserver),
    )

    return mocks
