import functools
import time

import requests

REQUEST_TIMEOUT = 10
RETRIES = 300
SLEEP_SEC = 1


class MaxRetryError(Exception):
    """Raised when maximum retries number exceeded"""


def retry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        attempt = 0
        while attempt < RETRIES:
            try:
                return func(*args, **kwargs)
            except Exception:  # pylint: disable=broad-except
                attempt += 1
                time.sleep(SLEEP_SEC)
        if attempt == RETRIES:
            raise MaxRetryError('Max retry number is exceeded')

    return wrapper


@retry
def retry_request(method, url, **kwargs):
    kwargs['timeout'] = kwargs.get('timeout', REQUEST_TIMEOUT)
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response
