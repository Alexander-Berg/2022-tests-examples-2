import contextlib
import datetime
import sys
import time

import aiohttp.web
import pytest

from taxi_tests import http
from taxi_tests.utils import callinfo
from taxi_tests.utils import net as net_utils
from taxi_tests.utils import session_context
from taxi_tests.utils import tracing
from taxi_tests.utils import tskv

pytest_plugins = ['taxi_tests.plugins.tracing']

REQUEST_FROM_ANOTHER_TEST_ERROR = 'Internal error: request is from other test'


class BaseError(Exception):
    """Base class for exceptions from this module."""


class MockServerError(BaseError):
    pass


class HandlerNotFoundError(MockServerError):
    pass


class Handler:
    def __init__(self, func, *, raw_request=False, json_response=False):
        self.callqueue = callinfo.acallqueue(func)
        self.raw_request = raw_request
        self.json_response = json_response

    async def __call__(self, request):
        if not self.raw_request:
            request = await http.wrap_request(request)
        response = await self.callqueue(request)
        if not self.json_response:
            return response
        if isinstance(response, aiohttp.web.Response):
            return response
        return http.make_response(json=response)


class Session:
    def __init__(self):
        self.handlers = {}
        self.failures = []
        self.prefix_handlers = {}

    def add_failure(self, request, error):
        self.failures.append((request, error))

    def get_handler(self, path):
        if path in self.handlers:
            return self.handlers[path]
        for prefix in self.prefix_handlers:
            if path.startswith(prefix):
                return self.prefix_handlers[prefix]
        raise HandlerNotFoundError

    async def handle_request(self, request):
        try:
            handler = self.get_handler(request.path)
            response = await handler(request)
            if isinstance(response, aiohttp.web.Response):
                return response
            raise MockServerError(
                'aiohttp.web.Response instance is expected '
                f'{response!r} given')
        except HandlerNotFoundError:
            raise
        except Exception as exc:
            self.add_failure(request, exc)
            raise

    def register_handler(self, path, func, prefix=False):
        if prefix:
            handlers = self.prefix_handlers
        else:
            handlers = self.handlers
        handlers[path] = func
        return func

    def handle_failures(self, message):
        if not self.failures:
            return
        failures, self.failures = self.failures, []
        message = [message, '']
        failure_messages = set()
        cause = None
        for request, failure in failures:
            if isinstance(failure, HandlerNotFoundError):
                text = 'perhaps you forget to setup mockserver handler'
            else:
                text = repr(failure)
                if cause is None:
                    cause = failure
            failure_messages.add(' * {}: {}'.format(request.path, text))
        message += sorted(failure_messages)
        raise MockServerError('\n'.join(message)) from cause


class HandlerInstaller:
    def __init__(self, server, session):
        self._server = server
        self._session = session

    @property
    def base_url(self):
        return self._server.base_url

    @property
    def host(self):
        return self._server.host

    @property
    def port(self):
        return self._server.port

    def handler(self, path, prefix=False, raw_request=False,
                json_response=False):
        def decorator(func):
            handler = Handler(
                func, raw_request=raw_request, json_response=json_response,
            )
            self._session.register_handler(
                path, handler, prefix=prefix,
            )
            return handler.callqueue
        return decorator

    def json_handler(self, path, prefix=False, raw_request=False):
        return self.handler(
            path, prefix=prefix, raw_request=raw_request, json_response=True)

    def url(self, url):
        return self.base_url + url

    @contextlib.contextmanager
    def ignore_trace_id(self):
        # pylint: disable=protected-access
        trace_id = self._server._trace_id
        try:
            self._server._trace_id = None
            yield
        finally:
            self._server._trace_id = trace_id

    make_response = staticmethod(http.make_response)


# pylint: disable=too-many-instance-attributes
class Server:
    session = None

    def __init__(self, sock, *, nofail=False, notrace=False):
        sock_address = sock.getsockname()
        self.host, self.port = 'localhost', sock_address[1]
        self.base_url = 'http://%s:%d/' % (self.host, self.port)
        self._sock = sock
        self._nofail = nofail
        self._notrace = notrace
        self._trace_id = None

    @contextlib.contextmanager
    def new_session(self, trace_id: str):
        self._trace_id = trace_id
        self.session = Session()
        try:
            yield self.session
        finally:
            session = self.session
            self.session = None
            self._trace_id = None
            session.handle_failures('Mockserver failure')

    async def loop_attach(self, loop):
        request_handler = self._handle_request if self._notrace else (
            self._trace_handle_request
        )
        server = aiohttp.web.Server(request_handler, loop=loop)
        # create per test socket duplicate
        loop_server = await loop.create_server(server, sock=self._sock.dup())
        return loop_server

    async def _trace_handle_request(self, request):
        trace_id = request.headers.get(tracing.TRACE_ID_HEADER)
        started = time.perf_counter()
        fields = [
            ('type', 'mockserver_request'),
            ('timestamp', datetime.datetime.utcnow()),
            ('method', request.method),
            ('url', request.url),
        ]
        if trace_id:
            fields.append(('trace_id', trace_id))
        try:
            response = await self._handle_request(request)
            fields.extend([
                ('meta_code', response.status),
                ('status', 'DONE'),
            ])
            return response
        except BaseException as exc:
            fields.extend([
                ('status', 'FAIL'),
                ('exc_info', str(exc)),
            ])
            raise
        finally:
            delay_ms = 1000 * (time.perf_counter() - started)
            fields.append(('delay', f'{delay_ms:.3f}ms'))
            print(
                tskv.items_to_tskv(fields, add_header=False),
                file=sys.stderr)

    async def _handle_request(self, request):
        trace_id = request.headers.get(tracing.TRACE_ID_HEADER)
        if not self.session:
            error_message = 'Internal error: missing mockserver fixture'
            if self._nofail or not tracing.is_from_client_fixture(trace_id):
                return _internal_error(error_message)
            raise MockServerError(error_message)

        if tracing.is_other_test(trace_id, self._trace_id):
            return _internal_error(REQUEST_FROM_ANOTHER_TEST_ERROR)
        try:
            return await self.session.handle_request(request)
        except HandlerNotFoundError as exc:
            if self._nofail or not tracing.is_from_client_fixture(trace_id):
                return _internal_error(
                    'Internal error: mockserver handler not found',
                )
            self.session.add_failure(request, exc)
            raise


def pytest_addoption(parser):
    group = parser.getgroup('mockserver')
    group.addoption('--mockserver-nofail', action='store_true',
                    help='Do not fail if no handler is set.')
    group.addoption('--mockserver-notrace', action='store_true',
                    help='Do not print mockserver request / response log.')
    group.addoption('--mockserver-host', default='localhost',
                    help='Default host for mockserver.')
    group.addoption('--mockserver-port', default=9999, type=int,
                    help='Default port for mockserver.')


@pytest.fixture
async def mockserver(pytestconfig, _mockserver, loop, trace_id):
    server = await _mockserver.loop_attach(loop)
    with _mockserver.new_session(trace_id) as session:
        try:
            yield HandlerInstaller(_mockserver, session)
        finally:
            server.close()
            await server.wait_closed()


@pytest.fixture(scope='session', autouse=True)
def _mockserver(pytestconfig, testsuite_session_context, worker_id):
    if worker_id == 'master':
        sock = net_utils.bind_socket(
            pytestconfig.option.mockserver_host,
            pytestconfig.option.mockserver_port,
        )
    else:
        sock = net_utils.bind_socket()
    server = Server(
        sock,
        nofail=pytestconfig.option.mockserver_nofail,
        notrace=pytestconfig.option.mockserver_notrace,
    )
    testsuite_session_context.mockserver = session_context.MockserverInfo(
        host=server.host,
        port=server.port,
        base_url=server.base_url,
    )
    with contextlib.closing(sock):
        yield server


def _internal_error(message='Internal error'):
    return http.make_response(message, status=500)
