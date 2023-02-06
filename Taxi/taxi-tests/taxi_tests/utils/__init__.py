import datetime
import time


CACHE_ERROR_MSG = (
    'Cache update did not happen in time.'
    'cached_values: %s, service: %s'
)


def wait_for(timeout, error_msg, *, sleep=5):
    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    obj = None
    while datetime.datetime.now() < end:
        obj = {}
        yield obj
        time.sleep(sleep)
    raise TimeoutError(error_msg + f', obj: {obj}')


def wait_for_cache(cached_values, service, cache_handler='cache-stats',
                   timeout=150, sleep_for=5):
    def _get_time_updates():
        response = service.get(cache_handler)
        times = [response[cv]['last_update'] for cv in cached_values]
        return times

    if not isinstance(cached_values, list):
        cached_values = [cached_values]

    cache_size = len(cached_values)
    time_updates = _get_time_updates()
    mask = [True for _ in range(cache_size)]
    cur_cache_size = cache_size

    for _ in wait_for(
            timeout,
            CACHE_ERROR_MSG % (cached_values, str(service)),
            sleep=sleep_for,
    ):
        last_updates = _get_time_updates()
        for i in range(cache_size):
            if mask[i] and time_updates[i] != last_updates[i]:
                mask[i] = False
                cur_cache_size -= 1
                if cur_cache_size == 0:
                    return

    raise TimeoutError('Timeout for waiting caches {}'.
                       format([cached_values[i]
                               for i in range(cache_size) if mask[i]]))
