# -*- coding: utf-8 -*-
import json
import logging
import re
import socket
import time
import traceback
from multiprocessing.pool import ThreadPool
from random import choice
from string import ascii_letters
from urlparse import urlparse

import allure
from furl import furl
from hamcrest import equal_to
from requests import Session, Request
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.connection import HTTPConnection

from common import env

logger = logging.getLogger(__name__)


def create_curl(request):
    curl = "curl --compressed -vLskX {method} '{url}'" \
        .format(method=request.method, url=request.url)

    if request.headers:
        curl += ' ' + ' '.join(["-H '{name}: {value}'".format(name=name, value=value)
                                for name, value in request.headers.iteritems()])

    if request.body:
        curl += " -d '{body}'".format(body=request.body)

    return curl


def create_request_info(r):
    parsed_url = urlparse(r.url)
    return '{method} {path} HTTP 1.1\nHost: {hostname}\n{headers}'.format(
        method=r.request.method,
        path=parsed_url.path,
        hostname=parsed_url.hostname,
        headers='\n'.join(['{}: {}'.format(name, value) for name, value in r.request.headers.iteritems()])
    )


def create_response_info(r):
    info = 'HTTP/1.1 {status} {reason}\n{headers}'.format(
        status=r.status_code,
        reason=r.reason,
        headers='\n'.join(['{name}: {value}'.format(name=name, value=value) for name, value in r.headers.iteritems()])
    )

    content = r.content
    content_type = r.headers.get('Content-Type', None)
    if content and content_type and 'image' not in content_type:
        try:
            data = r.json()
            info += '\n{}'.format(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False).encode('utf8'))
        except Exception:
            info += '\n{}'.format(content)

    return info


_default_hooks = set()


def _dns_override(self):
    hostname = self.host

    override = env.dns_override()
    for k, v in override.iteritems():
        if re.compile(k).match(self.host):
            hostname = v
            logger.debug('Remap {} to {}'.format(self.host, v))
            break

    try:
        conn = socket.create_connection(
            (hostname, self.port),
            self.timeout,
            self.source_address,
        )
    except AttributeError:  # Python 2.6
        conn = socket.create_connection(
            (hostname, self.port),
            self.timeout,
        )
    return conn


HTTPConnection._new_conn = _dns_override


def default_response_hook(func):
    _default_hooks.add(func)
    return func


@default_response_hook
def _log_request(response, *args, **kwargs):
    curl = create_curl(response.request)
    logger.debug('{curl} << status={status}, total_time={time}'.format(
        curl=curl,
        status=response.status_code,
        time=response.elapsed.microseconds / 1000
    ))


@default_response_hook
def _attach_request_info(response, *args, **kwargs):
    curl = create_curl(response.request)
    request_info = create_request_info(response)
    response_info = create_response_info(response)

    content = '---- CURL ----\n{curl}\n\n---- REQUEST -----\n{request}\n\n---- RESPONSE ----\n{response}' \
        .format(curl=curl, request=request_info, response=response_info)

    allure.attach(response.url, content)


class Req(Request):
    _kwargs = {}
    _rate_limit = 0

    @staticmethod
    def _log_failed_request(request):
        curl = create_curl(request)
        logger.error(curl)
        logger.error(traceback.format_exc())

    def __init__(self, url=None, method='GET', headers=None, files=None, data=None, params=None, auth=None,
                 cookies=None, hooks=None, json=None, session=None, step=None, **kwargs):
        super(Req, self).__init__(method, url, headers, files, data, params, auth, cookies, hooks, json)
        response_hooks = set(self.hooks.get('response'))
        response_hooks.update(_default_hooks)
        self.hooks['response'] = response_hooks
        if kwargs is None:
            kwargs = {}
        self._kwargs = kwargs
        self._kwargs['verify'] = 'certs/YandexInternalRootCA.pem'
        self._session = session if session is not None else Session()
        self.step = step
        self._rate_limit = env.rate_limit()

    def rh(self):
        if 'rh' not in self._kwargs:
            self._kwargs['rh'] = 1
        return self

    @staticmethod
    def get_random_rid():
        return ''.join(choice(ascii_letters) for i in range(15))

    def _do_send(self, session, safe=False):
        allow_redirects = self._kwargs.get('allow_redirects', True)
        loop_count = 2
        allow_retry = self._kwargs.get('allow_retry', False)
        if allow_retry:
            loop_count = self._kwargs.get('retries', loop_count)
        before_retry = self._kwargs.get('before_retry', 2)
        self.prepared_request = session.prepare_request(self)
        response = None
        for i in range(loop_count):
            try:
                start = time.clock()

                response = session.send(self.prepared_request,
                                        allow_redirects=allow_redirects,
                                        verify=False)

                if response is not None and allow_retry and response.status_code >= 400 and i < (loop_count - 1):
                    time.sleep(before_retry)
                    continue

                stop = time.clock()
                if self._rate_limit > 0:
                    exec_time = stop - start
                    sleep = 1.0 / self._rate_limit - exec_time
                    if sleep > 0:
                        time.sleep(sleep)

                return ReqResult(self, response)
            except Exception as e:
                self._log_failed_request(self.prepared_request)
                if not safe:
                    raise e
                return ReqResult(self, response, error=e)

    def send(self, session=None, safe=False):
        if session is None:
            session = self._session

        if 'rh' in self._kwargs:
            self.params['test_request_id'] = self.get_random_rid()

        if 'no_allure' in self._kwargs:
            self.hooks.get('response').remove(_attach_request_info)
            return self._do_send(session)

        step_name = self.step if self.step else self.method + ' ' + self.url

        with allure.step(step_name):
            return self._do_send(session, safe=safe)


class ReqResult(object):
    def __init__(self, request, response=None, error=None):
        self.request = request
        self.response = response
        self.error = error

    def is_ok(self, matcher=None):
        return not self.is_error(matcher)

    def is_error(self, matcher=None):
        if matcher is None:
            matcher = equal_to(200)
        return (self.error is not None) or not matcher._matches(self.response.status_code)

    def format_error(self):
        curl = create_curl(self.request.prepared_request)
        if self.error:
            return '{curl} -> {error}'.format(curl=curl, error=self.error.message)
        return '{curl} -> {status}'.format(curl=curl, status=self.response.status_code)

    def json(self):
        assert self.is_ok()
        try:
            return self.response.json()
        except ValueError:
            raise ValueError('JSON Encode Problem with JSON:<<<\n' + self.response.text + '\n<<<<')

    def text(self):
        return self.response.text()

    # FIXME: переделать на property по аналогии с headers
    def content(self):
        return self.response.content

    def get_headers(self):
        return self.response.headers

    headers = property(get_headers)


def get_request_results_parallel(urls, **kwargs):
    session = Session()
    adapter = HTTPAdapter(max_retries=5, pool_maxsize=100)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    pool = ThreadPool(8)

    def wrap_ping(url):
        return Req(url, no_allure=1, **kwargs).send(session)

    result = pool.map(wrap_ping, urls)
    pool.close()
    pool.join()
    session.close()
    return result


def resolve_dns(url):
    host = furl(url).host
    try:
        return socket.gethostbyname(host)
    except Exception:
        try:
            addr_info = socket.getaddrinfo(host, 0, socket.AF_INET6)
            if addr_info:
                return addr_info[0][4][0]
        except Exception:
            return None
