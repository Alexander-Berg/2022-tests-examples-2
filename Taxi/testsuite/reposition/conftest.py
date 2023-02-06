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
    'tests_plugins.config_service_defaults',
    'tests_plugins.mock_conductor',
    'tests_plugins.mock_experiments3_proxy',
    'tests_plugins.mock_geoareas',
    'tests_plugins.mock_taxi_exp',
    'tests_plugins.mock_tags',
    'tests_plugins.mock_territories',
    'tests_plugins.mock_tvm',
    'tests_plugins.mock_tvm2',
    'tests_plugins.mock_heatmap_storage',
    'tests_plugins.pgsupport_fixture',
    'tests_plugins.mock_solomon',
    'tests_plugins.mock_agglomerations',
]

taxi_reposition = fastcgi.create_client_fixture('taxi_reposition')
