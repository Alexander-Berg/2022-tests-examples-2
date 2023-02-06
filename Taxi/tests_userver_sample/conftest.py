# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest
from userver_sample_plugins import *  # noqa: F403 F401


@pytest.fixture
def service_client_default_headers():
    return {
        'User-Agent': 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)',
    }


@pytest.fixture
def query_cache(taxi_userver_sample):
    async def query(cache_name, key):
        result = await taxi_userver_sample.get(
            'caches/' + cache_name, params={'key': key},
        )
        if result.status_code == 200:
            return result.json()
        if result.status_code == 404:
            assert result.json()['code'] == 'OOPS'
            return None
        assert False

    return query
