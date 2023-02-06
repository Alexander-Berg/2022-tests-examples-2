import multiprocessing as mp
from concurrent import futures
import functools

from dmp_suite import global_state


def _get_key(key, default=None):
    return global_state.get(key, default)


def test_global_state_patch():
    with global_state.patch(key=123):
        assert global_state.get('key') == 123

        with global_state.patch(key=456):
            assert global_state.get('key') == 456

        assert global_state.get('key') == 123

    assert global_state.get('key') is None


def test_global_state_get_keys():
    with global_state.patch(key_1=123, key_2=456, key_3='asd'):
        result = global_state.get_keys('key_1', 'key_3')

    assert result == {'key_3': 'asd', 'key_1': 123}


def test_global_state_threading():
    fn = functools.partial(_get_key, 'key', 0)

    with global_state.patch(key=123):
        with futures.ThreadPoolExecutor(max_workers=4) as pool:
            mp_buffers_futures = [
                pool.submit(fn) for _ in range(100)
            ]
            for future in futures.as_completed(mp_buffers_futures, timeout=10):
                assert future.result() == 123

    with futures.ThreadPoolExecutor(max_workers=4) as pool:
        mp_buffers_futures = [
            pool.submit(fn) for _ in range(100)
        ]
        for future in futures.as_completed(mp_buffers_futures, timeout=10):
            assert future.result() == 0


def test_global_state_fork():
    mp_ctx = mp.get_context('fork')

    fn = functools.partial(_get_key, 'key', 0)

    with global_state.patch(key=123):
        with futures.ProcessPoolExecutor(
                max_workers=4,
                mp_context=mp_ctx,
        ) as pool:
            mp_buffers_futures = [
                pool.submit(fn) for _ in range(100)
            ]
            for future in futures.as_completed(mp_buffers_futures, timeout=10):
                assert future.result() == 123

    with futures.ProcessPoolExecutor(
            max_workers=4,
            mp_context=mp_ctx,
    ) as pool:
        mp_buffers_futures = [
            pool.submit(fn) for _ in range(100)
        ]
        for future in futures.as_completed(mp_buffers_futures, timeout=10):
            assert future.result() == 0
