from __future__ import unicode_literals

import logging
import posixpath
import requests
import time

from sandbox.projects.common import decorators


logger = logging.getLogger(__name__)


def sleep_on_too_many_requests(n_try, e, current_delay):
    if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == requests.codes.too_many_requests:
        time.sleep(min(current_delay * n_try, 30))


class TestenvApiClientError(requests.RequestException):
    pass


class _TestenvApiHandler(object):
    """Base API handler object."""

    def __init__(
        self,
        token=None,
        base_url='https://testenv.yandex-team.ru/api/te/v1.0',
        path=(),
        timeout=180,
        log_raw_response=False,
        no_retry_client_errors=False,
    ):
        self.__token = token
        self.__base_url = base_url
        self.__path = list(path)
        self.__timeout = timeout

        self._log_raw_response = log_raw_response
        self._no_retry_client_errors = no_retry_client_errors

    @property
    def url(self):
        return posixpath.join(*(url_part for url_part in [self.__base_url] + [p.lstrip('/') for p in self.__path]))

    def __do_request(self, method, **kwargs):
        """
        Perform authorized request to API.

        All keyword arguments will be passed to a `requests` method (GET, POST, etc) directly.
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.__token:
            headers["Authorization"] = "OAuth {}".format(self.__token)
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        timeout = self.__timeout if 'timeout' not in kwargs else kwargs.pop('timeout')
        kwargs.setdefault('allow_redirects', True)
        logger.debug("Requesting %s %s with timeout=%s and parameters %s", method, self.url, timeout, kwargs)
        r = getattr(requests, method.lower())(
            self.url,
            headers=headers,
            timeout=timeout,
            **kwargs  # noqa (py3)
        )
        logger.debug("Got %s\n%s", r.status_code, '\n'.join(['{}: {}'.format(k, v) for k, v in r.headers.items()]))

        if self._log_raw_response:
            logger.info("Response content: %s", r.content)

        try:
            if self._no_retry_client_errors and 400 <= r.status_code < 500:
                raise TestenvApiClientError('{} Client Error: {}'.format(r.status_code, r.reason), response=r)
            else:
                r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                "Got %s response from %s with timeout=%s and parameters %s. Error: %s:\n%s\n\n",
                r.status_code, self.url, timeout, kwargs, e, r.content,
            )

            # try to parse API response
            try:
                error = r.json()
                logger.error('TestEnv says `%s`, traceback:\n%s', error.get('message'), error.get('traceback'))
            except Exception as he:
                logger.error('Cannot parse TestEnv json response: %s', he)

            raise e
        res = r.json()
        return res

    def _get_handler(self, name):
        return _TestenvApiHandler(
            token=self.__token,
            base_url=self.__base_url,
            path=self.__path + [name],
            timeout=self.__timeout,
            log_raw_response=self._log_raw_response,
            no_retry_client_errors=self._no_retry_client_errors,
        )

    def __getitem__(self, name):
        return self._get_handler(name)

    # Methods
    @decorators.retries(5, delay=5, exceptions=(requests.exceptions.HTTPError, ), hook=sleep_on_too_many_requests)
    def GET(self, **kwargs):
        return self.__do_request(method='GET', **kwargs)

    def POST(self, **kwargs):
        return self.__do_request(method='POST', **kwargs)

    def PUT(self, **kwargs):
        return self.__do_request(method='PUT', **kwargs)

    def PATCH(self, **kwargs):
        return self.__do_request(method='PATCH', **kwargs)

    def DELETE(self, **kwargs):
        return self.__do_request(method='DELETE', **kwargs)


class TestenvApiClient(_TestenvApiHandler):
    """
    Based on https://testenv.yandex-team.ru/api/te/v1.0/documentation docs.

    Usage:
    >>> TestenvApiClient().projects.GET(params=dict(type='custom_check', status='working', name='yabs-2.0'))
    [
        {
            "status": "working",
            "comment": "started automatically",
            "name": "yabs-2.0",
            "shard": "production",
            "task_owner": "YABS_SERVER_SANDBOX_TESTS",
            "project_type": "custom_check"
        },
        ...
    ]
    """

    # Handler aliases
    @property
    def projects(self):
        return self._get_handler('projects/')

    @property
    def arcadia(self):
        return self._get_handler('arcadia/')

    @property
    def autocheck(self):
        return self._get_handler('autocheck/')

    @property
    def constants(self):
        return self._get_handler('constants/')

    @property
    def default(self):
        return self._get_handler('default/')

    @property
    def system_info(self):
        return self._get_handler('system_info/')

    @property
    def sandbox(self):
        return self._get_handler('sandbox/')

    @property
    def svn(self):
        return self._get_handler('svn/')
