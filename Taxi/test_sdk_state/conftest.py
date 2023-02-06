import pytest

from tests_plus_sweet_home import constants


@pytest.fixture(autouse=True)
def mock_plus_wallet(mockserver):
    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        return {
            'balances': [
                {
                    'balance': constants.DEFAULT_BALANCE,
                    'currency': constants.DEFAULT_CURRENCY,
                    'wallet_id': constants.DEFAULT_WALLET_ID,
                },
            ],
        }
