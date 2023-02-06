import pytest

# root conftest for service grocery-caas-promo
pytest_plugins = ['grocery_caas_promo_plugins.pytest_plugins']


@pytest.fixture(name='cold_storage', autouse=True)
def mock_cold_storage(mockserver):
    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/'
        'expiring-products',
    )
    def _mock_cold_storage(request):
        return {'items': []}
