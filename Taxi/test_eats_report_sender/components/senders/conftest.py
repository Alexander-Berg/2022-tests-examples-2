# pylint: disable=redefined-outer-name
import asynctest
import pytest


@pytest.fixture
def mock_assh__file():
    file = asynctest.MagicMock(mock_name='file')
    file.write = asynctest.CoroutineMock()
    return file


@pytest.fixture
def mock_assh__client(mock_assh__file):
    open_file_manager = asynctest.MagicMock(mock_name='open_file_manager')
    open_file_manager.__aenter__.return_value = mock_assh__file

    client = asynctest.MagicMock(mock_name='client')
    client.open.return_value = open_file_manager

    return client


@pytest.fixture
def mock_assh__connect(mock_assh__client):
    client_manager = asynctest.MagicMock(mock_name='client_manager')
    client_manager.__aenter__.return_value = mock_assh__client

    connect = asynctest.MagicMock(mock_name='connect')
    connect.start_sftp_client.return_value = client_manager

    return connect


@pytest.fixture
def mock_assh(mock_assh__connect, monkeypatch):
    connect_manager = asynctest.MagicMock()
    connect_manager.mock_name = 'connect manager'
    connect_manager.__aenter__.return_value = mock_assh__connect

    mock_asyncssh = asynctest.MagicMock()
    mock_asyncssh.mock_name = 'asyncssh'
    mock_asyncssh.connect.return_value = connect_manager

    import asyncssh
    monkeypatch.setattr(asyncssh, 'connect', mock_asyncssh.connect)

    return mock_asyncssh
