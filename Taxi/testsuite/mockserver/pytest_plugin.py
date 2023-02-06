import typing

import pytest

from testsuite import annotations
from testsuite.utils import colors

from . import classes
from . import exceptions
from . import reporter_plugin
from . import server

_SSL_KEY_FILE_INI_KEY = 'mockserver-ssl-key-file'
_SSL_CERT_FILE_INI_KEY = 'mockserver-ssl-cert-file'


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
        help='Default host for http mockserver.',
    )
    group.addoption(
        '--mockserver-port',
        type=int,
        default=0,
        help=(
            'Http mockserver port for default (master) worker. Set 0 to use '
            'random port. NOTE: non-default workers always use random port.'
        ),
    )
    group.addoption(
        '--mockserver-ssl-host',
        default='localhost',
        help='Default host for https mockserver.',
    )
    group.addoption(
        '--mockserver-ssl-port',
        type=int,
        default=0,
        help=(
            'Https mockserver port for default (master) worker. Set 0 to use '
            'random port. NOTE: non-default workers always use random port.'
        ),
    )
    parser.addini(
        'mockserver-tracing-enabled',
        type='bool',
        default=False,
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
    parser.addini(
        'mockserver-trace-id-header',
        default=server.DEFAULT_TRACE_ID_HEADER,
        help=(
            'name of tracing http header, value changes from test to test and '
            'is constant within test'
        ),
    )
    parser.addini(
        'mockserver-span-id-header',
        default=server.DEFAULT_SPAN_ID_HEADER,
        help='name of tracing http header, value is unique for each request',
    )
    parser.addini(
        'mockserver-ssl-cert-file',
        type='pathlist',
        help='path to ssl certificate file to setup mockserver_ssl',
    )
    parser.addini(
        'mockserver-ssl-key-file',
        type='pathlist',
        help='path to ssl key file to setup mockserver_ssl',
    )


def pytest_configure(config):
    config.pluginmanager.register(
        reporter_plugin.MockserverReporterPlugin(
            colors_enabled=colors.should_enable_color(config),
        ),
        'mockserver_reporter',
    )


@pytest.fixture
def mockserver(
        _mockserver: server.Server, _mockserver_trace_id: str,
) -> annotations.YieldFixture[server.MockserverFixture]:
    with _mockserver.new_session(_mockserver_trace_id) as session:
        yield server.MockserverFixture(_mockserver, session)


@pytest.fixture
async def mockserver_ssl(
        _mockserver_ssl: typing.Optional[server.Server],
        _mockserver_trace_id: str,
) -> annotations.AsyncYieldFixture[server.MockserverSslFixture]:
    if _mockserver_ssl is None:
        raise exceptions.MockServerError(
            f'mockserver_ssl is not configured. {_SSL_KEY_FILE_INI_KEY} and '
            f'{_SSL_CERT_FILE_INI_KEY} must be specified in pytest.ini',
        )
    with _mockserver_ssl.new_session(_mockserver_trace_id) as session:
        yield server.MockserverFixture(_mockserver_ssl, session)


@pytest.fixture(scope='session')
def mockserver_info(_mockserver: server.Server) -> classes.MockserverInfo:
    """Returns mockserver information object."""
    return _mockserver.server_info


@pytest.fixture(scope='session')
def mockserver_ssl_info(
        _mockserver_ssl: typing.Optional[server.Server],
) -> typing.Optional[classes.MockserverInfo]:
    if _mockserver_ssl is None:
        return None
    return _mockserver_ssl.server_info


@pytest.fixture(scope='session')
def mockserver_ssl_cert(pytestconfig) -> typing.Optional[classes.SslCertInfo]:
    def _get_ini_path(name):
        values = pytestconfig.getini(name)
        if not values:
            return None
        if len(values) > 1:
            raise exceptions.MockServerError(
                f'{name} ini setting has multiple values',
            )
        return str(values[0])

    cert_path = _get_ini_path(_SSL_CERT_FILE_INI_KEY)
    key_path = _get_ini_path(_SSL_KEY_FILE_INI_KEY)
    if cert_path and key_path:
        return classes.SslCertInfo(
            cert_path=cert_path, private_key_path=key_path,
        )
    return None


@pytest.fixture(scope='session')
async def _mockserver(
        pytestconfig, worker_id, testsuite_logger, loop, _mockserver_reporter,
) -> annotations.AsyncYieldFixture[server.Server]:
    async with server.create_server(
            pytestconfig.option.mockserver_host,
            pytestconfig.option.mockserver_port,
            worker_id,
            loop,
            testsuite_logger,
            _mockserver_reporter,
            pytestconfig,
            ssl_info=None,
    ) as result:
        yield result


@pytest.fixture(scope='session')
async def _mockserver_ssl(
        pytestconfig,
        worker_id,
        testsuite_logger,
        loop,
        mockserver_ssl_cert,
        _mockserver_reporter,
) -> annotations.AsyncYieldFixture[typing.Optional[server.Server]]:

    if mockserver_ssl_cert:
        async with server.create_server(
                pytestconfig.option.mockserver_ssl_host,
                pytestconfig.option.mockserver_ssl_port,
                worker_id,
                loop,
                testsuite_logger,
                _mockserver_reporter,
                pytestconfig,
                mockserver_ssl_cert,
        ) as result:
            yield result
    else:
        yield None


@pytest.fixture(scope='session')
def _mockserver_reporter(
        pytestconfig,
) -> reporter_plugin.MockserverReporterPlugin:
    return pytestconfig.pluginmanager.get_plugin('mockserver_reporter')


@pytest.fixture
def _mockserver_trace_id() -> str:
    return server.generate_trace_id()
