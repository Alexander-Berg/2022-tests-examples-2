import contextlib
import datetime
import itertools
import logging
import ssl
import time
import typing
import uuid
import warnings

import aiohttp.web

from testsuite.utils import callinfo
from testsuite.utils import http
from testsuite.utils import net as net_utils
from testsuite.utils import url_util

from . import classes
from . import exceptions
from . import reporter_plugin

DEFAULT_TRACE_ID_HEADER = 'X-YaTraceId'
DEFAULT_SPAN_ID_HEADER = 'X-YaSpanId'

_TRACE_ID_PREFIX = 'testsuite-'

REQUEST_FROM_ANOTHER_TEST_ERROR = 'Internal error: request is from other test'

_SUPPORTED_ERRORS_HEADER = 'X-Testsuite-Supported-Errors'
_ERROR_HEADER = 'X-Testsuite-Error'

_LOGGER_HEADERS = (
    ('X-YaTraceId', 'trace_id'),
    ('X-YaSpanId', 'span_id'),
    ('X-YaRequestId', 'link'),
)

logger = logging.getLogger(__name__)


class Handler:
    def __init__(self, func, *, raw_request=False, json_response=False):
        self.orig_func = func
        self.callqueue = callinfo.acallqueue(func)
        self.raw_request = raw_request
        self.json_response = json_response

    def __repr__(self):
        return (
            f'{Handler.__module__}.{Handler.__name__}({self.orig_func!r}, '
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
    handlers: typing.Dict[str, Handler]
    prefix_handlers: typing.Dict[str, Handler]

    def __init__(
            self,
            reporter: typing.Optional[
                reporter_plugin.MockserverReporterPlugin
            ] = None,
            tracing_enabled=True,
            trace_id=None,
    ):
        if trace_id is None:
            trace_id = generate_trace_id()
        self.trace_id = trace_id
        self.reporter = reporter
        self.tracing_enabled = tracing_enabled
        self.handlers = {}
        self.prefix_handlers = {}

    def get_handler(self, path):
        if path in self.handlers:
            return self.handlers[path]
        for prefix in self.prefix_handlers:
            if path.startswith(prefix):
                return self.prefix_handlers[prefix]
        raise exceptions.HandlerNotFoundError(
            self._get_handler_not_found_message(path),
        )

    def _get_handler_not_found_message(self, path: str) -> str:
        if self.tracing_enabled:
            tracing_state = 'enabled'
        else:
            tracing_state = 'disabled'
        handlers = itertools.chain(
            (path for path in self.handlers),
            (path + '*' for path in self.prefix_handlers),
        )
        handlers_list = '\n'.join(f'- {path}' for path in handlers)
        return (
            f'Mockserver handler is not installed for {path!r}.\n'
            'Perhaps you forgot to setup mockserver handler. Run with '
            '--mockserver-nofail flag to suppress these errors.\n'
            f'Tracing: {tracing_state}. Installed handlers:\n'
            f'{handlers_list}'
        )

    async def handle_request(self, request):
        handler = self.get_handler(request.path)
        try:
            response = await handler(request)
            if isinstance(response, aiohttp.web.Response):
                return response
            raise exceptions.MockServerError(
                'aiohttp.web.Response instance is expected '
                f'{response!r} given',
            )
        except exceptions.HandlerNotFoundError:
            raise
        except http.MockedError as exc:
            return _mocked_error_response(request, exc.error_code)
        except Exception as exc:
            self._report_handler_failure(request.path, exc)
            raise

    def _report_handler_failure(self, path: str, exc: Exception):
        if self.reporter:
            self.reporter.report_error(
                exc, f'Exception in mockserver handler for {path!r}: {exc !r}',
            )

    def register_handler(self, path, func, prefix=False):
        path = url_util.ensure_leading_separator(path)
        if prefix:
            handlers = self.prefix_handlers
        else:
            handlers = self.handlers
        handlers[path] = func
        return func


# pylint: disable=too-many-instance-attributes
class Server:
    session = None

    def __init__(
            self,
            mockserver_info: classes.MockserverInfo,
            *,
            logger=None,
            nofail=False,
            reporter: typing.Optional[
                reporter_plugin.MockserverReporterPlugin
            ] = None,
            tracing_enabled=True,
            trace_id_header=DEFAULT_TRACE_ID_HEADER,
            span_id_header=DEFAULT_SPAN_ID_HEADER,
    ):
        self._info = mockserver_info
        self._logger = logger
        self._nofail = nofail
        self._reporter = reporter
        self._tracing_enabled = tracing_enabled
        self._trace_id_header = trace_id_header
        self._span_id_header = span_id_header

    @property
    def tracing_enabled(self) -> bool:
        if self.session is None:
            return self._tracing_enabled
        return self.session.tracing_enabled

    @property
    def trace_id_header(self):
        return self._trace_id_header

    @property
    def span_id_header(self):
        return self._span_id_header

    @property
    def server_info(self) -> classes.MockserverInfo:
        return self._info

    @contextlib.contextmanager
    def new_session(self, trace_id: typing.Optional[str] = None):
        self.session = Session(self._reporter, self._tracing_enabled, trace_id)
        try:
            yield self.session
        finally:
            self.session = None

    async def handle_request(self, request):
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

    async def _handle_request(self, request: aiohttp.web.Request):
        trace_id = request.headers.get(self.trace_id_header)
        nofail = (
            self._nofail
            or self.tracing_enabled
            and not _is_from_client_fixture(trace_id)
        )
        if not self.session:
            error_message = 'Internal error: missing mockserver fixture'
            if nofail:
                return _internal_error(error_message)
            raise exceptions.MockServerError(error_message)

        if self.tracing_enabled and _is_other_test(
                trace_id, self.session.trace_id,
        ):
            self._report_other_test_request(request, trace_id)
            return _internal_error(REQUEST_FROM_ANOTHER_TEST_ERROR)
        try:
            return await self.session.handle_request(request)
        except exceptions.HandlerNotFoundError as exc:
            self._report_handler_not_found(exc, nofail=nofail)
            return _internal_error(
                'Internal error: mockserver handler not found',
            )

    def _report_handler_not_found(
            self, exc: exceptions.HandlerNotFoundError, *, nofail: bool,
    ):
        level = logging.WARNING if nofail else logging.ERROR
        logger.log(level, '%s', exc)
        if not nofail and self._reporter is not None:
            self._reporter.report_error(exc)

    def _report_other_test_request(self, request, trace_id):
        logger.warning(
            'Mockserver called path %s with previous test trace_id %s',
            request.path,
            trace_id,
        )


class MockserverFixture:
    """Mockserver handler installer fixture."""

    def __init__(self, mockserver: Server, session: Session) -> None:
        self._server = mockserver
        self._session = session

    @property
    def base_url(self) -> str:
        """Mockserver base url."""
        return self._server.server_info.base_url

    @property
    def host(self) -> str:
        """Mockserver hostname."""
        return self._server.server_info.host

    @property
    def port(self) -> int:
        """Mockserver port."""
        return self._server.server_info.port

    @property
    def trace_id_header(self) -> str:
        return self._server.trace_id_header

    @property
    def span_id_header(self) -> str:
        return self._server.span_id_header

    @property
    def trace_id(self) -> str:
        return self._session.trace_id

    def handler(
            self,
            path: str,
            prefix: bool = False,
            raw_request: bool = False,
            json_response: bool = False,
    ) -> classes.GenericRequestDecorator[http.Request]:
        """Register basic http handler for ``path``.

        Returns decorator that registers handler ``path``. Original function is
        wrapped with :ref:`AsyncCallQueue`.

        :param path: match url by prefix if ``True`` exact match otherwise
        :param raw_request: pass ``aiohttp.web.Response`` to handler instead of
            ``testsuite.utils.http.Request``
        :param regex: set True to treat path as regex pattern. Otherwise the
               pattern is interpreted by
               :py:class:`testsuite.mockserver.routing.RouteParser`

        .. code-block:: python

           @mockserver.handler('/service/path')
           def handler(request: testsuite.utils.http.Request):
               return mockserver.make_response('Hello, world!')
        """

        if raw_request:
            warnings.warn(
                'raw_request=True is deprecated, '
                'use aiohttp_handler() instead',
                DeprecationWarning,
            )
        if json_response:
            warnings.warn(
                'json_response=True is deprecated, '
                'use json_handler() instead',
                DeprecationWarning,
            )

        return self._handler_installer(
            path,
            prefix=prefix,
            raw_request=raw_request,
            json_response=json_response,
        )

    def json_handler(
            self, path: str, prefix: bool = False, raw_request: bool = False,
    ) -> classes.JsonRequestDecorator[http.Request]:
        """Register json http handler for ``path``.

        Returns decorator that registers handler ``path``. Original function is
        wrapped with :ref:`AsyncCallQueue`.

        :param path: match url by prefix if ``True`` exact match otherwise
        :param raw_request: pass ``aiohttp.web.Response`` to handler instead of
            ``testsuite.utils.http.Request``
        :param regex: set True to treat path as regex pattern. Otherwise the
               pattern is interpreted by
               :py:class:`testsuite.mockserver.routing.RouteParser`

        .. code-block:: python

           @mockserver.json_handler('/service/path')
           def handler(request: testsuite.utils.http.Request):
               # Return JSON document
               return {...}
               # or call to mockserver.make_response()
               return mockserver.make_response(...)
        """
        if raw_request:
            warnings.warn(
                'raw_request=True is deprecated, '
                'use aiohttp_json_handler() instead',
                DeprecationWarning,
            )
        return self._handler_installer(
            path, prefix=prefix, raw_request=raw_request, json_response=True,
        )

    def aiohttp_handler(
            self, path: str, prefix: bool = False,
    ) -> classes.GenericRequestDecorator[aiohttp.web.Request]:
        return self._handler_installer(
            path, prefix=prefix, raw_request=True, json_response=False,
        )

    def aiohttp_json_handler(
            self, path: str, prefix: bool = False,
    ) -> classes.JsonRequestDecorator[aiohttp.web.Request]:
        return self._handler_installer(
            path, prefix=prefix, raw_request=True, json_response=True,
        )

    def url(self, path: str) -> str:
        """Builds mockserver url for ``path``"""
        return url_util.join(self.base_url, path)

    def ignore_trace_id(self) -> typing.ContextManager[None]:
        return self.tracing(False)

    @contextlib.contextmanager
    def tracing(self, value: bool = True):
        original_value = self._session.tracing_enabled
        try:
            self._session.tracing_enabled = value
            yield
        finally:
            self._session.tracing_enabled = original_value

    def get_callqueue_for(self, path) -> callinfo.AsyncCallQueue:
        return self._session.get_handler(path).callqueue

    make_response = staticmethod(http.make_response)

    TimeoutError = http.TimeoutError
    NetworkError = http.NetworkError

    def _handler_installer(
            self,
            path: str,
            prefix: bool = False,
            raw_request: bool = False,
            json_response: bool = False,
    ) -> typing.Callable:
        def decorator(func):
            handler = Handler(
                func, raw_request=raw_request, json_response=json_response,
            )
            self._session.register_handler(path, handler, prefix=prefix)
            return handler.callqueue

        return decorator


MockserverSslFixture = MockserverFixture


def _create_ssl_context(ssl_info: classes.SslCertInfo) -> ssl.SSLContext:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(ssl_info.cert_path, ssl_info.private_key_path)
    return ssl_context


def _internal_error(message: str = 'Internal error') -> aiohttp.web.Response:
    return http.make_response(message, status=500)


def _mocked_error_response(request, error_code) -> aiohttp.web.Response:
    if _SUPPORTED_ERRORS_HEADER not in request.headers:
        raise exceptions.MockServerError(
            'Service does not support mockserver errors protocol',
        )
    supported_errors = request.headers[_SUPPORTED_ERRORS_HEADER].split(',')
    if error_code not in supported_errors:
        raise exceptions.MockServerError(
            f'Service does not support mockserver error of type {error_code}',
        )
    return http.make_response(
        response='', status=599, headers={_ERROR_HEADER: error_code},
    )


@contextlib.asynccontextmanager
async def create_server(
        host,
        port,
        worker_id,
        loop,
        testsuite_logger,
        mockserver_reporter,
        pytestconfig,
        ssl_info,
) -> typing.AsyncGenerator[Server, None]:
    ssl_context: typing.Optional[ssl.SSLContext]
    port = port if worker_id == 'master' else 0
    sock = net_utils.bind_socket(host, port)
    mockserver_info = _create_mockserver_info(sock, host, ssl_info)
    with contextlib.closing(sock):
        server = Server(
            mockserver_info,
            logger=testsuite_logger,
            nofail=pytestconfig.option.mockserver_nofail,
            reporter=mockserver_reporter,
            tracing_enabled=pytestconfig.getini('mockserver-tracing-enabled'),
            trace_id_header=pytestconfig.getini('mockserver-trace-id-header'),
            span_id_header=pytestconfig.getini('mockserver-span-id-header'),
        )
        if ssl_info:
            ssl_context = _create_ssl_context(ssl_info)
        else:
            ssl_context = None
        web_server = aiohttp.web.Server(server.handle_request, loop=loop)
        loop_server = await loop.create_server(
            web_server, sock=sock, ssl=ssl_context,
        )
        try:
            yield server
        finally:
            loop_server.close()
            await loop_server.wait_closed()


def _create_mockserver_info(
        sock, host: str, ssl_info: typing.Optional[classes.SslCertInfo],
) -> classes.MockserverInfo:
    sock_address = sock.getsockname()
    schema = 'https' if ssl_info else 'http'
    port = sock_address[1]
    base_url = '%s://%s:%d/' % (schema, host, port)
    return classes.MockserverInfo(
        host=host, port=port, base_url=base_url, ssl=ssl_info,
    )


def generate_trace_id() -> str:
    return _TRACE_ID_PREFIX + uuid.uuid4().hex


def _is_from_client_fixture(trace_id: str) -> bool:
    return trace_id is not None and trace_id.startswith(_TRACE_ID_PREFIX)


def _is_other_test(trace_id: str, current_trace_id: str) -> bool:
    return trace_id != current_trace_id and _is_from_client_fixture(trace_id)
