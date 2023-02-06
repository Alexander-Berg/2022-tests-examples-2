import pytest

from testsuite.mockserver import classes
from testsuite.mockserver import exceptions
from testsuite.mockserver import server


class DummyServer:
    @property
    def server_info(self):
        return classes.MockserverInfo(
            host='', port=0, base_url='http://mockserver/', ssl=None,
        )


def test_session():
    session = server.Session()

    def handler(request):
        pass

    handler = session.register_handler('/foo', handler)
    assert session.get_handler('/foo') is handler

    def handler2(request):
        pass

    handler2 = session.register_handler('/foo', handler2)
    assert session.get_handler('/foo') is handler2

    with pytest.raises(exceptions.HandlerNotFoundError):
        session.get_handler('/bar')


def test_installer_base_url():
    session = server.Session()
    dummy_server = DummyServer()
    installer = server.MockserverFixture(dummy_server, session)
    assert installer.base_url == dummy_server.server_info.base_url


def test_installer_handlers():
    session = server.Session()
    installer = server.MockserverFixture(DummyServer(), session)

    @installer.handler('/foo')
    def handler1(request):
        return 'result'

    @installer.json_handler('/bar')
    def handler2(request):
        return {}

    assert session.get_handler('/foo').callqueue is handler1
    assert session.get_handler('/bar').callqueue is handler2
