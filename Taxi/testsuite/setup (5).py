import setuptools

setuptools.setup(
    name='testsuite',
    version='0.1',
    description='Yandex.Taxi Testsuite Package',
    install_requires=[
        'PyYAML>=3.13',
        'aiohttp>=3.5.4',
        'pytest-aiohttp>=0.3.0',
        'pytest>=3.7.2',
        'python-dateutil>=2.7.3',
        'pytz>=2018.5',
        'uvloop>=0.12.1',
        'pymongo>=3.7.1',  # Currently required by .utils.json_util
        'cached-property>=1.5.1',
    ],
    extras_require={
        'mongodb': [],
        'postgresql': ['psycopg2>=2.7.5'],
        'postgresql-binary': ['psycopg2-binary>=2.7.5'],
        'redis': ['python-redis>=0.2.1', 'redis>=2.10.6'],
        'mysql': ['PyMySQL>=0.9.2'],
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    packages=setuptools.find_packages(include=['testsuite', 'testsuite.*']),
    package_data={
        'testsuite.environment': ['scripts/*.sh'],
        'testsuite.databases.mongo': ['scripts/service-mongo'],
        'testsuite.databases.redis': [
            'configs/*.tpl',
            'scripts/service-redis',
        ],
        'testsuite.databases.mysql': [
            'scripts/mysql-helper',
            'scripts/service-mysql',
        ],
        'testsuite.databases.pgsql': [
            'configs/*.conf',
            'scripts/find-pg.sh',
            'scripts/pgmigrate-helper',
            'scripts/psql-helper',
            'scripts/service-postgresql',
        ],
    },
)
