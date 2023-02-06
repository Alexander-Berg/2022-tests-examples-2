NAME = 'contractor-instant-payouts-qiwi'

_RAISE_401 = 'Bearer ffffffff-ffff-ffff-ffff-000000000401'


def _handler_api_balance(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401)

        return {
            'balance': {'value': '100.00', 'currency': 'RUB'},
            'available': {'value': '100.00', 'currency': 'RUB'},
        }

    return handler


def _handler_api_card_token_create(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401)

        return {'payUrl': 'https://oplata.qiwi.com/form/?invoice_uid=xxx'}

    return handler


def _handler_api_card_token_get(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']
        print(auth_token)
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401)

        return {
            'status': 'SUCCESS',
            'isValidCard': True,
            'createdToken': {
                'token': '11111111-1111-1111-1111-111111111111',
                'name': '123456******7890',
                'expiredDate': '2022-01-01T00:00:00',
            },
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/partner/payout/v1/agents/agent/points/point/balance',
        _handler_api_balance(context, mockserver),
    )

    add(
        '/partner/payin/v1/sites/site/bills/'
        '4b9f3be4-40d0-51d8-aa7a-0624e509c4dc',
        _handler_api_card_token_create(context, mockserver),
    )

    add(
        '/partner/payin/v1/sites/site/validation/card/requests/'
        '4b9f3be4-40d0-51d8-aa7a-0624e509c4dc',
        _handler_api_card_token_get(context, mockserver),
    )

    return mocks
