pytest_plugins = [
    'taxi_tests.plugins.assertrepr_compare',
    'taxi_tests.plugins.common',
    'taxi_tests.plugins.config',
    'taxi_tests.plugins.mocked_time',
    'taxi_tests.plugins.mongodb',
    'taxi_tests.plugins.pgsql',
    'taxi_tests.plugins.redisdb',
    'taxi_tests.plugins.verify_file_paths',
]
