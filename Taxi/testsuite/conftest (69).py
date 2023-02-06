# root conftest for service cargo-finance
pytest_plugins = [
    # Codegen service plugins
    'cargo_finance_plugins.pytest_plugins',
    # Local service plugins
    'tests_cargo_finance.workers',
]
