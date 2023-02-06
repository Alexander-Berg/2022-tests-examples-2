import datetime

import elasticsearch
import pytest

from taxi.integration_testing.framework import environment

ELASTICSEARCH_TIMEOUT_SECONDS = 30


@pytest.fixture(scope='session')
def elastic_container(testenv: environment.EnvironmentManager) -> environment.TestContainer:
    return testenv.add_container(
        name='elastic',
        image='registry.yandex.net/taxi/externalimages/elasticsearch',
        environment={
            'discovery.type': 'single-node'
        },
        ports=[9200],
        aliases=[
            'elasticsearch.taxi.yandex',
            'taxi-search-logs01.taxi.yandex.net',
            'taxi-elastic-logs.taxi.yandex.net'
        ]
    )


@pytest.fixture(scope='session')
def elastic_client(elastic_container: environment.TestContainer) -> elasticsearch.Elasticsearch:
    es = elasticsearch.Elasticsearch([f'http://{elastic_container.get_endpoint(9200)}'])
    elasticsearch_timeout: datetime.timedelta = datetime.timedelta(seconds=ELASTICSEARCH_TIMEOUT_SECONDS)
    started = datetime.datetime.now()

    while not es.ping():
        if datetime.datetime.now() > started + elasticsearch_timeout:
            raise environment.EnvironmentSetupError(f'elasticsearch did not start during {elasticsearch_timeout}')

    return es
