# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
import time

import asyncpg
from asyncpg import connect_utils
import pytest

from taxi import pg
from taxi.pg import conf_types
from taxi.pg import exceptions
from taxi.pg import pool as pool_module
from taxi.pg.policies import single_policies


async def test_create_pool_with_user(patch, pgsql, patch_get_host_info):
    dsn = patch_get_host_info()
    dsn_parameters = pgsql['pg'].conn.get_dsn_parameters()
    original_connect = connect_utils._connect

    # TODO(aselutin): remove 'if' in TAXITOOLS-3207 after asyncpg upgrade
    if asyncpg.__version__.startswith('0.23.0'):

        @patch('asyncpg.connect_utils._connect')
        async def _connect(
                *, loop, timeout, connection_class, record_class, **kwargs,
        ):
            assert kwargs['user'] == 'another_user'
            kwargs['user'] = dsn_parameters['user']
            return await original_connect(
                loop=loop,
                timeout=timeout,
                connection_class=connection_class,
                record_class=record_class,
                **kwargs,
            )

    else:

        @patch('asyncpg.connect_utils._connect')
        async def _connect(*, loop, timeout, connection_class, **kwargs):
            assert kwargs['user'] == 'another_user'
            kwargs['user'] = dsn_parameters['user']
            return await original_connect(  # pylint: disable=missing-kwoa
                loop=loop,
                timeout=timeout,
                connection_class=connection_class,
                **kwargs,
            )

    dsn_parameters = pgsql['pg'].conn.get_dsn_parameters()
    policy = single_policies.Master(
        check_host_timeout=1.0,
        close_pool_timeout=1.0,
        max_time_between_checks=1.0,
        max_replication_delay=1.0,
    )
    await pg.create_pool(dsn=dsn, policy=policy, user='another_user')


async def test_create_pool_with_cto(patch, pgsql, patch_get_host_info):
    dsn = patch_get_host_info()
    original_do_execute = asyncpg.connection.Connection._do_execute

    policy = single_policies.Master(
        check_host_timeout=1.0,
        close_pool_timeout=1.0,
        max_time_between_checks=1.0,
        max_replication_delay=1.0,
    )
    pool = await pg.create_pool(dsn=dsn, policy=policy, command_timeout=128)

    async with pool.acquire() as conn:
        original_do_execute = conn._do_execute

        # TODO(aselutin): remove kwargs in TAXITOOLS-3207 after asyncpg upgrade
        @patch('asyncpg.connection.Connection._do_execute')
        async def _do_execute(query, executor, timeout, retry=True, **kwargs):
            assert timeout == 128
            return await original_do_execute(
                query, executor, timeout, retry, **kwargs,
            )

        await conn.fetchval('SELECT 1;')


async def test_select_with_pool(master_pool):
    pool = master_pool
    async with pool.acquire() as conn:
        assert await conn.fetchval('SELECT 1;') == 1


@pytest.fixture
async def pool_and_patched_refresh(patch, master_pool):
    pool = master_pool
    pool_refresh = pool._refresh

    @patch('taxi.pg.pool.Pool._refresh')
    async def _refresh(log_extra):
        await pool_refresh(log_extra)

    return pool, _refresh


@pytest.mark.parametrize(
    ['is_acquire_error', 'method', 'exception', 'expected_count'],
    [
        (True, 'fetch', Exception, 1),
        (False, 'fetch', asyncpg.exceptions.ReadOnlySQLTransactionError, 1),
        (False, 'execute', asyncpg.exceptions.ReadOnlySQLTransactionError, 1),
        (False, 'fetch', Exception, 0),
    ],
)
async def test_refresh_on_error(
        patch,
        pool_and_patched_refresh,
        is_acquire_error,
        method,
        exception,
        expected_count,
):
    query = 'SELECT 1;'
    if is_acquire_error:

        @patch('asyncpg.pool.Pool.acquire')
        def acquire(timeout=None):
            raise exception

    else:

        @patch('asyncpg.connection.Connection.execute')
        async def execute(*args, **kwrags):
            if args[0] == query:
                raise exception

        @patch('asyncpg.connection.Connection._execute')
        async def _execute(*args, **kwrags):
            if args[0] == query:
                raise exception

    pool, patched_refresh = pool_and_patched_refresh
    for _ in range(2):
        try:
            async with pool.acquire() as conn:
                if method == 'fetch':
                    await conn.fetch('SELECT 1;')
                elif method == 'execute':
                    await conn.execute('SELECT 1;')
            assert False
        except exception:
            pass
        await pool._refresh_task
    assert len(patched_refresh.calls) == expected_count


async def test_refresh_on_success(patch, pool_and_patched_refresh):
    pool, patched_refresh = pool_and_patched_refresh
    for _ in range(2):
        async with pool.acquire() as conn:
            await conn.fetch('SELECT 1;')
        await pool._refresh_task
    assert not patched_refresh.calls


@pytest.mark.parametrize(
    ['is_master_changed', 'expected_count'], [(False, 0), (True, 1)],
)
async def test_refresh_by_time_single(
        patch,
        pool_and_patched_refresh,
        is_master_changed,
        expected_count,
        patch_get_host_info,
):
    pool, patched_refresh = pool_and_patched_refresh
    patch_get_host_info(
        master_host=(
            'fake_host_1' if not is_master_changed else 'fake_host_2'
        ),
    )

    policy_is_needed_to_recreate = pool._policy._is_needed_to_recreate

    @patch('taxi.pg.policy_impl.SinglePolicy._is_needed_to_recreate')
    async def _is_needed_to_recreate(*args, **kwargs):
        return await policy_is_needed_to_recreate(*args, **kwargs)

    pool._last_check_time -= pool._policy.max_time_between_checks * 2
    for _ in range(3):
        async with pool.acquire() as conn:
            await conn.fetch('SELECT 1;')
        assert pool._update_status_task
        await pool._update_status_task
        await pool._refresh_task
    # in any case _is_needed_to_recreate must be called once because
    # _last_check_time was patched once
    assert len(_is_needed_to_recreate.calls) == 1
    assert len(patched_refresh.calls) == expected_count


@pytest.mark.parametrize(
    ['is_host_info_list_changed', 'expected_count'], [(False, 0), (True, 1)],
)
async def test_refresh_by_time_multi(
        patch, round_robin_pool, is_host_info_list_changed, expected_count,
):
    pool = round_robin_pool
    pool_refresh = pool._refresh

    @patch('taxi.pg.pool.Pool._refresh')
    async def _refresh(log_extra):
        await pool_refresh(log_extra)

    original_method = pool._policy._get_host_info

    @patch('taxi.pg.policy_impl.Policy._get_host_info')
    async def _get_host_info(
            conn_settings: conf_types.ConnectionSettings, context, log_extra,
    ):
        if is_host_info_list_changed and conn_settings.host == 'fake_host_3':
            raise Exception
        return await original_method(conn_settings, context, log_extra)

    pool._last_check_time -= pool._policy.max_time_between_checks * 2
    for _ in range(3):
        async with pool.acquire() as conn:
            await conn.fetch('SELECT 1;')
        assert pool._update_status_task
        await pool._update_status_task
        await pool._refresh_task
    assert len(_refresh.calls) == expected_count


@pytest.mark.parametrize(
    ['replication_delay', 'expected_count'], [(0.5, 2), (2, 1)],
)
async def test_exclude_by_replication_delay(
        patch,
        round_robin_pool,
        patch_get_host_info,
        replication_delay,
        expected_count,
):
    pool = round_robin_pool
    patch_get_host_info(replication_delay=replication_delay)

    pool._last_check_time -= pool._policy.max_time_between_checks * 2
    pool.acquire()
    await pool._update_status_task
    pool.acquire()
    await pool._refresh_task

    assert len(pool._pool_holder._pool_wrappers) == expected_count


@pytest.mark.parametrize(
    ['master_mode', 'expected_count'],
    [
        (conf_types.MasterMode.allow, 3),
        (conf_types.MasterMode.fallback, 1),
        (conf_types.MasterMode.disable, None),
    ],
)
async def test_master_mode(
        patch,
        round_robin_pool,
        patch_get_host_info,
        master_mode,
        expected_count,
):
    pool = round_robin_pool
    pool._policy._master_mode = master_mode
    original_method = pool._policy._get_host_info

    @patch('taxi.pg.policy_impl.Policy._get_host_info')
    async def _get_host_info(
            conn_settings: conf_types.ConnectionSettings, context, log_extra,
    ):
        if (
                master_mode is not conf_types.MasterMode.allow
                and conn_settings.host in ['fake_host_2', 'fake_host_3']
        ):
            raise Exception
        return await original_method(conn_settings, context, log_extra)

    pool._last_check_time -= pool._policy.max_time_between_checks * 2
    try:
        pool.acquire()
        await pool._update_status_task
        pool.acquire()
        await pool._refresh_task
    except exceptions.CreatePoolError:
        assert master_mode is conf_types.MasterMode.disable
    else:
        assert len(pool._pool_holder._pool_wrappers) == expected_count


async def test_close_connection(patch, create_pool):
    original_connect = asyncpg.connect
    close_call_count = 0

    class _Connection(asyncpg.Connection):
        async def close(self, *, timeout=None):
            assert timeout == 1.0
            await super().close(timeout=timeout)
            nonlocal close_call_count
            close_call_count += 1

    @patch('asyncpg.connect')
    async def _connect(*args, **kwargs):
        kwargs['connection_class'] = _Connection
        return await original_connect(*args, **kwargs)

    pool = await create_pool()
    await pool.close(timeout=1.0)
    # check connections for fake_host_1, fake_host_2 and fake_host_3
    assert len(_connect.calls) == 3
    assert close_call_count == 3


async def test_close_pool(create_pool):
    pool = await create_pool()
    asyncpg_pool = pool._pool_holder._pool_wrapper.pool
    assert not asyncpg_pool._closed
    # invalidate pool to call refresh
    pool._pool_holder._is_acceptable = False
    async with pool.acquire() as conn:
        await conn.fetch('SELECT 1;')
    await pool._refresh_task
    await pool.close(timeout=1.0)
    assert asyncpg_pool._closed


@pytest.mark.parametrize('delay, expected_count', [(2.0, 0), (4.0, 1)])
async def test_min_time_between_refreshes(
        monkeypatch, pool_and_patched_refresh, delay, expected_count,
):
    pool, patched_refresh = pool_and_patched_refresh
    monkeypatch.setattr(pool_module, 'MIN_TIME_BETWEEN_REFRESHES', 3)
    now = time.monotonic()
    # invalidate pool and call refresh
    pool._pool_holder._is_acceptable = False
    pool._last_refresh_time = now - delay
    pool.acquire()
    await pool._refresh_task
    assert len(patched_refresh.calls) == expected_count
    if expected_count:
        assert pool._last_refresh_time > now - delay
