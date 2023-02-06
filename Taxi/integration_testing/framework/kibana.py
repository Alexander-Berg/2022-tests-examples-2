import pytest

from taxi.integration_testing.framework import environment


@pytest.fixture(scope='session')
def kibana_container(testenv: environment.EnvironmentManager) -> environment.TestContainer:
    return testenv.add_container(
        name='kibana',
        image='registry.yandex.net/taxi/externalimages/kibana',
        environment={
            'ELASTICSEARCH_HOSTS': 'http://elasticsearch.taxi.yandex:9200'
        },
        ports=[5601],
        aliases=[
            'kibana.taxi.yandex.nonexistent'
        ]
    )
