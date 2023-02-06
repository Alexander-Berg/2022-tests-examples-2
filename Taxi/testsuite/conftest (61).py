# root conftest for service cargo-c2c
pytest_plugins = [
    'cargo_c2c_plugins.pytest_plugins',
    'tests_cargo_c2c.plugins.workers',
]
