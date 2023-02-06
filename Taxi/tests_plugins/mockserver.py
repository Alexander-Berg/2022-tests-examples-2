import contextlib
import json

import gevent
from gevent import pywsgi
import gevent.monkey
import pytest
import werkzeug
import werkzeug.exceptions
import werkzeug.utils

from taxi_tests.utils import callinfo
from taxi_tests.utils import net as net_utils
from taxi_tests.utils import session_context
from taxi_tests.utils import tracing

pytest_plugins = ['taxi_tests.plugins.tracing']

REQUEST_FROM_ANOTHER_TEST_ERROR = 'Internal error: request is from other test'


class BaseError(Exception):
    """Base class for exceptions from this module."""


class MockServerError(BaseError):
    pass


class HandlerNotFoundError(MockServerError):
    pass


class Request(werkzeug.Request):
    @werkzeug.utils.cached_property
    def json(self):
        if 'json' not in self.environ.get('CONTENT_TYPE', ''):
            raise werkzeug.exceptions.BadRequest('Not a JSON request')
        try:
            return json.loads(self.data.decode('utf-8'))
        except Exception:
            raise werkzeug.exceptions.BadRequest('Unable to read JSON request')


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
        raise HandlerNotFoundError(path)

    def handle_request(self, request, start_response):
        try:
            response = self.get_handler(request.path)(request)
            return response(request.environ, start_response)
        except HandlerNotFoundError:
            raise
        except (
            werkzeug.exceptions.ClientDisconnected,
            werkzeug.exceptions.NotFound,
        ):
            raise
        except Exception as exc:
            self.add_failure(request, exc)
            raise

    def register_handler(self, path, func, prefix=False):
        if prefix:
            handlers = self.prefix_handlers
        else:
            handlers = self.handlers
        wrapped = callinfo.callqueue(func)
        handlers[path] = wrapped
        return wrapped

    def _flush_callinfo(self):
        for handler in self.handlers.values():
            handler.flush()
        for handler in self.prefix_handlers.values():
            handler.flush()

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

    def handler(self, path, prefix=False):
        def decorator(func):
            return self._session.register_handler(path, func, prefix=prefix)

        return decorator

    def json_handler(self, path, prefix=False):
        def decorator(func):
            return self._session.register_handler(
                path, json_wrapper(func), prefix=prefix,
            )

        return decorator

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

    @staticmethod
    def make_response(*args, **kwargs):
        return _make_response(*args, **kwargs)


class Server:  # pylint: disable=too-many-instance-attributes
    session = None

    def __init__(self, listener, *, nofail=False):
        self.wsgi = pywsgi.WSGIServer(listener, self.application)
        self.host, self.port = 'localhost', self.wsgi.address[1]
        self.base_url = 'http://%s:%d/' % (self.host, self.port)
        self.started = False
        self._nofail = nofail
        self._trace_id = None

    def close(self):
        self.wsgi.close()

    def application(self, env, start_response):
        request = Request(env)
        trace_id = request.headers.get(tracing.TRACE_ID_HEADER)

        if not self.session:
            error_message = 'Internal error: missing mockserver fixture'
            if self._nofail or not tracing.is_from_client_fixture(trace_id):
                return _internal_error(request, start_response, error_message)
            raise MockServerError(error_message)

        if tracing.is_other_test(trace_id, self._trace_id):
            return _internal_error(
                request, start_response, REQUEST_FROM_ANOTHER_TEST_ERROR,
            )
        try:
            return self.session.handle_request(request, start_response)
        except HandlerNotFoundError as exc:
            if self._nofail or not tracing.is_from_client_fixture(trace_id):
                return _internal_error(
                    request,
                    start_response,
                    'Internal error: mockserver handler not found',
                )
            self.session.add_failure(request, exc)
            raise

    def start(self):
        if not self.started:
            gevent.spawn(self.wsgi.serve_forever)
        self.started = True

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


def pytest_load_initial_conftests(early_config, parser, args):
    # Monkey patch as early as possible
    gevent.monkey.patch_all()


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
        default=9999,
        type=int,
        help='Default port for mockserver.',
    )


def json_wrapper(func):
    def decorated(request):
        response = func(request)
        if isinstance(response, werkzeug.Response):
            return response
        return _make_response(
            json.dumps(response, ensure_ascii=False).encode('utf-8'),
            content_type='application/json',
        )

    return decorated


@pytest.fixture
def mockserver(_mockserver: Server, trace_id):
    with _mockserver.new_session(trace_id) as session:
        yield HandlerInstaller(_mockserver, session)


@pytest.fixture(scope='session', autouse=True)
def _mockserver(pytestconfig, testsuite_session_context, worker_id):
    if worker_id == 'master':
        listener = (
            pytestconfig.option.mockserver_host,
            pytestconfig.option.mockserver_port,
        )
    else:
        listener = net_utils.bind_socket()
    server = Server(listener, nofail=pytestconfig.option.mockserver_nofail)
    testsuite_session_context.mockserver = session_context.MockserverInfo(
        host=server.host, port=server.port, base_url=server.base_url,
    )
    server.start()
    with contextlib.closing(server):
        yield server


def _make_response(response=None, status=200, headers=None, content_type=None):
    return werkzeug.Response(
        response=response,
        status=status,
        headers=headers,
        content_type=content_type,
    )


def _internal_error(request, start_response, message='Internal error'):
    response = _make_response(message, status=500)
    return response(request.environ, start_response)
