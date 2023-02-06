import pytest
from requests import exceptions

from taxi_tests.utils import log_requests

REPOSITION_HOST = 'http://reposition.taxi.yandex.net/'
TIMEOUT = 10
RETRIES = 2


class Reposition:
    @staticmethod
    def _method(method, url, *, params,
                retry_on_500=True, retry_on_timeout=True,
                **kwargs):
        params = {} if params is None else params.copy()
        for num in range(RETRIES):
            try:
                response = log_requests.request(
                    method, url,
                    timeout=TIMEOUT,
                    params=params,
                    **kwargs,
                )
                if response.status_code != 500 or not retry_on_500:
                    break
            except exceptions.ReadTimeout:
                if not retry_on_timeout or num >= (RETRIES - 1):
                    raise
        return response

    def post(self, path, json, *, params=None, headers=None):
        response = self._method(
            'post',
            REPOSITION_HOST + path,
            json=json,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def put(self, path, json, *, params=None, headers=None):
        response = self._method(
            'put',
            REPOSITION_HOST + path,
            json=json,
            params=params,
            headers=headers,
        )
        response.raise_for_status()

    def get(self, path, params=None, headers=None):
        response = self._method(
            'get',
            REPOSITION_HOST + path,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


@pytest.fixture
def reposition():
    return Reposition()
