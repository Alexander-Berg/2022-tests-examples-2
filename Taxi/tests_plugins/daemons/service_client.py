import uuid

import requests
from requests import structures

from taxi_tests import utils
from taxi_tests.utils import tracing


DEFAULT_USER_AGENT = 'yandex-taxi/3.18.0.7675 Android/6.0 (testenv client)'
DEFAULT_HEADERS = {
    'Accept-Language': 'en-US, en;q=0.8,ru;q=0.6',
    'User-Agent': DEFAULT_USER_AGENT,
}
DEFAULT_TIMEOUT = 120.0


class ServiceClient:
    """Basic http service client."""

    def __init__(
            self,
            base_url,
            *,
            service_headers=None,
            timeout=DEFAULT_TIMEOUT,
            session=None,
    ):
        self.base_url = base_url
        self.service_headers = service_headers or {}
        self.timeout = timeout
        self.session = session or requests.session()

    def _request(
            self,
            http_method,
            path,
            headers=None,
            bearer=None,
            x_real_ip=None,
            **kwargs,
    ):
        url = '{}{}'.format(self.base_url, path)
        headers = _build_headers(
            headers,
            service_headers=self.service_headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
        )
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        return self.session.request(
            http_method, url, headers=headers, **kwargs,
        )

    def post(
            self,
            method,
            json=None,
            data=None,
            params=None,
            bearer=None,
            x_real_ip=None,
            headers=None,
            files=None,
            **kwargs,
    ):
        return self._request(
            'POST',
            method,
            json=json,
            data=data,
            params=params,
            headers=headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
            files=files,
            **kwargs,
        )

    def put(
            self,
            method,
            json=None,
            data=None,
            params=None,
            bearer=None,
            x_real_ip=None,
            headers=None,
            files=None,
            **kwargs,
    ):
        return self._request(
            'PUT',
            method,
            json=json,
            data=data,
            params=params,
            headers=headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
            files=files,
            **kwargs,
        )

    def patch(
            self,
            method,
            json=None,
            data=None,
            params=None,
            bearer=None,
            x_real_ip=None,
            headers=None,
            files=None,
            **kwargs,
    ):
        return self._request(
            'PATCH',
            method,
            json=json,
            data=data,
            params=params,
            headers=headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
            files=files,
            **kwargs,
        )

    def get(self, method, headers=None, bearer=None, x_real_ip=None, **kwargs):
        return self._request(
            'GET',
            method,
            headers=headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
            **kwargs,
        )

    def delete(
            self, method, headers=None, bearer=None, x_real_ip=None, **kwargs,
    ):
        return self._request(
            'DELETE',
            method,
            headers=headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
            **kwargs,
        )

    def options(
            self, method, headers=None, bearer=None, x_real_ip=None, **kwargs,
    ):
        return self._request(
            'OPTIONS',
            method,
            headers=headers,
            bearer=bearer,
            x_real_ip=x_real_ip,
            **kwargs,
        )


class ServiceClientTestsControl(ServiceClient):
    """Fastcgi client for services with tests/control method support.

    Performs lazy call to tests/control on first service call.
    """

    def __init__(self, base_url, *, mocked_time, **kwargs):
        """
        :param base_url: Base service URL.
        :param now: Current time
        """
        super(ServiceClientTestsControl, self).__init__(base_url, **kwargs)
        self._caches_invalidated = True
        self._mocked_time = mocked_time

    def _prepare(self):
        if self._caches_invalidated:
            self.invalidate_caches(now=self._mocked_time.now)

    def _request(
            self,
            http_method,
            path,
            headers=None,
            bearer=None,
            x_real_ip=None,
            **kwargs,
    ):
        self._prepare()
        return super(ServiceClientTestsControl, self)._request(
            http_method, path, headers, bearer, x_real_ip, **kwargs,
        )

    def tests_control(
            self,
            now=None,
            invalidate_caches=True,
            clean_update=True,
            workers=None,
    ):
        if now is None:
            now = self._mocked_time.now
        if workers is None:
            workers = []

        response = self.post(
            'tests/control',
            {
                'now': utils.timestring(now),
                'invalidate_caches': invalidate_caches,
                'cache_clean_update': clean_update,
                'run_workers': workers,
            },
        )
        assert response.status_code == 200

    def invalidate_caches(self, now=None, clean_update=True):
        if clean_update:
            self._caches_invalidated = False
        self.tests_control(
            now=now, invalidate_caches=True, clean_update=clean_update,
        )

    def run_workers(self, workers):
        self.tests_control(workers=workers)


def _build_headers(
        user_headers=None, service_headers=None, bearer=None, x_real_ip=None,
):
    if service_headers is None:
        service_headers = {}
    headers = structures.CaseInsensitiveDict()
    headers.update(DEFAULT_HEADERS)
    headers.update(service_headers)
    if user_headers:
        headers.update(user_headers)
    if bearer:
        headers['Authorization'] = 'Bearer %s' % bearer
    if x_real_ip:
        headers['X-Real-IP'] = x_real_ip
    if tracing.SPAN_ID_HEADER not in headers:
        headers[tracing.SPAN_ID_HEADER] = uuid.uuid4().hex
    return headers
