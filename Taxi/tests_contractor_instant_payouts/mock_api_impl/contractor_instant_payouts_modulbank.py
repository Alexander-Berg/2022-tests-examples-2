NAME = 'contractor-instant-payouts-modulbank'

_RAISE_401 = 'ffffffff-ffff-ffff-ffff-000000000401'
_RESPONSE_401 = {
    'status': 'fail',
    'error': {'code': 'ERR_UNAUTHORIZED', 'message': 'Unauthorized'},
}


def _make_account(account):
    return {
        'id': account['id'],
        'status': account['status'],
        'inn': account['inn'],
        'balance': account['balance'],
    }


def _handler_api_accounts(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401, json=_RESPONSE_401)

        accounts = []
        for account in context['modulbank']['accounts']:
            if account['auth_token'] != auth_token:
                continue
            accounts.append(account)

        return {
            'status': 'success',
            'data': [_make_account(account) for account in accounts],
        }

    return handler


def _handler_api_accounts_id(context, mockserver, account_id):
    def handler(request):
        auth_token = request.headers['Authorization']
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401, json=_RESPONSE_401)

        accounts = []
        for account in context['modulbank']['accounts']:
            if account['auth_token'] != auth_token:
                continue
            if account['id'] != account_id:
                continue
            accounts.append(account)
        assert len(accounts) == 1

        return {'status': 'success', 'data': _make_account(accounts[0])}

    return handler


def _handler_api_cards_tokens(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401, json=_RESPONSE_401)

        return {
            'status': 'success',
            'data': {
                'id': 'dddddddd-dddd-dddd-dddd-dddddddddddd',
                'card_token': 'cccccccc-cccc-cccc-cccc-cccccccccccc',
                'status': 'wait_pan',
                'form_url': '/forms/cards/tokenize?session=xxx',
                'lifetime_sec': int(request.json['lifetime_sec']),
            },
        }

    return handler


def _handler_api_sbp_participants(context, mockserver):
    def handler(request):
        auth_token = request.headers['Authorization']
        if auth_token == _RAISE_401:
            return mockserver.make_response(status=401, json=_RESPONSE_401)

        return {
            'data': {
                'rcv_time': '2022-01-01T12:00:00+00:00',
                'participants': [
                    {
                        'id': '101',
                        'name_en': 'Bank1',
                        'name_ru': 'Банк1',
                        'effective_date': '20220101',
                        'bic': '123',
                    },
                    {
                        'id': '102',
                        'name_en': 'Bank2',
                        'name_ru': 'Банк2',
                        'effective_date': '20220101',
                        'bic': '456',
                    },
                ],
            },
            'status': 'success',
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/api/accounts', _handler_api_accounts(context, mockserver))
    for account in context['modulbank']['accounts']:
        account_id = account['id']
        add(
            f'/api/accounts/{account_id}',
            _handler_api_accounts_id(context, mockserver, account_id),
        )
    add('/api/cards/tokens', _handler_api_cards_tokens(context, mockserver))
    add(
        '/api/sbp/participants',
        _handler_api_sbp_participants(context, mockserver),
    )

    return mocks
