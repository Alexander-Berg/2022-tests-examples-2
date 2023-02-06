# pylint: disable=redefined-outer-name
# pylint: disable=deprecated-method
# pylint: disable=invalid-name
# pylint: disable=bad-continuation
import collections
import functools
import os
import sys
import typing

import aiohttp.web
import pytest
import yarl

sys.path = [
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../backend-py3'),
    ),
] + sys.path

CONTENT_TYPE_HEADER = 'Content-Type'

SUBMODULES_TO_USE = ('testsuite',)

MOCKSERVER_PATTERN = '$mockserver'
MOCKSERVER_HTTPS_PATTERN = '$mockserver_https'

pytest_plugins = [
    # Testsuite plugins
    'testsuite.pytest_plugin',
]

sys.path = [
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'submodules', submodule_name),
    )
    for submodule_name in SUBMODULES_TO_USE
] + sys.path

from taxi.clients import http_client  # noqa  # pylint: disable=E0401,C0413
from taxi.util import callinfo  # noqa  # pylint: disable=E0401,C0413


@pytest.fixture
def stub():
    """Stub fixture.

    Provides function that takes only keyword arguments `**kw` and
    creates stub object which attributes are `kw` keys.

    Usage:

        def test_something(stub):
            obj = stub(x=1, get_x=lambda: return 2)
            assert obj.x == 1
            assert obj.get_x() == 2

    :return: Function that creates stub objects.
    """
    # pylint: disable=unnecessary-lambda
    return lambda **kw: collections.namedtuple('Stub', kw.keys())(**kw)


@pytest.fixture
def mock(monkeypatch):
    """Help to mock objects.

    Usage:

        def test_something(mock):
            @mock
            def foo(x, y=1, *a, **kw):
                return x + y + sum(a) + sum(kw.values())

            assert foo(1, 2) == 3
            assert foo(5) == 6
            assert foo(3, y=4) == 7
            assert foo(10, 20, 300, 400, plus=1000) == 1730

            # `call` pops information about first call
            assert foo.call == {'x': 1, 'y': 2, 'a': (), 'kw': {}}
            assert foo.call == {'x': 5, 'y': 1, 'a': (), 'kw': {}}

            # `calls` pops all calls information
            assert foo.calls == [
                {'x': 3, 'y': 4, 'a': (), 'kw': {}},
                {'x': 10, 'y': 20, 'a': (300, 400), 'kw': {'plus': 1000}},
            ]

            # When no information left...
            assert foo.call is None
            assert foo.calls == []

    """

    def wrapper(func):
        return functools.wraps(func)(callinfo.CallsInfoWrapper(func))

    return wrapper


@pytest.fixture
def patch(mock, monkeypatch):
    """Monkey patch helper.

    Usage:

        @patch('full.path.to.func')
        def func(*args, **kwargs):
            return (args, kwargs)

        assert foo(1, x=2) == ((1,), {'x': 2})
        assert foo.calls == [{'args': (1,), 'kwargs': {'x': 2}}]

    """

    def dec_generator(full_func_path):
        def dec(func):
            mocked = mock(func)
            monkeypatch.setattr(full_func_path, mocked)
            return mocked

        return dec

    return dec_generator


@pytest.fixture(autouse=True)
def session_request_mock(
        request, mock, monkeypatch, mockserver, mockserver_ssl,
):
    marker = request.node.get_closest_marker('not_mock_request')
    if marker:
        yield None
    else:
        session = SessionRequestMock(
            mock, monkeypatch, mockserver.base_url, mockserver_ssl.base_url,
        )
        yield session
        missed_requests = session.missed_requests
        if missed_requests:
            raise RuntimeError(
                'Several requests was not mocked up: %s' % missed_requests,
            )


@pytest.fixture
def response_mock():
    return Response


@pytest.fixture
def patch_aiohttp_session(session_request_mock):
    def wrapper(base_url, method=None):
        def wraps(func):
            func = session_request_mock.wrap_handler(base_url, method, func)
            return func

        return wraps

    return wrapper


class SessionRequestMock:
    class RequestWrapper:
        def __init__(self, coro):
            self._coro = coro

        def __await__(self):
            return self._coro.__await__()

    def __init__(
            self,
            mock,
            monkeypatch,
            mockserver_base_url,
            mockserver_ssl_base_url,
    ):
        self._monkeypatch = monkeypatch
        self._mock = mock
        self._handlers = collections.defaultdict(dict)
        self._mockserver_base_url = mockserver_base_url
        self._mockserver_ssl_base_url = mockserver_ssl_base_url
        self.missed_requests = []
        ClientSession = aiohttp.client.ClientSession
        HTTPClient = http_client.HTTPClient
        self._original = ClientSession._request  # pylint: disable=W0212
        self._original_hclient = HTTPClient._request  # pylint: disable=W0212
        monkeypatch.setattr('aiohttp.client.ClientSession._request', self)
        monkeypatch.setattr(
            'taxi.clients.http_client.HTTPClient._request', self,
        )
        self._ignored_hosts = ['127.0.0.1', 'localhost']

    def __get__(self, instance, owner):
        async def request(method, url, **kwargs):
            url = self._replace_mockserver(url)
            if self._is_url_ignored(url):
                if isinstance(instance, http_client.HTTPClient):
                    with self._monkeypatch.context() as monkey:
                        monkey.setattr(
                            'aiohttp.client.ClientSession._request',
                            self._original,
                        )
                        return await self._original_hclient(
                            instance, method, url, **kwargs,
                        )
                return await self._original(instance, method, url, **kwargs)

            return await self.RequestWrapper(
                self._request(method, url, **kwargs),
            )

        return request

    def _replace_mockserver(self, url: typing.Union[str, yarl.URL]) -> str:
        if isinstance(url, yarl.URL):
            url = str(url)
        pattern = None
        base_url = ''
        if url.startswith(MOCKSERVER_HTTPS_PATTERN):
            pattern = MOCKSERVER_HTTPS_PATTERN
            base_url = self._mockserver_ssl_base_url
        elif url.startswith(MOCKSERVER_PATTERN):
            pattern = MOCKSERVER_PATTERN
            base_url = self._mockserver_base_url
        if pattern:
            # TODO(dmkurilov)  replace with correct solution
            path = url[len(pattern) :].lstrip('/')
            base_url = base_url.rstrip('/')
            url = '%s/%s' % (base_url, path)
        return url

    def _is_url_ignored(self, url):
        if not isinstance(url, yarl.URL):
            url = yarl.URL(url)
        return url.host in self._ignored_hosts

    async def _request(self, method, url, **kwargs):
        if not self._handlers:
            self.missed_requests.append((method, url))
            return None
        suitable_urls = [
            url
            for url, handlers in self._handlers.items()
            if method.lower() in handlers or None in handlers
        ]
        if not suitable_urls:
            self.missed_requests.append((method, url))
            return None
        sorted_urls = sorted(
            suitable_urls,
            key=functools.partial(self._common_prefix_length, str(url)),
            reverse=True,
        )
        requested_url = sorted_urls[0]
        method = method.lower()
        handlers = self._handlers[requested_url]
        method_handler = handlers.get(method)

        if method_handler is not None:
            return method_handler(method, url, **kwargs)

        default_handler = handlers.get(None)
        if default_handler:
            return default_handler(method, url, **kwargs)

        return None

    @staticmethod
    def _common_prefix_length(first_string, second_string):
        i = -1
        for i, (first, second) in enumerate(zip(first_string, second_string)):
            if first != second:
                return i
        return i + 1

    def wrap_handler(self, base_url, method, handler):
        handler = self._mock(handler)
        if method:
            method = method.lower()
        self._handlers[base_url][method] = handler
        return handler


class Response:  # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            text=None,
            json=None,
            read=None,
            status=200,
            url=yarl.URL('http://dummy/url'),
            method=None,
            headers=None,
            request_info=None,
    ):
        self._text = text
        self._json = json
        self._read = read
        self.status = status
        self.url = url
        self.method = method
        if headers is None:
            self.headers = {CONTENT_TYPE_HEADER: 'application/json'}
        else:
            self.headers = headers
        self._request_info = request_info
        self.content_length = 1

    async def text(self):
        assert self._read is None
        return self._text

    async def json(self, content_type=None):
        return self._json

    async def read(self):
        return self._read

    def release(self):
        pass

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(
                request_info=None,
                history=None,
                code=self.status,
                message=self._text,
            )

    @property
    def request_info(self):
        return self._request_info

    @property
    def content_type(self):
        if CONTENT_TYPE_HEADER in self.headers:
            return self.headers[CONTENT_TYPE_HEADER]
        return 'application/json'
