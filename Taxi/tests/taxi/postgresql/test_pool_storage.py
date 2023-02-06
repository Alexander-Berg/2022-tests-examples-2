# pylint: disable=unused-variable
import asyncio

import asyncpg
import pytest

from taxi.postgresql import dsn_parser
from taxi.postgresql import pool_storage as ps


class Connection:
    connection_count = 0

    def __init__(self, conf):
        self._is_master = conf.get('is_master', False)
        sync_slave_hosts = conf.get('sync', [])
        self._sync_slave_hosts = sync_slave_hosts if self._is_master else []
        self.connection_count += 1

    async def fetchval(self, query, timeout):
        return not self._is_master

    async def fetch(self, query, timeout):
        return [{'application_name': host} for host in self._sync_slave_hosts]

    async def close(self, timeout):
        assert timeout == ps.CLOSE_CONNECTION_TIMEOUT
        self.connection_count -= 1


class Pool:
    connection_count = 0

    def __init__(self, conf):
        self.conf = conf

    async def close(self):
        pass

    async def acquire(self, timeout):
        if not self.conf['available']:
            raise asyncpg.CannotConnectNowError
        self.connection_count += 1
        return Connection(self.conf)

    async def release(self, connection, timeout):
        self.connection_count -= 1


@pytest.mark.parametrize(
    ['conf_1', 'conf_2', 'expected_1', 'expected_2'],
    [
        (
            {
                'host1.net': {'available': False},
                'host2.net': {'available': True},
                'host3.net': {
                    'name': 'host3.net',
                    'available': True,
                    'is_master': True,
                    'sync': ['host1_net', 'host5_net'],
                },
                'host4.net': {'available': True},
                'host5.net': {'available': True},
            },
            {
                'host1.net': {'available': False},
                'host2.net': {'available': False},
                'host3.net': {'available': True},
                'host4.net': {
                    'available': True,
                    'is_master': True,
                    'sync': ['host3_net'],
                },
                'host5.net': {'available': True},
            },
            {
                ps.PGHostType.master: 'host3.net',
                ps.PGHostType.sync_slave: 'host5.net',
                ps.PGHostType.slave: 'host2.net',
            },
            {
                ps.PGHostType.master: 'host4.net',
                ps.PGHostType.sync_slave: 'host3.net',
                ps.PGHostType.slave: 'host5.net',
            },
        ),
    ],
)
async def test_pool_storage(patch, conf_1, conf_2, expected_1, expected_2):
    # pylint: disable=protected-access
    Pool.connection_count = 0
    Connection.connection_count = 0

    conf_by_host = conf_1

    @patch('asyncpg.connect')
    async def connect(**kwargs):
        assert kwargs['port'] == '9999'
        assert kwargs['user'] == 'test_user'
        assert kwargs['password'] == 'test_password'
        assert kwargs['database'] == 'test_database'
        assert kwargs['ssl'] is True
        assert kwargs['timeout'] == ps.CREATE_CONNECTION_TIMEOUT
        host = kwargs['host']
        if not conf_by_host[host]['available']:
            raise asyncpg.CannotConnectNowError
        return Connection(conf_by_host[host])

    @patch('asyncpg.pool.create_pool')
    async def create_pool(**kwargs):
        assert kwargs['min_size'] == 1
        assert kwargs['max_size'] == 5
        host = kwargs['host']
        return Pool(conf_by_host[host])

    is_wait_for_called = False

    @patch('asyncio.wait_for')
    async def wait_for(coro, **kwargs):
        nonlocal is_wait_for_called
        is_wait_for_called = True
        await coro
        raise asyncio.TimeoutError

    pool_storage = dsn_parser.create_pool_storage(
        [
            f'host={",".join(conf_1)} port=9999 user=test_user '
            f'password=test_password dbname=test_database sslmode=require',
        ],
        min_size=1,
        max_size=5,
    )

    def get_hosts_by_host_type(pool_storage: ps.PGPoolStorage):
        pool_wrappers_by_host_type = pool_storage._pool_wrappers_by_host_type
        return {
            host_type: wrapper.host
            for host_type, wrapper in pool_wrappers_by_host_type.items()
        }

    await pool_storage.init_cache()
    assert get_hosts_by_host_type(pool_storage) == expected_1

    for host, conf in conf_1.items():
        conf_1[host].clear()
        conf_1[host].update(conf_2[host])

    await pool_storage.refresh_cache()
    assert is_wait_for_called
    assert get_hosts_by_host_type(pool_storage) == expected_2
    assert Pool.connection_count == 0
    assert Connection.connection_count == 0
    await pool_storage.close_pools()


@pytest.mark.parametrize(
    [
        'host_types',
        'create_pool_kwargs',
        'kwargs_by_host_type',
        'exception_message',
        'host_type',
        'expected',
    ],
    [
        (
            (
                ps.PGHostType.master,
                ps.PGHostType.slave,
                ps.PGHostType.sync_slave,
            ),
            {'max_size': 5},
            {
                ps.PGHostType.master: {'max_size': 10},
                ps.PGHostType.sync_slave: {'max_size': 7},
            },
            None,
            ps.PGHostType.master,
            {
                'host1.net': {'max_size': 10},
                'host2.net': {'max_size': 7},
                'host3.net': {'max_size': 5},
            },
        ),
        (
            (ps.PGHostType.slave, ps.PGHostType.sync_slave),
            {'max_size': 5},
            {ps.PGHostType.master: {'max_size': 10}},
            'some host type of {<PGHostType.master: \'master\'>} is not '
            'declared in host_types',
            ps.PGHostType.master,
            None,
        ),
        (
            (ps.PGHostType.slave, ps.PGHostType.sync_slave),
            {'max_size': 5},
            None,
            'some host type of {<PGHostType.master: \'master\'>} is not '
            'declared in host_types',
            ps.PGHostType.master,
            None,
        ),
        (
            (ps.PGHostType.slave, ps.PGHostType.sync_slave),
            {'max_size': 5},
            None,
            None,
            ps.PGHostType.slave,
            {'host2.net': {'max_size': 5}, 'host3.net': {'max_size': 5}},
        ),
        (
            (ps.PGHostType.slave,),
            {'max_size': 5},
            {ps.PGHostType.slave: {'host': 'host1.net'}},
            'not acceptable create-pool arguments {\'host\'}',
            None,
            None,
        ),
    ],
)
async def test_kwargs_by_host_type(
        patch,
        host_types,
        create_pool_kwargs,
        kwargs_by_host_type,
        exception_message,
        host_type,
        expected,
):
    conf_by_host = {
        'host1.net': {
            'available': True,
            'is_master': True,
            'sync': ['host2_net'],
        },
        'host2.net': {
            'available': True,
            'is_master': False,
            'sync': ['host2_net'],
        },
        'host3.net': {
            'available': True,
            'is_master': False,
            'sync': ['host2_net'],
        },
    }

    @patch('asyncpg.connect')
    async def connect(**kwargs):
        host = kwargs['host']
        return Connection(conf_by_host[host])

    @patch('asyncpg.pool.create_pool')
    async def create_pool(**kwargs):
        host = kwargs['host']
        assert kwargs['max_size'] == expected[kwargs['host']]['max_size']
        return Pool(conf_by_host[host])

    try:
        pool_storage = dsn_parser.create_pool_storage(
            [
                f'host={",".join(["host1.net", "host2.net", "host3.net"])} '
                f'port=9999 user=test_user password=test_password '
                f'dbname=test_database sslmode=require',
            ],
            host_types=host_types,
            create_pool_kwargs_by_host_type=kwargs_by_host_type,
            **create_pool_kwargs,
        )
        await pool_storage.get_pool(host_type)
    except Exception as exc:  # pylint: disable=broad-except
        assert str(exc) == exception_message
