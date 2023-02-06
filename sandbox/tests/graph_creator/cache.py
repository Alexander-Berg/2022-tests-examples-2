from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from unittest.mock import MagicMock

from sandbox.projects.ott.packager_management_system.lib.graph_creator.cache import SyncedCache


def test_get():
    cache = SyncedCache()

    loader_mock = MagicMock(return_value='val')

    actual_value = cache.get('key', loader_mock)

    assert actual_value == 'val'


def test_get_cached():
    cache = SyncedCache()

    loader_mock = MagicMock(return_value='val')

    cache.get('key', loader_mock)
    cache.get('key', loader_mock)

    loader_mock.assert_called_once()


def test_synced_concurrent_get():
    lock = Lock()

    def _load(*_):
        with lock:
            return 'val'

    cache = SyncedCache()
    loader_mock = MagicMock(side_effect=_load)
    executor = ThreadPoolExecutor(max_workers=2)

    lock.acquire()

    executor.submit(cache.get, 'key', loader_mock)
    executor.submit(cache.get, 'key', loader_mock)

    lock.release()
    executor.shutdown()

    loader_mock.assert_called_once()
