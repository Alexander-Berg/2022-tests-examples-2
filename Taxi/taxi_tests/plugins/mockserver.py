import contextlib
import datetime
import sys
import time
import traceback

import aiohttp.web
import pytest

from taxi_tests import http
from taxi_tests.utils import callinfo
from taxi_tests.utils import net as net_utils
from taxi_tests.utils import session_context
from taxi_tests.utils import tracing

pytest_plugins = ['taxi_tests.plugins.tracing']

REQUEST_FROM_ANOTHER_TEST_ERROR = 'Internal error: request is from other test'

_MISSING_HANDLER_ERROR = (
    'perhaps you forget to setup mockserver handler, use --mockserver-nofail '
    'to suppress these errors{}'
)
_SUPPORTED_ERRORS_HEADER = 'X-Testsuite-Supported-Errors'
_ERROR_HEADER = 'X-Testsuite-Error'

_LOGGER_HEADERS = (
    ('X-YaTraceId', 'trace_id'),
    ('X-YaSpanId', 'span_id'),
    ('X-YaRequestId', 'link'),
)


class BaseError(Exception):
    """Base class for exceptions from this module."""


class MockServerError(BaseError):
    pass


class HandlerNotFoundError(MockServerError):
    def __init__(self, tracing_enabled):
        self.tracing_enabled = tracing_enabled
        super().__init__()


class Handler:
    def __init__(self, func, *, raw_request=False, json_response=False):
        self.orig_func = func
        self.callqueue = callinfo.acallqueue(func)
        self.raw_request = raw_request
        self.json_response = json_response

    def __repr__(self):
        return (
            f'mockserver.Handler({self.orig_func!r}, '
            f'raw_request={self.raw_request}, '
            f'json_response={self.json_response})'
        )

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
    def __init__(self, reporter=None, tracing_enabled=True):
        self.reporter = reporter
        self.tracing_enabled = tracing_enabled
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
        raise HandlerNotFoundError(self.tracing_enabled)

    async def handle_request(self, request):
        try:
            handler = self.get_handler(request.path)
            response = await handler(request)
            if isinstance(response, aiohttp.web.Response):
                return response
            raise MockServerError(
                'aiohttp.web.Response instance is expected '
                f'{response!r} given',
            )
        except HandlerNotFoundError:
            raise
        except http.MockedError as exc:
            return _mocked_error_response(request, exc.error_code)
        except Exception as exc:
            exc_info = sys.exc_info()
            self.add_failure(request, exc)
            self._report_handler_failure(request, exc_info, handler)
            raise

    def _report_handler_failure(self, request, exc_info, handler):
        if self.reporter:
            self.reporter.write_line('Mockserver handler failed.', red=True)
            self.reporter.write_line('')
            self.reporter.write_line(
                f'{handler} crashed while responding to {request.url}',
                red=True,
            )
            self.reporter.write_line('')
            for line in traceback.format_exception(*exc_info):
                self.reporter.write(line, red=True)

    def register_handler(self, path, func, prefix=False):
        path = _normalize_mockserver_path(path)
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
        failure_messages = set()
        cause = None
        for request, failure in failures:
            if isinstance(failure, HandlerNotFoundError):
                text = _MISSING_HANDLER_ERROR.format(
                    ' (tracing enabled)' if failure.tracing_enabled else '',
                )
            else:
                text = repr(failure)
            if cause is None:
                cause = failure
            failure_messages.add(f' * {request.path}: {text}')
        messages = [message, *sorted(failure_messages)]
        raise MockServerError('\n'.join(messages)) from cause


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

    def handler(
            self, path, prefix=False, raw_request=False, json_response=False,
    ):
        def decorator(func):
            handler = Handler(
                func, raw_request=raw_request, json_response=json_response,
            )
            self._session.register_handler(path, handler, prefix=prefix)
            return handler.callqueue

        return decorator

    def json_handler(self, path, prefix=False, raw_request=False):
        return self.handler(
            path, prefix=prefix, raw_request=raw_request, json_response=True,
        )

    def url(self, url):
        return self.base_url + url

    def ignore_trace_id(self):
        return self.tracing(False)

    @contextlib.contextmanager
    def tracing(self, value: bool = True):
        original_value = self._session.tracing_enabled
        try:
            self._session.tracing_enabled = value
            yield
        finally:
            self._session.tracing_enabled = original_value

    def get_callqueue_for(self, path):
        return self._session.get_handler(path).callqueue

    make_response = staticmethod(http.make_response)

    TimeoutError = http.TimeoutError
    NetworkError = http.NetworkError


# pylint: disable=too-many-instance-attributes
class Server:
    session = None

    def __init__(
            self,
            sock,
            *,
            logger=None,
            nofail=False,
            reporter=None,
            tracing_enabled=True,
    ):
        sock_address = sock.getsockname()
        self.host, self.port = 'localhost', sock_address[1]
        self.base_url = 'http://%s:%d/' % (self.host, self.port)
        self._logger = logger
        self._sock = sock
        self._nofail = nofail
        self._trace_id = None
        self._reporter = reporter
        self._tracing_enabled = tracing_enabled

    @property
    def tracing_enabled(self) -> bool:
        if self.session is None:
            return self._tracing_enabled
        return self.session.tracing_enabled

    def get_info(self):
        return session_context.MockserverInfo(
            host=self.host, port=self.port, base_url=self.base_url,
        )

    @contextlib.contextmanager
    def new_session(self, trace_id: str):
        self._trace_id = trace_id
        self.session = Session(self._reporter, self._tracing_enabled)
        try:
            yield self.session
        finally:
            session = self.session
            self.session = None
            self._trace_id = None
            session.handle_failures('Mockserver failure')

    async def loop_attach(self, loop):
        server = aiohttp.web.Server(self._trace_handle_request, loop=loop)
        # create per test socket duplicate
        loop_server = await loop.create_server(server, sock=self._sock.dup())
        return loop_server

    async def _trace_handle_request(self, request):
        if not self._logger:
            return await self._handle_request(request)

        started = time.perf_counter()
        fields = {
            '_type': 'mockserver_request',
            'timestamp': datetime.datetime.utcnow(),
            'level': 'INFO',
            'method': request.method,
            'url': request.url,
        }
        for header, key in _LOGGER_HEADERS:
            if header in request.headers:
                fields[key] = request.headers[header]
        try:
            response = await self._handle_request(request)
            fields['meta_code'] = response.status
            fields['status'] = 'DONE'
            return response
        except BaseException as exc:
            fields['level'] = 'ERROR'
            fields['status'] = 'FAIL'
            fields['exc_info'] = str(exc)
            raise
        finally:
            delay_ms = 1000 * (time.perf_counter() - started)
            fields['delay'] = f'{delay_ms:.3f}ms'
            self._logger.log_entry(fields)

    async def _handle_request(self, request):
        trace_id = request.headers.get(tracing.TRACE_ID_HEADER)
        nofail = (
            self._nofail
            or self.tracing_enabled
            and not tracing.is_from_client_fixture(trace_id)
        )
        if not self.session:
            error_message = 'Internal error: missing mockserver fixture'
            if nofail:
                return _internal_error(error_message)
            raise MockServerError(error_message)

        if self.tracing_enabled and tracing.is_other_test(
                trace_id, self._trace_id,
        ):
            self._report_other_test_request(request, trace_id)
            return _internal_error(REQUEST_FROM_ANOTHER_TEST_ERROR)
        try:
            return await self.session.handle_request(request)
        except HandlerNotFoundError as exc:
            self._report_handler_not_found(request)
            if nofail:
                return _internal_error(
                    'Internal error: mockserver handler not found',
                )
            self.session.add_failure(request, exc)
            raise

    def _report_handler_not_found(self, request):
        if self._reporter:
            self._reporter.write_line(
                f'Mockserver handler not installed for path {request.path}',
                red=True,
            )

    def _report_other_test_request(self, request, trace_id):
        if self._reporter:
            self._reporter.write_line(
                f'Mockserver called path {request.path} with previous test '
                f'trace_id {trace_id}',
                yellow=True,
            )


def pytest_addoption(parser):
    group = parser.getgroup('mockserver')
    group.addoption(
        '--mockserver-nofail',
        action='store_true',
        help='Do not fail if no handler is set.',
    )
    group.addoption(
        '--mockserver-host',
        default='localhost',
        help='Default host for mockserver.',
    )
    group.addoption(
        '--mockserver-port',
        type=int,
        default=0,
        help=(
            'Mockserver port for default (master) worker. Set 0 to use random '
            'port. NOTE: non-default workers always use random port.'
        ),
    )
    parser.addini(
        'mockserver-tracing-enabled',
        type='bool',
        default=True,
        help=(
            'When request trace-id header not from testsuite:\n'
            '  True: handle, if handler missing return http status 500\n'
            '  False: handle, if handler missing raise '
            'HandlerNotFoundError\n'
            'When request trace-id header from other test:\n'
            '  True: do not handle, return http status 500\n'
            '  False: handle, if handler missing raise HandlerNotFoundError'
        ),
    )


@pytest.fixture
async def mockserver(pytestconfig, _mockserver, loop, trace_id):
    server = await _mockserver.loop_attach(loop)
    with _mockserver.new_session(trace_id) as session:
        try:
            yield HandlerInstaller(_mockserver, session)
        finally:
            server.close()
            await server.wait_closed()


@pytest.fixture(scope='session')
def mockserver_info(_mockserver):
    return _mockserver.get_info()


@pytest.fixture(scope='session', autouse=True)
def _mockserver(
        pytestconfig, testsuite_session_context, worker_id, testsuite_logger,
):
    reporter = pytestconfig.pluginmanager.get_plugin('terminalreporter')
    port = pytestconfig.option.mockserver_port if worker_id == 'master' else 0
    sock = net_utils.bind_socket(pytestconfig.option.mockserver_host, port)
    server = Server(
        sock,
        logger=testsuite_logger,
        nofail=pytestconfig.option.mockserver_nofail,
        reporter=reporter,
        tracing_enabled=pytestconfig.getini('mockserver-tracing-enabled'),
    )
    testsuite_session_context.mockserver = server.get_info()

    with contextlib.closing(sock):
        yield server


def _internal_error(message='Internal error'):
    return http.make_response(message, status=500)


def _mocked_error_response(request, error_code):
    if _SUPPORTED_ERRORS_HEADER not in request.headers:
        raise MockServerError(
            'Service does not support mockserver errors protocol',
        )
    supported_errors = request.headers[_SUPPORTED_ERRORS_HEADER].split(',')
    if error_code not in supported_errors:
        raise MockServerError(
            f'Service does not support mockserver error of type {error_code}',
        )
    return http.make_response(
        response='', status=599, headers={_ERROR_HEADER: error_code},
    )


def _normalize_mockserver_path(path):
    if not path.startswith('/'):
        return '/' + path
    return path
