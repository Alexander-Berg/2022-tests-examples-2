import pytest

from taxi.integration_testing.framework import environment


@pytest.fixture(scope='session')
def memcached_container(testenv: environment.EnvironmentManager) -> environment.TestContainer:
    return testenv.add_container(
        name='memcached',
        image='registry.yandex.net/taxi/externalimages/memcached',
        ports=[11211],
        aliases=[
            'memcached.taxi.yandex.nonexistent'
        ]
    )
