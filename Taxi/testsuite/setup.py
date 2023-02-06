import setuptools

setuptools.setup(
    name='taxi-tests',
    version='0.1',
    description='Yandex.Taxi testsuite base package',
    install_requires=[
        'psycopg2==2.7.5',
        'pymongo==3.7.1',
        'pytest==3.7.2',
        'python-dateutil==2.7.3',
        'python-redis==0.2.1',
        'pytz==2018.5',
        'PyYAML==3.13',
        'redis==2.10.6',
        'requests==2.19.1',
        'Werkzeug==0.14.1',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
