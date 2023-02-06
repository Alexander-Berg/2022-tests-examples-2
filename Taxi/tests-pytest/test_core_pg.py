import pytest

from taxi.core import pg


class ConnectorMock(object):
    def __init__(self):
        self.counter = 0
        self.establish_connection_calls = []
        self.get_connection_calls = []

    def establish_connection(self, params):
        self.establish_connection_calls.append(params)
        self.counter += 1
        return self.counter

    def get_connection(self, connection_id):
        self.get_connection_calls.append(connection_id)
        return connection_id


class ConnectionHolderMock(object):
    def __init__(self, params):
        self.init_calls = [params]
        self.get_connection_calls = 0
        self.put_connection_calls = 0
        self.destroy_calls = 0

    def get_connection(self):
        self.get_connection_calls += 1
        return {'connection_object': True}

    def put_connection(self, connection):
        self.put_connection_calls += 1
        assert connection == {'connection_object': True}

    def destroy(self):
        self.destroy_calls += 1


@pytest.mark.filldb(_fill=False)
def test_connector(patch):

    @patch('socket.getaddrinfo')
    def getaddrinfo(host, port):
        # results for ya.ru
        return [
            (30, 2, 17, '', ('2a02:6b8::2:242', 80, 0, 0)),
            (30, 1, 6, '', ('2a02:6b8::2:242', 80, 0, 0)),
            (2, 2, 17, '', ('87.250.250.242', 80)),
            (2, 1, 6, '', ('87.250.250.242', 80)),
        ]

    connector = pg.Connector(ConnectionHolderMock)

    conn_id = connector.establish_connection(
        {'connection_kwargs': {'host': 'host1', 'port': 1, 'dbname': 'test'}}
    )
    assert conn_id == 0
    assert getaddrinfo.calls == [{'host': 'host1', 'port': 1}]
    assert len(connector._connection_holders) == 1

    holder = connector._connection_holders[0]
    holder.init_calls == [
        {'connection_kwargs': {'host': 'host1', 'port': 1, 'dbname': 'test'}}
    ]
    holder.get_connection_calls == 0
    holder.put_connection_calls == 0
    holder.destroy_calls == 0

    assert connector._ids_by_addr == {('host1', 1): [0]}
    assert connector._sockaddrs_by_addr == {
        ('host1', 1): {('2a02:6b8::2:242', 80, 0, 0), ('87.250.250.242', 80)}
    }

    with connector.get_connection(0) as conn:
        assert conn == {'connection_object': True}

    holder.get_connection_calls == 1
    holder.put_connection_calls == 1


@pytest.mark.filldb(_fill=False)
def test_dynamic_connection():
    connector = ConnectorMock()
    dynamic_connection = pg.DynamicConnection({
        'master': {'id': 'master'}, 'slaves': [{'id': 'slave1'}]
    }, connector)

    assert connector.establish_connection_calls == [
        {'id': 'master'}, {'id': 'slave1'}
    ]

    assert connector.get_connection_calls == []

    dynamic_connection.master
    assert connector.get_connection_calls == [1]

    dynamic_connection.slave
    assert connector.get_connection_calls == [1, 2]
