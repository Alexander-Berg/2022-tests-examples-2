import pytest

BALANCES = 'balances-handler'

DEFAULT_WALLET_ID = 'wallet/123123123123'
DEFAULT_BALANCE = '2809'
DEFAULT_WALLET = {
    'wallet_id': DEFAULT_WALLET_ID,
    'amount': DEFAULT_BALANCE,
    'currency': 'RUB',
}
OTHER_CURRENCY_WALLET_ID = 'wallet/321321321321'
OTHER_CURRENCY_WALLET = {
    'wallet_id': OTHER_CURRENCY_WALLET_ID,
    'amount': DEFAULT_BALANCE,
    'currency': 'ILS',
}

DEFAULT_RESPONSE = {'balances': [OTHER_CURRENCY_WALLET, DEFAULT_WALLET]}


@pytest.fixture(name='billing_wallet')
def mock_billing_wallet(mockserver):
    class Context:
        def __init__(self):
            self.error_code = {}
            self.check_balances_data = None
            self.balances_data = None

        def mock_balances(self, **argv):
            self.balances_data = {}
            for key in argv:
                self.balances_data[key] = argv[key]

        def check_balances(self, **argv):
            self.check_balances_data = {}
            for key in argv:
                self.check_balances_data[key] = argv[key]

        def set_error_code(self, code):
            self.error_code[BALANCES] = code

        def times_balances_called(self):
            return mock_balances.times_called

        def flush_all(self):
            mock_balances.flush()

    context = Context()

    @mockserver.json_handler('/billing-wallet/balances')
    def mock_balances(request):
        if BALANCES in context.error_code:
            code = context.error_code[BALANCES]
            return mockserver.make_response('{}', code)

        if context.check_balances_data is not None:
            for key, value in context.check_balances_data.items():
                assert request.json[key] == value, key

        if context.balances_data is None:
            return DEFAULT_RESPONSE

        return {**DEFAULT_RESPONSE, **context.balances_data}

    return context
