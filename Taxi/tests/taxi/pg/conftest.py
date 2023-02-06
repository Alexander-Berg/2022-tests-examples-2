# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
import datetime
import logging
import pathlib

import asyncpg
from asyncpg import connect_utils
import pytest

from taxi import pg
from taxi.pg import policy_impl
from taxi.pg import pool as pool_module
from taxi.pg.policies import multi_policies
from taxi.pg.policies import single_policies
from testsuite.databases.pgsql import discover

SQLDATA_PATH = pathlib.Path(__file__).parent / 'static/postgresql'


@pytest.fixture(autouse=True)
def set_logger():
    logger = logging.getLogger('taxi.pg')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    yield
    logger.removeHandler(handler)


@pytest.fixture(scope='session')
def pgsql_local(pgsql_local_create):
    databases = discover.find_schemas('pg', schema_dirs=[SQLDATA_PATH])
    return pgsql_local_create(list(databases.values()))


@pytest.fixture
def patch_get_host_info(pgsql, patch):
    original_connect = connect_utils._connect

    def _patch_get_host_info(master_host='fake_host_1', replication_delay=0.1):
        # emulating multiple hosts
        dsn_parameters = pgsql['pg'].conn.get_dsn_parameters()

        # TODO(aselutin): remove 'if' in TAXITOOLS-3207 after asyncpg upgrade
        if asyncpg.__version__.startswith('0.23.0'):

            @patch('asyncpg.connect_utils._connect')
            async def _connect(
                    *, loop, timeout, connection_class, record_class, **kwargs,
            ):
                class Connection(connection_class):
                    __slots__ = ('fake_host',)

                    async def fetchrow(self, query, *args, **kwargs):
                        if query == policy_impl.IS_IN_RECOVERY_QUERY:
                            return {
                                'is_in_recovery': (
                                    self.fake_host != master_host
                                ),
                                'replication_delay': datetime.timedelta(
                                    seconds=replication_delay,
                                ),
                            }
                        return await super().fetchrow(query, *args, **kwargs)

                fake_host = kwargs['host']
                kwargs['host'] = dsn_parameters['host']
                conn = await original_connect(
                    loop=loop,
                    timeout=timeout,
                    connection_class=Connection,
                    record_class=record_class,
                    **kwargs,
                )
                conn.fake_host = fake_host
                return conn

        else:

            @patch('asyncpg.connect_utils._connect')
            async def _connect(*, loop, timeout, connection_class, **kwargs):
                class Connection(connection_class):
                    __slots__ = ('fake_host',)

                    async def fetchrow(self, query, *args, **kwargs):
                        if query == policy_impl.IS_IN_RECOVERY_QUERY:
                            return {
                                'is_in_recovery': (
                                    self.fake_host != master_host
                                ),
                                'replication_delay': datetime.timedelta(
                                    seconds=replication_delay,
                                ),
                            }
                        return await super().fetchrow(query, *args, **kwargs)

                fake_host = kwargs['host']
                kwargs['host'] = dsn_parameters['host']
                conn = await original_connect(  # pylint: disable=missing-kwoa
                    loop=loop,
                    timeout=timeout,
                    connection_class=Connection,
                    **kwargs,
                )
                conn.fake_host = fake_host
                return conn

        return (
            f'host=fake_host_1,fake_host_2,fake_host_3 '
            f'port={dsn_parameters["port"]} '
            f'user={dsn_parameters["user"]} '
            f'dbname={dsn_parameters["dbname"]} '
            f'sslmode=disable'
        )

    return _patch_get_host_info


@pytest.fixture
def create_pool(monkeypatch, patch_get_host_info):
    monkeypatch.setattr(pool_module, 'MIN_TIME_BETWEEN_REFRESHES', 0)

    async def _create_pool(policy_type=single_policies.Master):
        policy = policy_type(
            check_host_timeout=1.0,
            close_pool_timeout=1.0,
            max_time_between_checks=1.0,
            max_replication_delay=1.0,
        )
        dsn = patch_get_host_info()
        return await pg.create_pool(dsn, policy=policy, min_size=1, max_size=5)

    return _create_pool


@pytest.fixture
async def master_pool(create_pool):
    pool = await create_pool()
    yield pool
    await pool.close(timeout=1.0)


@pytest.fixture
async def round_robin_pool(create_pool):
    pool = await create_pool(policy_type=multi_policies.RoundRobin)
    yield pool
    await pool.close(timeout=1.0)
