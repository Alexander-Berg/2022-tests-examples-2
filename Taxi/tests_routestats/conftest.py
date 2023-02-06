# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from routestats_plugins import *  # noqa: F403 F401


def enable_plugin(name: str) -> dict:
    return {
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'name': name,
        'consumers': ['uservices/routestats'],
        'clauses': [],
        'default_value': {'enabled': True},
    }


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'routestats_plugins: routestats plugins fixture',
    )


@pytest.fixture(name='routestats_plugins', autouse=True)
async def _routestats_plugins(request, taxi_routestats, experiments3):
    """
    For custom plugins:
    @pytest.mark.routestats_plugins(names=['top_level:proxy'])
    async def my_test(...)
    """
    for marker in request.node.iter_markers('routestats_plugins'):
        for plugin in marker.kwargs['names']:
            experiments3.add_config(
                **enable_plugin('routestats:uservices:plugins:' + plugin),
            )
    await taxi_routestats.invalidate_caches()


@pytest.fixture(name='mock_admin_images', autouse=True)
def _mock_admin_images(mockserver, load_json):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_response.json')
