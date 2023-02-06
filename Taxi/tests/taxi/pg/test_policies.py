# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
import pytest

from taxi.pg import pool_holders
from taxi.pg.policies import single_policies


async def test_round_robin(patch, round_robin_pool):
    used_pools = set()
    original_class = pool_holders.PoolHolderAcquireContext

    @patch('taxi.pg.pool_holders.PoolHolderAcquireContext')
    def pool_holder_acquire_context(**kwargs):
        used_pools.add(kwargs['asyncpg_pool'])
        return original_class(**kwargs)

    pool = round_robin_pool
    assert isinstance(pool._pool_holder, pool_holders.MultiPoolHolder)
    assert len(pool._pool_holder._pool_wrappers) == 2
    for _ in range(2):
        async with pool.acquire() as conn:
            await conn.fetch('SELECT 1;')
    assert len(used_pools) == 2


@pytest.mark.parametrize(
    [
        'policy_type',
        'ping_delay_by_host_before',
        'ping_delay_by_host_after',
        'expected_host_before',
        'expected_host_after',
    ],
    [
        (
            single_policies.Fastest,
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.003,
                'fake_host_3': 0.0031,
            },
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.003,
                'fake_host_3': 0.00069,
            },
            'fake_host_2',
            'fake_host_3',
        ),
        (
            single_policies.Fastest,
            {'fake_host_1': 0.001, 'fake_host_2': 0.003, 'fake_host_3': 0.006},
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.003,
                'fake_host_3': 0.00071,  # not enough to change host
            },
            'fake_host_2',
            'fake_host_2',
        ),
        (
            single_policies.Slowest,
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.009,
                'fake_host_3': 0.0089,
            },
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.009,
                'fake_host_3': 0.0166,
            },
            'fake_host_2',
            'fake_host_3',
        ),
        (
            single_policies.Slowest,
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.009,
                'fake_host_3': 0.0089,
            },
            {
                'fake_host_1': 0.001,
                'fake_host_2': 0.009,
                'fake_host_3': 0.0164,  # not enough to change host
            },
            'fake_host_2',
            'fake_host_2',
        ),
    ],
)
async def test_fastest_and_slowest(
        patch,
        create_pool,
        policy_type,
        ping_delay_by_host_before,
        ping_delay_by_host_after,
        expected_host_before,
        expected_host_after,
):
    pool = await create_pool(policy_type=policy_type)
    ping_delay_by_host = ping_delay_by_host_before

    @patch('taxi.pg.policies.single_policies._PingDelayPolicy._get_ping_delay')
    async def _get_ping_delay(conn):
        return ping_delay_by_host[conn.fake_host]

    # invalidate pool and call refresh
    pool._pool_holder._is_acceptable = False
    pool.acquire()
    await pool._refresh_task

    assert (
        len(pool._pool_holder.context.ping_delays_by_host['fake_host_1'])
        == single_policies._PingDelayPolicy.QUEUE_MIN_SIZE
    )

    async with pool.acquire() as conn:
        assert conn.fake_host == expected_host_before

    ping_delay_by_host = ping_delay_by_host_after

    pool._last_check_time -= pool._policy.max_time_between_checks * 2
    pool.acquire()
    await pool._update_status_task
    pool.acquire()
    await pool._refresh_task

    async with pool.acquire() as conn:
        assert conn.fake_host == expected_host_after

    await pool.close(timeout=1.0)
