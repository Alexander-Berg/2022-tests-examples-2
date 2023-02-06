import pytest


@pytest.fixture(name='clown_namespaces')
def _clown_namespaces():
    return [{'id': 1, 'name': 'taxi'}]


@pytest.fixture(autouse=True)
def _clown_cache_mocks_autouse(clown_cache_mocks):
    return clown_cache_mocks


@pytest.fixture(autouse=True)
def _patch_cache_path(monkeypatch):
    monkeypatch.setattr(
        'clownductor_cache.components.CACHE_PATH',
        '/tmp/yandex/taxi/clownductor/',
    )
