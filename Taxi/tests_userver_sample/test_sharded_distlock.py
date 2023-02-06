import pytest
from sharded_distlock.pytest_plugin import (  # pylint: disable=import-error
    ShardedDistLockError,
)


@pytest.fixture(name='sharded_distlock_sample')
def _sharded_distlock_sample(taxi_userver_sample, sharded_distlock_task):
    return sharded_distlock_task(
        taxi_userver_sample, 'sharded-distlock-sample',
    )


@pytest.fixture(name='run_shard_and_check_result')
def _run_shard_and_check_result(sharded_distlock_sample):
    async def _wrapper(shard):
        assert (await sharded_distlock_sample.run_shard(shard)) == {
            'name': 'sharded-distlock-sample',
            'shard': shard,
        }

    return _wrapper


async def test_basics(sharded_distlock_sample, run_shard_and_check_result):
    await sharded_distlock_sample.add_shard('default')

    await run_shard_and_check_result('default')


async def test_add_shard(sharded_distlock_sample, run_shard_and_check_result):
    await sharded_distlock_sample.add_shard('default')

    await run_shard_and_check_result('default')

    await sharded_distlock_sample.add_shard('new')

    await run_shard_and_check_result('new')


async def test_remove_shard(
        sharded_distlock_sample, run_shard_and_check_result,
):
    await sharded_distlock_sample.add_shards({'default', 'new'})

    await run_shard_and_check_result('default')
    await run_shard_and_check_result('new')

    await sharded_distlock_sample.remove_shard('default')

    with pytest.raises(
            ShardedDistLockError, match='shard default is not exist',
    ):
        await sharded_distlock_sample.run_shard('default')

    await run_shard_and_check_result('new')


async def test_disabling_shard(
        sharded_distlock_sample, run_shard_and_check_result,
):
    await sharded_distlock_sample.add_shards({'default', 'new'})

    await run_shard_and_check_result('default')

    await sharded_distlock_sample.disable_task()

    with pytest.raises(
            ShardedDistLockError, match='shard default is not exist',
    ):
        await sharded_distlock_sample.run_shard('default')
    with pytest.raises(ShardedDistLockError, match='shard new is not exist'):
        await sharded_distlock_sample.run_shard('new')

    await sharded_distlock_sample.enable_task()

    await run_shard_and_check_result('default')


async def test_disabling_by_host_shard(
        sharded_distlock_sample, run_shard_and_check_result,
):
    await sharded_distlock_sample.add_shard('default')

    impossible_regexp = 'my-magic-host'
    always_possible_regexp = r'[\d\D]+'

    await sharded_distlock_sample.update_shard(
        'default', {'hosts': always_possible_regexp},
    )

    await run_shard_and_check_result('default')

    await sharded_distlock_sample.update_shard(
        'default', {'hosts': impossible_regexp},
    )

    with pytest.raises(
            ShardedDistLockError, match='shard default is not exist',
    ):
        await sharded_distlock_sample.run_shard('default')
