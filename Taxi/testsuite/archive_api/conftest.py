from tests_plugins import fastcgi

pytest_plugins = [
    # settings fixture
    'tests_plugins.settings',
    # Testsuite plugins
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.plugins.default',
    'taxi_tests.plugins.aliases',
    'taxi_tests.plugins.translations',
    'taxi_tests.plugins.mocks.configs_service',
    'tests_plugins.daemons.plugins',
    'tests_plugins.testpoint',
    # Local mocks
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mock_yt',
    'tests_plugins.config_service_defaults',
    # Local fixtures
    'archive_api.mock_yt_replications',
]

taxi_archive_api = fastcgi.create_client_fixture(
    'taxi_archive_api',
    service_headers={'YaTaxi-Api-Key': 'archive_api_token'},
)
