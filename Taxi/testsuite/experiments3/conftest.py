from tests_plugins import fastcgi

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # local mocks
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.config_service_defaults',
]

taxi_experiments3 = fastcgi.create_client_fixture('taxi_experiments3')
