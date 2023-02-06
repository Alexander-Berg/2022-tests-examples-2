# root conftest for service cargo-corp

pytest_plugins = [
    # root
    'cargo_corp_plugins.pytest_plugins',
    # local service plugins
    'tests_cargo_corp.plugins.database',
    'tests_cargo_corp.plugins.fixtures',
    'tests_cargo_corp.plugins.mocks',
    'tests_cargo_corp.plugins.service',
]
