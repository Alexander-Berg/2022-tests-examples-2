# pylint: disable=W0212
import pytest

from client_chyt import components as chyt_clients_lib


async def test_chyt_client(library_context, patch, simple_secdist):
    clique_alias = '*test'
    mock_value = iter([{'test': 'test'}])

    @patch('yt.clickhouse.execute')
    def execute(*args, **kwargs):
        assert kwargs['alias'] == clique_alias
        return mock_value

    client_config = chyt_clients_lib.CHYTClientConfig(
        cluster='hahn', alias=clique_alias,
    )

    client = library_context.chyt_clients.get_client(client_config)
    result = await client.execute('select 1')

    assert result == [{'test': 'test'}]
    assert len(execute.calls) == 1


def test_chyt_client_custom_timeout(library_context):
    client = library_context.chyt_clients.get_client(
        chyt_clients_lib.CHYTClientConfig(cluster='hahn', alias='*test'),
    )
    assert client._yt_client.config['proxy']['request_timeout'] == 15

    client = library_context.chyt_clients.get_client(
        chyt_clients_lib.CHYTClientConfig(
            cluster='hahn',
            alias='*test',
            qos=chyt_clients_lib.QOSConfig(timeout_ms=10000),
        ),
    )
    assert client._yt_client.config['proxy']['request_timeout'] == 10


async def test_qos_settings(library_context):
    clique_alias = '*test'
    client = library_context.chyt_clients.get_client(
        chyt_clients_lib.CHYTClientConfig(cluster='hahn', alias=clique_alias),
    )
    proxy_config = client._yt_client.config['proxy']
    assert proxy_config['request_timeout'] == 15
    assert client._qos_config.attempts == 1
    assert client._qos_config.timeout_ms == 15000
    assert client._qos_config.delay_ms == 100


# Deprecated method.
# Secdist patch via library.yaml doesnt work.
# TODO: make it better
@pytest.fixture(name='simple_secdist')
def simple_secdist_fixture(simple_secdist):
    simple_secdist['settings_override'].update(
        {'YT_CONFIG': {'hahn': {'prefix': '//home/testsuite'}}},
    )
    return simple_secdist
