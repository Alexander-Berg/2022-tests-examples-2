import pytest


@pytest.fixture(name='disabled_first_update_caches')
def _disabled_first_update_caches(request):
    mark = request.node.get_closest_marker('uservice_oneshot')
    return mark.kwargs.get('disable_first_update', ()) if mark else []


@pytest.fixture
def disable_first_update_hook(disabled_first_update_caches):
    def hook(config, config_vars):
        components = config['components_manager']['components']
        for cache_name in disabled_first_update_caches:
            components[cache_name]['dump']['first-update-mode'] = 'skip'

    return hook
