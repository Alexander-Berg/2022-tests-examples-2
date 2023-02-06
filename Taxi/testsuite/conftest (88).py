import pytest

# root conftest for service cashback-annihilator
pytest_plugins = ['cashback_annihilator_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def _mock_plus_wallet(mockserver):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        balances = [
            {
                'balance': '120.0000',
                'currency': 'RUB',
                'wallet_id': 'w/eb92da32-3174-5ca0-9df5-d42db472a355',
            },
        ]
        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )
