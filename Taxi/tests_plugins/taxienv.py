import testsuite.environment.main

SERVICE_PLUGINS = [
    'testsuite.databases.mongo.pytest_plugin',
    'testsuite.databases.pgsql.pytest_plugin',
    'testsuite.databases.redis.pytest_plugin',
    'taxi_testsuite.plugins.databases.yt.pytest_plugin',
    'tests_plugins.databases.ydb.pytest_plugin',
    'testsuite.databases.clickhouse.pytest_plugin',
]

if __name__ == '__main__':
    testsuite.environment.main.main(service_plugins=SERVICE_PLUGINS)
