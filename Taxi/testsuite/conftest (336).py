# root conftest for service eulas
pytest_plugins = [
    'eulas_plugins.pytest_plugins',
    'tests_eulas.mocks.order_core',
    'tests_eulas.mocks.parks_replica',
    'tests_eulas.mocks.personal',
]
