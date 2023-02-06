import pytest


# root conftest for service united-dispatch
pytest_plugins = [
    # Codegen service plugins
    'united_dispatch_plugins.pytest_plugins',
    'united_dispatch_grocery_plugins.pytest_plugins',
    'united_dispatch_eats_plugins.pytest_plugins',
    'united_dispatch_delivery_plugins.pytest_plugins',
    # Local service plugins
    'tests_united_dispatch.plugins.candidates_fixtures',
    'tests_united_dispatch.plugins.experiments',
    'tests_united_dispatch.plugins.happy_path',
    'tests_united_dispatch.plugins.cargo_dispatch_fixtures',
    'tests_united_dispatch.plugins.fixtures',
    'tests_united_dispatch.plugins.mocks',
    'tests_united_dispatch.plugins.workers',
    'tests_united_dispatch.plugins.simulator_fixtures',
    # Simulator
    'simulator.core.mocks.driver_trackstory',
    'simulator.core.mocks.order_satisfy',
    'simulator.core.mocks.order_search',
    'simulator.core.mocks.score_candidates',
]


@pytest.fixture(name='load_json_var')
def _load_json_var(load_json):
    def load_json_var(path, **variables):
        def var_hook(obj):
            varname = obj['$var']
            return variables[varname]

        return load_json(path, object_hook={'$var': var_hook})

    return load_json_var


def pytest_addoption(parser):
    parser.addoption(
        '--simulate', action='store_true', default=False, help='run simulator',
    )


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'simulator: mark test as simulator entrypoint',
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--simulate'):
        # --simulate was given in cli: run only simulator
        new_items = []
        for item in items:
            if item.get_closest_marker('simulator'):
                new_items.append(item)
        items[:] = new_items
    else:
        # --simulate was not given in cli: run all tests without simulator
        skip_simulate = pytest.mark.skip(reason='need --simulate option')
        for item in items:
            if 'simulator' in item.keywords:
                item.add_marker(skip_simulate)
