NAME = 'interpay'

_RAISE_401 = 'Bearer bad_token'
_RESPONSE_401 = {
    'error': {
        'code': 401,
        'status': 'Unauthorized',
        'request': '45e55a03-dc69-9357-8526-0e6542d3917d',
        'reason': 'Access token is not active',
        'message': 'Access credentials are invalid',
    },
}


def _handler_api_add_card(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']

        assert auth_token.startswith('Bearer ')
        assert request.headers['Service-Key'] == '1'
        assert request.headers['Idempotency-replay'] == 'true'
        assert request.json['route'] == 'yt'

        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401, json=_RESPONSE_401)

        return {
            'id': 1,
            'route': 'yt',
            'state': 'new',
            'external_id': '30000000-0000-0000-0000-000000000001',
            'token': 'token1',
            'nonce': 'nonce1',
        }

    return handler


def _handler_api_get_balance(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']

        assert auth_token.startswith('Bearer ')

        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401, json=_RESPONSE_401)

        return {
            'id': 1,
            'ref_id': 123,
            'currency': 398,
            'balance': '100.0000',
            'stated_at': '2022-01-01T00:00:00+00:00',
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/v1/svc/card_withdrawal/cards',
        _handler_api_add_card(context, mockserver),
    )

    add(
        '/v1/emoney/contracts/1/balance',
        _handler_api_get_balance(context, mockserver),
    )

    return mocks
