import setuptools

setuptools.setup(
    name='taxi-tests',
    version='0.1',
    description='Yandex.Taxi testsuite base package',
    install_requires=[
        'PyYAML>=3.13',
        'aiohttp~=3.5.4',
        'pytest-aiohttp~=0.3.0',
        'pytest~=3.7.2',
        'python-dateutil~=2.7.3',
        'pytz>=2018.5',
        'uvloop~=0.12.1',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
