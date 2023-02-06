# coding: utf-8
import pytest

from dmp_suite.greenplum.config import ConnectionManager, GreenplumConfigError
from dmp_suite.greenplum.connection import EtlConnection


class ConnectionMock(EtlConnection):
    def __init__(self, name):
        self.name = name

    def __eq__(self, o):
        return self.name == o.name and type(self) == type(o)


def test_connection_manager():
    manager = ConnectionManager()

    conn1 = ConnectionMock('1')
    conn2 = ConnectionMock('2')

    with pytest.raises(GreenplumConfigError):
        manager.get_connection()

    manager.register_connection(conn1.name, conn1)
    assert manager.get_connection(conn1.name) == conn1

    with pytest.raises(GreenplumConfigError):
        manager.get_connection()

    with pytest.raises(GreenplumConfigError):
        manager.register_connection(conn1.name, conn1)

    with pytest.raises(GreenplumConfigError):
        manager.register_connection(conn1.name, conn1, set_as_default=True)

    with pytest.raises(GreenplumConfigError):
        manager.get_connection(conn2.name)

    manager.register_connection(conn2.name, conn2, set_as_default=True)
    assert manager.get_connection() == conn2
    assert manager.get_connection(conn1.name) == conn1
    assert manager.get_connection(conn2.name) == conn2

    with pytest.raises(GreenplumConfigError):
        manager.register_connection('new_name', conn1, set_as_default=True)

    with pytest.raises(GreenplumConfigError):
        manager.register_connection('new_name', conn2, set_as_default=True)

    manager.register_connection('new_name', conn2)
    assert manager.get_connection() == conn2
    assert manager.get_connection(conn2.name) == conn2
    assert manager.get_connection('new_name') == conn2
