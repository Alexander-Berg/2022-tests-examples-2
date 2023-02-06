import pytest


@pytest.fixture(name='driver_categories_api', autouse=True)
def mock_driver_categories_api(mockserver, load_json):
    @mockserver.json_handler('/driver-categories-api/internal/v2/categories')
    def _internal_v2_categories(request):
        all_categories = load_json('all_categories.json')
        return all_categories
