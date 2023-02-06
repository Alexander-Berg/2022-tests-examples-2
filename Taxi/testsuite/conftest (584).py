import pytest

# root conftest for service shortcuts-admin
pytest_plugins = ['shortcuts_admin_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def _mock_admin_images(mockserver, load_json):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock(_):
        return load_json('admin_images_list.json')
