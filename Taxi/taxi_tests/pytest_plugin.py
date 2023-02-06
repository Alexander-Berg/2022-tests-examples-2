# Common testsuite plugins
pytest_plugins = [
    'taxi_tests.plugins.loop',
    'taxi_tests.daemons.pytest_plugin',
    'taxi_tests.environment.pytest_plugin',
    'taxi_tests.logging.pytest_plugin',
    'taxi_tests.plugins.assertrepr_compare',
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.mocked_time',
    'taxi_tests.plugins.mockserver',
    'taxi_tests.plugins.testpoint',
    'taxi_tests.plugins.verify_file_paths',
]
