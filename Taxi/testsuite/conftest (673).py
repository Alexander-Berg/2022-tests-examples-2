import pytest
# root conftest for service zoneinfo
pytest_plugins = ['zoneinfo_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def mock_admin_images_response(mockserver, load_json):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_response.json')
